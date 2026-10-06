"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .tasks import ROOT, eval_markers   # có sẵn: eval_markers tính lúc chạy từ tasks/*-eval/

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    if out_dir is None:
        out_dir = ROOT / "skills" / "auto"
    out_dir = Path(out_dir)

    # Đọc các lần chạy của tác vụ học
    runs = []
    results_path = Path(results_dir)
    if not results_path.exists():
        print("WARNING: results directory not found")
        return []

    for task_dir in sorted((results_path / source_condition).iterdir()):
        if not task_dir.is_dir():
            continue
        run_json = task_dir / "run.json"
        trace_md = task_dir / "trace.md"

        if not run_json.exists():
            continue

        r = json.loads(run_json.read_text(encoding="utf-8"))

        # Chỉ dùng tác vụ học
        if r.get("role") != "learn":
            continue

        # Đọc trace (chỉ lấy 6000 ký tự cuối)
        trace = ""
        if trace_md.exists():
            trace = trace_md.read_text(encoding="utf-8")[-6000:]

        # Lấy các check thất bại
        failed = []
        for check in r.get("checks", []):
            if not check.get("passed", True):
                failed.append((check.get("name", ""), check.get("detail", "")))

        runs.append({
            "task": r.get("task", task_dir.name),
            "failed": failed,
            "trace": trace,
        })

    # Kiểm tra có check thất bại không
    has_any_failure = any(run["failed"] for run in runs)
    if not has_any_failure:
        print("WARNING: no failed checks found in learning tasks")
        return []

    # Tạo prompt
    from .model import make_model
    if model is None:
        model = make_model()

    prompt_parts = [
        "You are writing SKILLs for a programming and data analysis agent.",
        "Below are failed checks (name and bot feedback) and traces from learning task runs.",
        f"Write at most {max_skills} short skills to help avoid these errors on NEW tasks of the same type.",
        "",
        "Rules:",
        "- Skills must be general: do not mention task IDs, specific filenames, answers, or numbers.",
        "- Each skill has YAML frontmatter with `name` (lowercase, hyphens) and `description` (one sentence: WHEN TO USE),",
        "  then at most 40 lines of imperative checklist-style instructions.",
        "- Output format, exact characters:",
        "```",
        "=== SKILL: <name> ===",
        "---",
        "name: <name>",
        "description: <when to use>",
        "---",
        "<content>",
        "=== END ===",
        "```",
        "",
    ]

    for run in runs:
        prompt_parts.append(f"## Task: {run['task']}")
        if run["failed"]:
            prompt_parts.append("Failed checks:")
            for name, detail in run["failed"]:
                prompt_parts.append(f"  - {name}: {detail}")
        if run["trace"]:
            prompt_parts.append(f"Trace (last 6000 chars):")
            prompt_parts.append(run["trace"])
        prompt_parts.append("")

    prompt = "\n".join(prompt_parts)

    # Gọi model
    reply = model.invoke(prompt)
    content = reply.content if hasattr(reply, "content") else str(reply)

    # Phân tích và ghi skill
    written = []
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, text in parse_skill_blocks(content):
        if len(written) >= max_skills:
            break

        problems = validate_skill(text, expected_name=name)
        if problems:
            print(f"SKIP skill '{name}': {problems}")
            continue

        skill_dir = out_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(text, encoding="utf-8")
        written.append(skill_file)
        print(f"wrote {skill_file}")

    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
