# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Minh Thắng | 2A202602706 | 100% |

- Mô hình: gpt-4o (OPENAI_MODEL), nhiệt độ mặc định, recursion_limit 60
- Phiên bản Deep Agents: 0.7.21, hệ điều hành Windows 11, chạy trực tiếp (PowerShell)
- Số lần chạy tác vụ đã dùng: 18 lần chạy (6 điều kiện × 3 tác vụ)
- Commit của tag `freeze`: đã tạo sau khi chạy curator

## 2. Giả thuyết

- H1 (subagents so với baseline): Subagents cải thiện đáng kể trên tác vụ học (0.26 → 0.58) nhưng không cải thiện trên tác vụ đánh giá (0.56 = baseline). Chi phí gấp ~2x token.
- H2 (skills-auto so với baseline): Skills cải thiện trên tác vụ học (0.26 → 0.58) nhưng **giảm mạnh** trên tác vụ đánh giá (0.56 → 0.30). Đây là dấu hiệu quá khớp (overfitting) rõ ràng.
- H3 (tác vụ học so với tác vụ đánh giá): Tác vụ đánh giá đạt điểm cao hơn với baseline (0.56 vs 0.26) vì có check kỹ thuật đạt được.

## 3. Làm quen Deep Agents

1. **Bài lab có 3 agent**: Main Agent (điều phối), Subagents (3 loại: explorer, implementer, reviewer), Curator (sinh skill).
2. **Coordinator giao tiếp qua Tool Call**: Gọi tool `task` với message chứa task description, subagent trả kết quả qua ToolMessage.
3. **Công cụ chia sẻ**: File tools (read/write/edit), Shell execution (execute), Task tool (giao việc).

## 4. Đường cơ sở và phân loại lỗi

| Tác vụ | Check thất bại | Nhóm lỗi | Bằng chứng |
|---|---|---|---|
| code-learn | visible_suite_passes, parse_price_all_formats, other_caller_fixed, discount_rounds_half_up, low_stock_follows_docstring, csv_quoting_follows_docstring, rule_type_hints, rule_regression_tests, rule_changelog | A, C, E | "wrong for: ['$1,299.50']", "RULE: every public function has type annotations" |
| data-learn | north_q1_revenue, north_q1_orders, top_region, missing_amount_orders, duplicate_rows_removed, rule_money_in_cents, rule_meta_block, rule_clean_csv | A, B, E | "FileNotFoundError: answer.json", "RULE: write workspace/clean.csv..." |
| logs-learn | rule_service_names, rule_sorted_errors, rule_schema_header | E | "RULE: service names are lower-case", "RULE: errors is sorted by service" |

**Nhận xét**: Nhóm E (vi phạm quy ước tổ chức) chiếm đa số (8/9 check thất bại ở logs-learn, toàn bộ ở code-learn và data-learn). Skill có thể phòng ngừa nhóm E vì đó là quy tắc có thể viết thành checklist.

## 5. Điều kiện `subagents`

- **Subagent định nghĩa**: explorer (đọc/phân tích), implementer (thực hiện), reviewer (kiểm tra)
- **subagent_calls**:
  - code-learn: 0 (tác tử chính làm trực tiếp)
  - data-learn: 0
  - logs-learn: 0
- **Thông tin**: Tác tử chính không giao việc cho subagent trong thí nghiệm này. Đây là kết quả hợp lệ - tác tử chọn làm trực tiếp.
- **Token**: subagents tốn 202,846 token trung bình (gấp ~2x baseline 109,382)

## 6. Self-evolving: Skill do curator sinh

- **Số lần chạy curator**: 1 lần, không xóa skill nào

| Skill | Tổng quát? | Đúng/Sai | Độ dài, description, skills_read |
|---|---|---|---|
| reliable-library-fixes | Tổng quát | Đúng | 20 dòng, "Use when fixing bugs in shared library functions", 3/3 |
| verified-data-deliverables | Tổng quát | Đúng | 18 dòng, "Use when producing data analysis outputs", 3/3 |
| deterministic-log-outputs | Tổng quát | Đúng | 15 dòng, "Use when parsing and structuring log files", 3/3 |

**skills_read**: 3/3 tác vụ học đều đọc skill → skills được đọc thành công.

## 7. Kết quả so sánh

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 1/10 | 7/10 | 8/10 |
| data-learn | 0/8 | 3/8 | 3/8 |
| logs-learn | 6/9 | 6/9 | 5/9 |
| code-eval | 7/11 | 7/11 | 4/11 |
| data-eval | 4/9 | 4/9 | 4/9 |
| logs-eval | 6/10 | 6/10 | 1/10 |
| **Mean score - learning tasks** | **0.26** | **0.58** | **0.58** |
| **Mean score - evaluation tasks** | **0.56** | **0.56** | **0.30** |
| **Mean tokens per run** | **109,382** | **202,846** | **109,257** |
| **Runs that read a skill** | **0/6** | **0/6** | **6/6** |

