# Edge-case library

Tối thiểu **8 card**, khuyến nghị 10–12. Một edge case tốt là case mà hai annotator hợp lý có thể làm khác nhau nếu
guideline chưa rõ. Tám ảnh dễ có label rõ ràng không được tính là edge-case library.

Cần có đủ độ đa dạng: occlusion / truncation / small-far · ambiguous semantics · conflicting road elements · **một case
critical-risk** · **một case guideline cho phép escalation**.

File này là kho nội bộ của nhóm, **không gửi cho peer**. Card dùng ảnh example/calibration thì chép rule + ví dụ sang
`02_guideline.md` (mục 7 và 9) để peer đọc được. Card về ảnh blind chỉ nằm ở đây, và decision của nó phải có trong
`gold_decisions.csv` trước `make freeze`.

Ảnh blind trong bộ 12: GTS18, BDD09, GTS17, GTS08, BDD21 (card EC02, EC03, EC08, EC09 — không chép sang guideline).

---

CASE ID: EC01
Sample: GTS23 (example)
Scene: Nút giao chữ T phía trước, xe đang tiến tới vạch dừng
Observation: Hai biển STOP bát giác, một ở đảo giao thông bên trái, một ở lề phải
Decision: LABEL
Expected: 2 box `priority / stop`, cả hai `relevance = ego`, `facing = front`; mỗi box ôm tight mặt bát giác, không ôm cột
Rationale: Critical cho downstream (xe phải dừng). Biển bên trái là biển lặp lại theo luật (Công ước Viên / StVO) nên vẫn áp dụng cho xe mình
Common mistake: Chỉ label biển bên phải, hoặc gán biển bên trái `not_ego` vì nó nằm bên trái
Diversity: critical

---

CASE ID: EC02
Sample: GTS17 (blind)
Scene: Lối vào khu mua sắm, hai cột biển hai bên
Observation: Trên mỗi cột: tấm tam giác xám (mặt sau biển nhường đường) ở trên, biển tròn đỏ vạch trắng ở dưới
Decision: LABEL + UNKNOWN
Expected: 2 box `prohibitory / no_entry`, `relevance = ego`; 2 box mặt sau `facing = back`, `sign_category = unknown`, `sign_type = unknown`, `relevance = not_ego`
Rationale: Cấm đi vào là critical. Mặt sau biển nhường đường áp dụng cho dòng xe ngược lại — gán `give_way` + `ego` sẽ báo sai quyền ưu tiên
Common mistake: Thấy tam giác đỉnh xuống rồi gán `priority / give_way` dù chỉ là mặt sau màu xám
Diversity: critical; conflict

---

CASE ID: EC03
Sample: GTS08 (blind)
Scene: Đường cao tốc lúc chạng vạng, ảnh nhoè chuyển động
Observation: Hai cặp biển tròn viền đỏ hai bên: số ba chữ số mờ (120) và biển cấm xe tải vượt
Decision: LABEL (ESCALATE nếu không đọc chắc số)
Expected: 4 box: 2 `prohibitory / speed_limit` với `value_text = 120` (hoặc `?` + `needs_review = true`), 2 `prohibitory / no_overtaking_trucks`; `readability = degraded`; `relevance = ego`
Rationale: Sai số tốc độ là critical. Guideline cấm đoán số: đọc không chắc thì `?` + escalate để downstream không dùng số sai
Common mistake: Ghi `20` hoặc `100` theo cảm giác; gộp biển tốc độ và biển xe tải vào một box
Diversity: low_visibility; critical; escalation

---

CASE ID: EC04
Sample: BDD06 (example)
Scene: Đường cao tốc Mỹ, trời âm u
Observation: Hai thoi vàng chữ đen END FREEWAY 1/2 MI ở dải phân cách trái và lề phải
Decision: LABEL
Expected: 2 box `danger_warning / other_warning`, `value_text = END FREEWAY 1/2 MI`, cả hai `ego`
Rationale: Thoi vàng ở Mỹ (MUTCD) là biển cảnh báo; ở Đức thoi vàng viền trắng là đường ưu tiên. Nhầm hệ thống làm sai nhóm ưu tiên
Common mistake: Gán `priority / priority_road` vì giống biển Đức
Diversity: conflict; ambiguity

---

CASE ID: EC05
Sample: GTS06 (example)
Scene: Đường đô thị Đức, biển trên cột lề phải
Observation: Biển 30 + tấm phụ mũi tên khoảng cách (chữ số nhoè) + tấm phụ giờ 7–18 h
Decision: LABEL
Expected: 3 box: `prohibitory / speed_limit` `30`; `supplementary_panel / panel_distance` `value_text = ?`; `supplementary_panel / panel_time` `7-18h`
Rationale: Biển phụ thay đổi phạm vi hiệu lực của biển chính; downstream cần box riêng để ghép điều kiện
Common mistake: Gộp 3 tấm thành một box; đoán khoảng cách là 300m
Diversity: small_far; ambiguity

---

