# Problem statement + downstream contract

## Bài toán

Phát hiện và phân loại **biển báo giao thông theo nhóm chức năng pháp lý** (Công ước Viên / StVO / MUTCD / QCVN 41)
trên ảnh dashcam Đức (GTSDB) và Mỹ (BDD100K), khó ở chỗ biển **nhỏ / xa / bị che / nhìn từ mặt sau**, và cùng một
hình dạng mang nghĩa khác nhau giữa hai hệ thống (thoi vàng: Đức = đường ưu tiên, Mỹ = cảnh báo).

## Downstream contract

1. **Downstream task / model / user là ai?** Module nhận diện biển báo cho ADAS và cập nhật bản đồ: detector phát
   hiện biển → classifier 2 tầng (`sign_category` → `sign_type`) → logic hành vi xe dùng biển có `relevance = ego`.
2. **Output annotation nào thực sự cần?** Rectangle tight box mặt biển (`traffic_sign`); attribute `sign_category`,
   `sign_type`, `value_text` (số tốc độ…), `relevance`; attribute phụ để lọc hard example: `facing`, `occlusion`,
   `readability`, `truncated`, `mount`, `temporary`; `needs_review` cho escalation.
3. **Failure nào gây hậu quả lớn nhất?** Sót hoặc sai biển điều khiển trực tiếp xe mình: STOP, nhường đường, cấm đi
   vào, giới hạn tốc độ (kể cả sai con số), và gán `relevance = ego` sai cho các biển này. Đây là decision `critical`.
4. **Khi ambiguity không resolve được, ai / ở đâu là escalation path?** Annotator vẫn vẽ box, điền lựa chọn tốt nhất
   và bật `needs_review = true`; QA owner xem 100% object `needs_review` trong vòng review, quyết định cuối thành
   rule / ví dụ mới ở version guideline sau.

## Scope

- **Trong scope (bắt buộc label):** mọi biển báo chính thức có cạnh ngắn ≥ 10 px: cảnh báo, ưu tiên, cấm/hạn chế,
  hiệu lệnh, chỉ dẫn (kể cả biển chỉ hướng, biển tên đường, biển số đường, bảng giá long môn), biển phụ, biển tạm,
  bảng chevron vòng cua, biển nhìn từ mặt sau/cạnh (`facing = back/edge_on`).
- **Ngoài scope (ignore):** đèn giao thông, vạch sơn, cọc tiêu / tấm sọc Leitbake / rào / nón, biển quảng cáo và
  cửa hàng, tranh tường giống biển, biển trên xe, sticker trên kính, phản chiếu của biển, biển < 10 px, biển bị che
  > 90%.
- **Geometry tolerance:** tight box phần mặt biển nhìn thấy (không ôm cột); mỗi cạnh lệch ≤ 2 px (≤ 1 px với biển có
  cạnh ngắn < 30 px). Khi chấm peer: ghép box bằng IoU ≥ 0.5, rồi kiểm tolerance cạnh.

## Output chấm được

Blind test chấm: LABEL (có box đúng số lượng), IGNORE (không vẽ biển thương mại / đèn / mặt sau thành biển thường),
UNKNOWN (`sign_category = unknown` cho mặt sau / không xác định), ESCALATE (`needs_review = true`), class 2 tầng,
`value_text`, `relevance`, `facing`, và geometry theo tolerance. Tất cả nằm trong export CVAT for images 1.1 và được
chấm tự động bằng `project/check_peer_accuracy.py` + `gold_decisions.csv`.

## Dữ liệu và giới hạn

12 ảnh trao đổi trong `project/dataraw/traffic_sign_gt/`: 6 GTSDB (Đức) + 6 BDD100K (Mỹ); chia 3 example /
4 calibration / 5 blind trong `sample_pack.csv`. Giới hạn: ít ảnh ban đêm; không có ảnh Việt Nam (QCVN 41 chỉ để đối
chiếu nhóm chức năng); nhiều biển 10–20 px nên `sign_type` thường phải là `other_<nhóm>`; relevance chỉ suy từ một
ảnh tĩnh nên có nhiều `unclear`.