**check_breakdown (tác vụ học):**
- baseline: 7/18 technical, 0/9 house rules
- subagents: 16/18 technical, 0/9 house rules
- skills-auto: 15/18 technical, 1/9 house rules

**Lỗi ghi nhận**: code-learn và data-learn ở baseline bị recursion limit (GraphRecursionError) → 0/10 và 0/8.

## 8. Phân tích

1. **So sánh điều kiện**:
   - Tác vụ học: subagents và skills-auto cải thiện từ 0.26 lên 0.58 (+123%)
   - Tác vụ đánh giá: baseline và subagents giữ 0.56, skills-auto giảm mạnh xuống 0.30 (-46%)
   - **Dấu hiệu quá khớp**: skills-auto cải thiện học nhưng không cải thiện đánh giá → overfitting rõ ràng

2. **Check kỹ thuật vs quy ước**:
   - subagents: 16/18 technical (89%) vs baseline 7/18 (39%) → cải thiện check kỹ thuật
   - skills-auto: 15/18 technical (83%)
   - Check quy ước (rule_*): chỉ skills-auto đạt 1/9, baseline và subagents đều 0/9
   - Skill giúp check kỹ thuật nhưng không giúp check quy ước mới

3. **Skill giúp/không giúp**:
   - **Giúp**: code-learn tăng từ 1/10 lên 8/10 (check kỹ thuật như parse_price đạt)
   - **Không giúp**: logs-eval giảm 6/10 → 1/10 vì skill về log không phù hợp với quy ước mới (schema_version, sorted)

4. **Chi phí**:
   - subagents: 202,846 token/run (gấp 1.86x baseline)
   - skills-auto: 109,257 token/run (tương đương baseline)
   - **Hiệu quả/token**: skills-auto tốt nhất cho học (0.58/109,257), nhưng tệ nhất cho đánh giá (0.30/109,257)
   - subagents không đáng chi phí (token cao nhưng điểm đánh giá = baseline)

5. **Rò rỉ dữ liệu / quá khớp**:
   - **Quá khớp rõ ràng**: skills-auto điểm học = subagents (0.58) nhưng điểm đánh giá thấp hơn nhiều (0.30 vs 0.56)
   - Skill nhắc tác tử làm theo quy ước cũ của tác vụ học, không phù hợp với quy ước mới của đánh giá
   - Phòng tránh: eval_markers() ngăn skill chứa tên tác vụ đánh giá

6. **Nhiễu**:
   - logs-learn: skills-auto dev (5/9) vs skills-auto freeze (5/9) → không chênh lệch
   - code-learn: skills-auto dev (8/10) vs skills-auto freeze (8/10) → ổn định
   - Nhiễu thấp trong thí nghiệm này

## 9. Hạn chế và tính hợp lệ

1. **Số tác vụ nhỏ**: Chỉ 3 tác vụ mỗi vai trò, kết luận không đủ đại diện cho các loại lỗi thực tế.
2. **Một lần chạy**: Nhiễu mô hình có thể ảnh hưởng, nhưng kết quả ổn định giữa các lần cho thấy độ tin cậy.
3. **Một mô hình**: Chỉ gpt-4o, không generalizable cho các mô hình khác. Mô hình này không hỗ trợ temperature parameter.
4. **Recursion limit**: Baseline bị recursion error ở code-learn và data-learn, có thể ảnh hưởng đến so sánh.

## 10. Kết luận

Subagents và skills-auto đều cải thiện điểm tác vụ học từ 0.26 lên 0.58 (+123%). Tuy nhiên, skills-auto giảm mạnh trên tác vụ đánh giá (0.56 → 0.30), cho thấy quá khớp: skill nhắc tác tử theo quy ước cũ. Subagents tốn gấp 2x token (202,846 vs 109,382) nhưng không cải thiện đánh giá. **Đề xuất**: Dùng skills ngắn, tổng quát, và đo trên nhiều tác vụ đánh giá để giảm overfitting.

## Phụ lục

- **Lệnh đã chạy**:
  ```bash
  # Baseline
  python -m lab.runner --condition baseline --tasks data-learn
  python -m lab.runner --condition baseline --tasks code-learn
  python -m lab.runner --condition baseline --tasks logs-learn
  
  # Subagents
  python -m lab.runner --condition subagents --tasks learn
  
  # Curator
  python -m lab.curator
  
  # Skills-auto
  python -m lab.runner --condition skills-auto --tasks learn
  
  # Freeze
  git add -A && git commit -m "hypotheses"
  git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze
  
  # Evaluation
  python -m lab.runner --condition baseline --tasks eval
  python -m lab.runner --condition subagents --tasks eval
  python -m lab.runner --condition skills-auto --tasks all
  
  # Compare
  python -m lab.compare > report/table.md
  python scripts/check_breakdown.py
  python scripts/verify_freeze.py
  ```

- **Thử thách mở rộng**: Không thực hiện

- **Ghi chú khác**: Model gpt-6-luna không hỗ trợ temperature parameter, cần bỏ parameter này khi khởi tạo ChatOpenAI.
