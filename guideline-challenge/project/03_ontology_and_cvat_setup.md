# Ontology + CVAT setup

Bảng ontology là **source of truth** cho schema CVAT: `03_cvat_labels.json` phải khớp từng dòng ở đây. Thay mọi
placeholder mới là xong (gate G2).

## Ontology table

| Name | Geometry | Type (class / attribute) | Allowed values | Default | Mutable? | Rationale |
|---|---|---|---|---|---|---|
| `traffic_sign` | rectangle (Shape) | class | — | — | — | Mọi biển báo chính thức có cùng geometry rule (tight box mặt biển nhìn thấy) và cùng QA rule |
| `sign_category` | — | attribute của `traffic_sign` | `__undefined__`, `priority`, `prohibitory`, `mandatory`, `danger_warning`, `informative`, `supplementary_panel`, `unknown` | `__undefined__` | không | Tầng 1 theo nhóm chức năng Công ước Viên (A–H) / QCVN 41 (P/R/W/I/S); `priority` tách riêng vì là nhóm critical |
| `sign_type` | — | attribute | 55 giá trị theo bảng 4.2 guideline (`stop` … `panel_text_other`, `unknown`) | `__undefined__` | không | Tầng 2; phải thuộc đúng nhóm của `sign_category` |
| `value_text` | — | attribute (text) | chữ tự do; `-` = không có số/chữ; `?` = không đọc được | `-` | không | Số tốc độ/tải trọng/khoảng cách — sai số là lỗi critical nên phải ghi được trong export |
| `relevance` | — | attribute | `__undefined__`, `ego`, `not_ego`, `unclear` | `__undefined__` | không | Biển có áp dụng cho xe mình không (quy tắc đặt biển bên phải/lặp trái/trên cao) |
| `facing` | — | attribute | `front`, `back`, `edge_on` | `front` | không | Mặt sau/cạnh vẫn label để model học, nhưng luôn `not_ego` |
| `occlusion` | — | attribute | `none`, `partial`, `heavy` | `none` | không | <10% / 10–50% / 50–90%; >90% không label |
| `readability` | — | attribute | `clear`, `degraded`, `illegible` | `clear` | không | Tách hard example (mờ, loá, đêm, nhỏ) cho downstream |
| `truncated` | — | attribute (checkbox) | true/false | `false` | không | Biển bị mép ảnh cắt |
| `mount` | — | attribute | `roadside`, `overhead`, `other` | `roadside` | không | Vị trí lắp đặt, hữu ích cho bản đồ và suy luận relevance |
| `temporary` | — | attribute (checkbox) | true/false | `false` | không | Biển công trường/tạm (nền vàng Đức, cam Mỹ) |
| `needs_review` | — | attribute (checkbox) | true/false | `false` | không | ESCALATE cấp object |

## Class hay attribute

Chỉ có một class hình học `traffic_sign`: mọi biển cùng geometry và QA rule; tách ~50 loại biển thành class sẽ nổ
taxonomy và làm annotator chọn sai label. Nhóm/loại biển, số trên biển, relevance, visibility là **thuộc tính của cùng
một object** → attribute. Không dùng tag cấp ảnh: ảnh không có box = không có biển; nghi ngờ thì dùng
`sign_category = unknown` hoặc `needs_review` trên từng biển.

Default có thể gây bias: `sign_category`, `sign_type`, `relevance` để `__undefined__` để buộc chọn (còn
`__undefined__` trong export = chưa xong). `facing = front`, `occlusion = none`, `readability = clear` là default
đúng cho đa số biển nhưng có thể tạo lỗi "im lặng" khi annotator quên đổi với biển mờ/mặt sau — QA kiểm riêng các
biển có box nhỏ (< 20 px) hoặc `sign_category = unknown` mà vẫn `readability = clear` / `facing = front`.

## CVAT

- **Phiên bản CVAT** (`make cvat-status`): 2.74.1 (http://localhost:8080)
- **Tên task calibration** (có version guideline, ví dụ `team07-calib-v1`): TODO
- **Guide của task đã dán `02_guideline.md`?** TODO (có / chưa)
- **Nhóm dùng Track hay Shape, vì sao:** Shape — task ảnh tĩnh, mỗi ảnh là một cảnh độc lập, không có object nào
  cần theo qua nhiều frame; không attribute nào `mutable`.
- **Ground truth để chấm peer:** `cvat_annotations/ground_truth_12/` (12 ảnh trong `dataraw/traffic_sign_gt/`,
  53 box), chấm bằng `python project/check_peer_accuracy.py <export peer>.zip`.

## Setup test

Một thành viên **chưa tham gia setup** mở task và trả lời: label gì, dùng tool nào, gán attribute nào, khi nào
escalate. Ghi lại ai test và chỗ họ vấp:

TODO
