# Revision log

Guideline v1 = bản nháp đầu; v2 = sau calibration nội bộ; v3 = sau blind handoff. Mỗi lần tăng `Version` trong
`02_guideline.md`, thêm một hoặc nhiều dòng vào bảng: đổi gì và vì sao, kèm bằng chứng (sample_id, dòng
calibration report, câu hỏi trong clarification log, feedback của peer).

Cột Version ghi dạng `v1`, `v2`, `v3` — `make status` tìm dòng bảng có `v2` và dòng có `v3`.

| Version | Đổi gì | Vì sao | Bằng chứng |
|---|---|---|---|
| v1 | Bản nháp đầu: taxonomy 2 tầng `sign_category` → `sign_type` theo Công ước Viên / StVO / MUTCD / QCVN 41; attribute value_text, relevance, facing, occlusion, readability, truncated, mount, temporary, needs_review | Topic lock: hierarchical sign taxonomy cho biển nhỏ/xa/bị che | Xem ảnh GTS01–28, BDD01–26; ví dụ GTS06, GTS23, GTS16, BDD06, GTS28 |
| v2 | Bỏ cột QCVN ở bảng 4.1; viết lại cột ghi chú bảng 4.2 bằng mô tả hình dạng thay cho mã luật; thêm mục 9.2 "Ảnh ví dụ đã label" (7 ảnh example + calibration, box tô màu theo `sign_category`, ảnh phóng to, bảng từng box, khung IGNORE cho biển quán và phản chiếu trên capô); xuất bản PDF | Calibration: các case khó (BDD01 bảng vàng số 10, GTS05 biển 30 `unclear`, GTS05 mẩu biển bị cắt) cần ví dụ nhìn thấy được thay vì chỉ mô tả bằng chữ; mã luật trong ghi chú khó đọc với annotator mới | `06_calibration_report.csv` dòng BDD01, GTS05 ×2; `assets/examples/` |
| v3 | Thêm mục 4.5 "Thứ tự điền attribute" (checklist 11 bước, ghi rõ khi nào đổi khỏi default); thêm bảng quyết định cho biển nhỏ/xa ở mục 6 (theo kích thước và mức đọc được → `sign_category` / `sign_type` / `readability`) | Blind test: nhóm 6 phản hồi 11 attribute dài, nhầm vài attribute lúc đầu, và biển ở xa không đoán được là biển gì. Kết quả chấm 14/14 đúng (GTS 100) nên không đổi rule nào đang chạy, chỉ bổ sung công cụ giúp áp dụng nhanh hơn | `07_blind_handoff/peer_feedback.md` câu 2–4; `transfer_score.csv`; `06_calibration_report.csv` dòng BDD04 |
