# QA plan + quality gates

Không được viết "reviewer kiểm tra lại". Phải có sampling, metric, threshold và action khi fail.

## Flow

Guideline → Calibration → Production → Self-QC → Review → Rework → Quality Gate. Cụ thể cho project:

- **Ai review, review bao nhiêu:** QA owner review. Mỗi batch: 100% object có `needs_review = true`; 100% object có
  `sign_type` critical (`stop`, `give_way`, `no_entry`, `speed_limit`); 100% ảnh có tag `critical` trong
  `sample_pack.csv`; và 20% ảnh còn lại chọn ngẫu nhiên (tối thiểu 2 ảnh). Annotator mới: 100% ảnh ở batch đầu.
- **Chọn sample theo rule nào:** theo rủi ro trước (critical, `needs_review`, biển 10–19 px, `readability != clear`,
  `relevance = unclear`), rồi random phần còn lại. Self-QC trước khi nộp: chế độ Attribute annotation đi qua từng
  object, không còn `__undefined__`.
- **Issue được ghi ở đâu, đóng thế nào:** mỗi lỗi một dòng trong `matches.csv` (do `check_peer_accuracy.py` sinh) hoặc
  comment trên object CVAT, kèm severity. Annotator sửa → reviewer chạy lại script → issue đóng khi dòng đó thành `TP`
  không còn `wrong_attributes` / `ESCAPE`.
- **Khi phát hiện guideline gap thì update và version ra sao:** gap được phân loại (guideline gap / data ambiguity /
  execution error). Guideline gap → sửa rule hoặc thêm ví dụ trong `02_guideline.md`, tăng version (v2 sau
  calibration, v3 sau blind), ghi `08_revision_log.md`, dán lại Guide trong task CVAT. Execution error → coaching,
  không đổi version.

## Defect severity

| Severity | Định nghĩa cho project này | Ví dụ | Action mặc định |
|---|---|---|---|
| Critical | Sai / sót biển điều khiển trực tiếp xe mình (`stop`, `give_way`, `no_entry`, `speed_limit`): sót box, sai `sign_type`, sai `relevance`, sai số tốc độ | Ghi 20 thay vì 120 (GTS08); gán mặt sau biển nhường đường thành `give_way` + `ego` (GTS17) | Batch REJECT; sửa ngay; kiểm lại 100% biển critical của annotator đó |
| Major | Sai nhóm/loại biển không critical, sót/thừa biển ≥ 10 px, label biển ngoài scope, sai `facing`, thiếu escalate khi guideline bắt buộc | Thoi vàng Mỹ gán `priority_road`; vẽ phản chiếu trên capô; không bật `needs_review` cho biển Süd | Rework trong batch; ghi vào revision log nếu lặp ≥ 2 lần |
| Minor | Geometry ngoài tolerance nhưng IoU ≥ 0.5; sai attribute phụ (`occlusion`, `readability`, `mount`, `temporary`, `truncated`) | Box lệch 3 px; `readability = clear` cho biển nhoè | Sửa khi review, không chặn batch |
| Question | Annotator không chắc rule áp dụng thế nào | "Biển trên cột đèn giao thông có phải `overhead`?" | Ghi clarification, trả lời bằng rule mới trong guideline (không trả lời miệng) |

## Metrics

Tất cả tính tự động bằng `python project/check_peer_accuracy.py <export>.zip` so với
`cvat_annotations/ground_truth_12/`.

| Metric | Cách tính | Vì sao phù hợp với bài toán |
|---|---|---|
| Detection F1 | Ghép box IoU ≥ 0.5 (greedy); F1 = 2PR/(P+R) | Detector downstream cần cả không sót (recall) lẫn không thừa (precision) |
| Category accuracy | `sign_category` đúng / box đã ghép | Tầng 1 là thứ ADAS dùng đầu tiên (cảnh báo / cấm / ưu tiên…) |
| Type accuracy | `sign_type` đúng / box đã ghép | Tầng 2 cho logic cụ thể (dừng, tốc độ…) |
| End-to-end | box ghép đúng + đúng `sign_type` / (GT + FP) | Một con số gộp detection + classification |
| Geometry compliance | box đạt tolerance mục 3 (≤ 2 px/cạnh, ≤ 1 px nếu biển < 30 px) / box đã ghép; kèm IoU trung bình | Kiểm geometry theo rule đã viết, không theo cảm giác |
| Attribute accuracy | từng attribute đúng / box đã ghép | Chỉ ra attribute nào guideline mô tả chưa rõ |
| `__undefined__` count | số attribute bắt buộc chưa chọn | Default `__undefined__` còn trong export = object chưa xong |

Metric high-risk tách riêng: **critical escape** = số biển critical trong ground truth bị sót hoặc sai `sign_type` /
`relevance` / số tốc độ (`?` + `needs_review` được chấp nhận vì là escalate hợp lệ). Mục tiêu = 0.

## Quality gate

```text
PASS if:
  critical escape = 0
  AND không thiếu ảnh nào trong export
  AND F1 >= 0.85 AND category accuracy >= 0.90 AND type accuracy >= 0.80
  AND geometry compliance >= 0.85 AND __undefined__ = 0
REWORK if: critical escape = 0 và F1 >= 0.60 nhưng trượt ít nhất một ngưỡng PASS
REJECT / ESCALATE if: critical escape >= 1, hoặc thiếu ảnh, hoặc F1 < 0.60
```

Trade-off: một biển critical sai có thể khiến xe vượt STOP hoặc chạy sai tốc độ, nên critical escape chặn cứng dù
các metric khác cao. Type accuracy đặt 0.80 (thấp hơn category 0.90) vì nhiều biển 10–20 px chỉ xác định được nhóm —
guideline cho phép `other_<nhóm>`, đòi cao hơn sẽ ép annotator đoán. Geometry 0.85 chứ không 1.0 vì tolerance 1–2 px
trên biển nhỏ khó đạt tuyệt đối mà ảnh hưởng downstream nhỏ (lỗi geometry là minor). `relevance` chỉ vào gate qua
critical escape, vì nhiều biển `unclear` là ambiguity thật của ảnh tĩnh.