CASE ID: EC06
Sample: BDD01 (calibration)
Scene: Cao tốc Mỹ, giá long môn phía trên
Observation: Ba bảng liền nhau trên giá (2 bảng xanh có tab EXIT, 1 bảng vàng mũi tên 10); phản chiếu các bảng trên capô
Decision: LABEL + IGNORE
Expected: 3 box `mount = overhead` (bảng có khung riêng → box riêng; tab EXIT dính liền → cùng box); phản chiếu trên capô: không vẽ
Rationale: Bảng là đơn vị vật lý; phản chiếu không phải biển thật, label vào sẽ tạo false positive cho detector
Common mistake: Một box cho cả giá; vẽ thêm box ở phản chiếu trên capô
Diversity: conflict; occlusion

---

CASE ID: EC07
Sample: GTS05 (calibration)
Scene: Góc phố Đức, nhiều cột biển
Observation: Mặt sau tấm tam giác và tấm tròn; một mẩu biển xanh bị mép phải ảnh cắt (rộng ~10 px)
Decision: UNKNOWN + ESCALATE
Expected: Mặt sau: `facing = back`, `unknown / unknown`, `not_ego`. Mẩu biển ở mép: `unknown / unknown`, `truncated = true`, `readability = illegible`, `needs_review = true`
Rationale: Không đủ bằng chứng để phân loại; escalate thay vì đoán, reviewer quyết định có giữ box không
Common mistake: Bỏ qua mẩu biển ở mép, hoặc gán loại biển theo hình dạng mặt sau
Diversity: occlusion; escalation

---

CASE ID: EC08
Sample: BDD21 (blind)
Scene: Đường ven sông Mỹ, khúc cua trái
Observation: Bảng vàng mũi tên đen hình chevron trên cột lề phải
Decision: LABEL
Expected: 1 box `danger_warning / chevron_alignment`, `ego`; đèn giao thông trong ảnh không vẽ
Rationale: MUTCD W1-8 là biển cảnh báo; StVO xếp bảng chevron (Z. 625) vào thiết bị giao thông — guideline chọn label thống nhất vì cùng chức năng
Common mistake: Coi chevron là thiết bị an toàn (như tấm sọc Leitbake) và bỏ qua
Diversity: ambiguity

---

CASE ID: EC09
Sample: GTS17 (blind)
Scene: Lối vào khu mua sắm
Observation: Tấm trắng viền đỏ chữ "Süd" trên cột bên phải — không rõ biển chính thức hay biển khu tư nhân
Decision: ESCALATE
Expected: 1 box `informative / other_informative`, `relevance = unclear`, `needs_review = true`
Rationale: Guideline mục 7(a): không chắc là biển chính thức thì vẫn vẽ + escalate để reviewer quyết
Common mistake: Bỏ qua hoàn toàn, hoặc gán như biển chỉ hướng chính thức không escalate
Diversity: escalation; ambiguity

---

CASE ID: EC10
Sample: BDD04 (calibration)
Scene: Phố Mỹ, biển xa 12–25 px
Observation: Thoi vàng mũi tên rẽ + tấm vàng "15" bên dưới; biển tròn vàng nhỏ; biển trắng chữ đỏ
Decision: LABEL
Expected: Thoi: `danger_warning / curve`; tấm 15: `supplementary_panel / panel_text_other` `15`; biển không đọc được ký hiệu: `other_<nhóm>` + `readability = illegible`
Rationale: Biển 10–19 px vẫn là dữ liệu cần cho detector; chọn nhóm theo màu/hình, không đoán loại
Common mistake: Bỏ qua vì nhỏ; hoặc đoán loại cụ thể khi không thấy ký hiệu
Diversity: small_far

---

CASE ID: EC11
Sample: BDD05 (calibration)
Scene: Đường Mỹ nhiều làn, biển bên kia đường
Observation: Biển nâu/trắng nhỏ ở lề đối diện và hai bảng lớn thấy mặt sau xám
Decision: UNKNOWN
Expected: Biển nhỏ: `informative` / `prohibitory` với `other_*`, `relevance = unclear`, `illegible`; bảng mặt sau: `facing = back`, `unknown`, `not_ego`
Rationale: Một ảnh không đủ biết biển thuộc đường nào → `unclear` trung thực tốt hơn `ego` đoán
Common mistake: Gán `ego` cho mọi biển nhìn thấy mặt trước
Diversity: small_far; occlusion

---

CASE ID: EC12
Sample: GTS05 (calibration)
Scene: Góc phố Đức, xe đang rẽ
Observation: Biển 30 ở vỉa hè đường cắt ngang, quay mặt về phía xe
Decision: LABEL + ESCALATE
Expected: `prohibitory / speed_limit` `30`, `relevance = unclear`, `needs_review = true`
Rationale: Guideline 4.4: `unclear` + `speed_limit` là critical → bắt buộc escalate để reviewer xác nhận làn áp dụng
Common mistake: Gán `ego` và bỏ qua escalate
Diversity: critical; escalation

---
