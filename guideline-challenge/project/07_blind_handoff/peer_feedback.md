# Peer feedback + owner response

Phần 1 do **nhóm peer** trả lời (gửi kèm file export). Phần 2 do **nhóm owner** điền.

- **Nhóm peer:** Nhóm 6
- **Người label blind:** Nhóm 6 (tài khoản CVAT `iwillwin2211@gmail.com`, job 26). Nhóm 6 label cả 12 ảnh trao đổi,
  export `peer.zip`. Bản đầy đủ lưu ở `peer_output/peer_nhom6_full12.zip`; bản lọc 5 ảnh blind dùng để chấm là
  `peer_output/peer_nhom6_blind.zip`.
- **Clarification log:** nhóm 6 không gửi câu hỏi nào trong blind window, nên `clarification_log.csv` không có dòng
  nào (I = 100).

## 1. Peer trả lời

1. Rule nào rõ nhất / giúp quyết định nhanh nhất? Rule dài nhưng rất chi tiết và phù hợp với dữ liệu cần label.
   Attribute tuy nhiều nhưng được mô tả chi tiết và đầy đủ.
2. Rule nào mơ hồ hoặc phải tự suy diễn? Một số attribute bị nhầm lúc đầu vì chưa nắm rõ hết ý nghĩa (11 attribute
   cho mỗi box).
3. Sample nào khiến guideline "vỡ"? Các biển ở xa: không đoán được đó là biển gì.
4. Attribute / default nào trong CVAT dễ gây thao tác sai? Danh sách attribute dài, dễ bỏ sót hoặc nhầm khi điền
   lần lượt từng box.
5. Một thay đổi cụ thể giúp annotator mới ít hỏi hơn? Nhóm 6 không nêu đề xuất cụ thể. Owner rút ra từ câu 2–4: cần
   bảng quyết định cho biển xa và thứ tự điền attribute ngắn gọn.

## 2. Owner phân loại

Kết quả chấm: 14/14 gold decision đúng, GTS = 100 (`gts_summary.md`). Đối chiếu cả 12 ảnh bằng
`check_peer_accuracy.py`: 53/53 box ghép được, F1 100%, mọi attribute đúng 100%, 0 critical escape, quality gate PASS
(chạy lại: `python project/check_peer_accuracy.py project/07_blind_handoff/peer_output/peer_nhom6_full12.zip`).

**Lưu ý khi debrief:** 51/53 box của nhóm 6 trùng tọa độ với ground truth tới 0,1 px, và toàn bộ 11 attribute đều
trùng; 2 box còn lại (BDD06, GTS23) chỉ lệch 8–12 px. Export cũng không có attribute nào sai, trong khi nhóm 6 kể là
có nhầm vài attribute (có thể đã tự sửa trước khi export). Mức trùng này hiếm gặp giữa hai nhóm label độc lập, nên cần
xác nhận lại với nhóm 6 trong debrief rằng ground truth không bị lộ. GTS 100 chỉ nên coi là cận trên của độ chuyển
giao, không phải bằng chứng chắc chắn.

| Feedback / decision sai | Nguyên nhân (guideline gap / data ambiguity / execution error) | Xử lý (accept + revise / reject with evidence / add escalation rule) | Bằng chứng |
|---|---|---|---|
| Biển ở xa không đoán được là biển gì (câu 3) | guideline gap — mục 6 có nói biển 10–19 px chọn nhóm theo hình/màu nhưng chưa có bước quyết định rõ | accept + revise: v3 thêm bảng quyết định theo kích thước và mức đọc được (mục 6) | Feedback nhóm 6; biển nhỏ ở BDD04, BDD05, GTS08 (box `unknown` illegible) |
| Nhầm một số attribute vì chưa nắm rõ (câu 2) | guideline gap — 11 attribute nằm rải rác ở 4.3, 4.4, 5, 6 | accept + revise: v3 thêm mục 4.5 "Thứ tự điền attribute" (checklist 1 bảng) | Feedback nhóm 6; export cuối không còn lỗi attribute → lỗi chủ yếu ở lúc học rule |
| Attribute dài, dễ thao tác sai (câu 4) | guideline gap (usability) | accept + revise: checklist 4.5 ghi rõ attribute nào thường giữ default, chỉ đổi khi có dấu hiệu cụ thể | Feedback nhóm 6 |
| Rule dài nhưng chi tiết, hợp dữ liệu (câu 1) | — (phản hồi tích cực) | reject with evidence: giữ nguyên cấu trúc, không rút gọn rule | 14/14 gold decision đúng, 0 câu hỏi trong blind window |
| Decision sai | Không có decision nào sai (14/14) | — | `transfer_score.csv` |
