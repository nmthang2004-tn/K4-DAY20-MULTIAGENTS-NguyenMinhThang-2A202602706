"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Dùng khi cần đọc và phân tích file, README, docstring, mẫu dữ liệu, hoặc báo cáo sự thật từ workspace mà không cần sửa gì.",
            "system_prompt": "Bạn là một chuyên gia đọc và phân tích file. Nhiệm vụ của bạn: đọc kỹ các file trong workspace, trích xuất thông tin quan trọng và báo cáo lại bằng tiếng Việt. Không sửa hay tạo file nào. Trả về báo cáo ngắn gọn, có cấu trúc."
        },
        {
            "name": "implementer",
            "description": "Dùng khi cần thực hiện thay đổi code, tạo file mới, chạy test hoặc script, và báo cáo kết quả thực thi.",
            "system_prompt": "Bạn là một lập trình viên thực hiện. Nhiệm vụ của bạn: thực hiện các thay đổi theo yêu cầu, tạo hoặc sửa file, chạy test hoặc script, và báo cáo kết quả. Khi xong, chạy lại test để xác nhận."
        },
        {
            "name": "reviewer",
            "description": "Dùng khi cần kiểm tra độc lập kết quả, đối chiếu với đề bài, hoặc xác nhận các trường hợp biên.",
            "system_prompt": "Bạn là một người kiểm tra độc lập. Nhiệm vụ của bạn: đọc đề bài, đối chiếu với kết quả thực tế trong workspace, và báo cáo xem có đạt yêu cầu không. Không sửa gì, chỉ kiểm tra và báo cáo."
        },
    ]
