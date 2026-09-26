# Annotation guideline — Phân loại biển báo giao thông theo cấp bậc (hierarchical sign taxonomy) cho biển nhỏ / xa / bị che

**Version:** v1

> Đọc hết mục 1–7 trước khi vẽ object đầu tiên. Mục 4 (taxonomy) và mục 7 (escalation) là nơi hay sai nhất.
> Mọi quyết định phải nhìn thấy được trong file export CVAT: box + attribute. Không có "quyết định trong
> đầu".

## 0. Căn cứ pháp lý (đọc 2 phút)

Ảnh đến từ hai hệ thống biển báo khác nhau. Guideline này **phân loại theo chức năng pháp lý của biển**, không theo
cảm giác, dựa trên các văn bản sau:

| Văn bản | Áp dụng cho | Dùng để làm gì trong guideline |
|---|---|---|
| **Công ước Viên 1968 về báo hiệu đường bộ** (Convention on Road Signs and Signals) | Khung chung | Chia biển thành các nhóm chức năng: A nguy hiểm, B ưu tiên, C cấm/hạn chế, D hiệu lệnh, E/F/G chỉ dẫn, H biển phụ. Đây là trục chính của `sign_category` |
| **StVO (Đức)** — Anlage 1 Gefahrzeichen, Anlage 2 Vorschriftzeichen, Anlage 3 Richtzeichen, Zusatzzeichen; §43 Verkehrseinrichtungen | Ảnh `GTS*` | Tra biển cụ thể của Đức. Đức là thành viên Công ước Viên |
| **MUTCD (Hoa Kỳ)** — Regulatory (R), Warning (W), Guide (D/E/M), plaques | Ảnh `BDD*` (đa số ở Mỹ) | Tra biển Mỹ. Mỹ **không** theo Công ước Viên: hình thoi vàng = cảnh báo, chữ nhật trắng = quy định |
| **QCVN 41:2024/BGTVT (Việt Nam)** — nhóm P (cấm), R (hiệu lệnh), W (nguy hiểm và cảnh báo), I (chỉ dẫn), S (biển phụ) | Đối chiếu | Đội VN dùng mã P/R/W/I/S để hiểu nhanh nhóm chức năng. Không có ảnh VN trong bộ dữ liệu |

Nguyên tắc khi các hệ thống mâu thuẫn: **xác định hệ thống của biển trước (Đức/Viên hay Mỹ), rồi mới đọc hình dạng
và màu theo hệ thống đó.** Cùng một hình thoi vàng: ở Đức là "đường ưu tiên" (nhóm ưu tiên), ở Mỹ là biển cảnh báo.
Ảnh `GTS*` luôn là hệ thống Đức. Ảnh `BDD*` phần lớn là Mỹ; một số ảnh BDD có chữ Hebrew (Israel, hệ thống gần với
Công ước Viên) — đọc theo bảng hình dạng/màu kiểu Viên ở mục 4.3.

## 1. Objective + scope

**Mục tiêu downstream:** dữ liệu để train và đánh giá module **nhận diện biển báo cho ADAS / cập nhật bản đồ** (phát
hiện biển → phân loại nhóm pháp lý → phân loại loại biển → biết biển có áp dụng cho xe mình không). Lỗi đắt nhất là
**bỏ sót hoặc phân loại sai biển điều khiển trực tiếp hành vi của xe mình**: STOP, nhường đường, cấm đi vào, giới
hạn tốc độ (kể cả sai con số).

**Trong scope — bắt buộc label:** mọi **biển báo giao thông chính thức** (mặt biển do cơ quan quản lý đường đặt, có
hình dạng/màu/ký hiệu theo luật), gồm:

- biển nguy hiểm/cảnh báo, biển ưu tiên, biển cấm/hạn chế, biển hiệu lệnh, biển chỉ dẫn (kể cả biển chỉ hướng, biển
  số đường, biển tên đường, biển trạm xe buýt, biển giá long môn trên cao), biển phụ;
- biển tạm thời (công trường, biển trên chân đế di động), biển nhìn từ mặt sau hoặc từ cạnh (label để model học, xem
  mục 5 và 6);
- bảng chevron chỉ hướng vòng cua (StVO Z. 625, MUTCD W1-8) — tuy StVO xếp Z. 625 vào "Verkehrseinrichtung", chức năng
  giống biển cảnh báo MUTCD nên label thống nhất (ngoại lệ có chủ đích, xem mục 4).

**Ngoài scope — không label (IGNORE):**

- đèn tín hiệu giao thông (kể cả tấm hậu đèn), vạch kẻ đường, chữ/mũi tên sơn trên mặt đường;
- thiết bị an toàn theo StVO §43 không phải biển: cọc tiêu (Leitpfosten), tấm sọc đỏ-trắng dựng đứng (Leitbake),
  rào chắn, cọc giao thông, nón giao thông;
- biển quảng cáo, biển cửa hàng (ví dụ chữ "A" đỏ của nhà thuốc Đức), biển tên toà nhà, số nhà, tranh tường/graffiti
  **có hình giống biển báo**, biển trên xe (xe buýt, xe tải, taxi), sticker/vật trên kính lái;
- **phản chiếu** của biển trên nắp capô, kính, cửa kính, vũng nước;
- biển quá nhỏ: cạnh ngắn của box < **10 px** ở độ phân giải gốc (xem mục 6).

## 2. Annotation unit

- **Đơn vị:** một **mặt biển vật lý** (một tấm biển) trên một ảnh tĩnh. Mỗi tấm = một box `traffic_sign`.
- Một cột có nhiều tấm chồng lên nhau (ví dụ biển tốc độ + 2 biển phụ bên dưới) → **mỗi tấm một box riêng**. Biển phụ
  là box riêng với `sign_category = supplementary_panel`.
- Một giá long môn (gantry) có nhiều bảng: bảng có **khung viền riêng / khe hở giữa hai bảng** → box riêng. Các phần
  in trên **cùng một nền, cùng một viền** (ví dụ tab "EXIT 40" dính liền mép trên bảng xanh) → một box.
- Hai biển giống hệt nhau ở hai bên đường (lặp lại theo luật) → **hai box**, cả hai đều label.
- Biển gấp đôi / biển hai mặt: chỉ label mặt nhìn thấy trong ảnh.
- Ảnh không có biển nào trong scope → **không vẽ box nào** (ảnh để trống là quyết định "không có biển"; vì vậy phải
  quét hết ảnh trước khi chuyển ảnh).

## 3. Geometry rule

- **Công cụ:** Rectangle, chế độ **Shape** (ảnh tĩnh, không dùng Track).
- **Tight box quanh phần mặt biển nhìn thấy** (visible, không amodal): bao trọn viền biển (kể cả viền trắng/đen ngoài
  cùng), **không** bao cột, giá đỡ, bóng đổ.
- Biển tròn/tam giác/bát giác/thoi: box là hình chữ nhật nhỏ nhất ôm các điểm ngoài cùng của viền.
- Bị che một phần: box chỉ ôm phần mặt biển **nhìn thấy**; không đoán phần bị che.
- Bị cắt ở mép ảnh: box chạy tới mép ảnh, bật `truncated`.
- Biển nhìn nghiêng / từ cạnh: box ôm hình chiếu nhìn thấy (có thể rất hẹp).
- **Tolerance:** mỗi cạnh box lệch so với mép biển thật ≤ **2 px** (biển có cạnh ngắn ≥ 30 px) hoặc ≤ **1 px** (biển
  nhỏ hơn). Zoom tối thiểu 200% khi vẽ biển < 30 px. Box ôm cả cột hoặc thừa > 20% chiều rộng là **sai geometry**.

## 4. Taxonomy

Một label hình học duy nhất: **`traffic_sign`** (rectangle). Phân loại bằng attribute theo 2 tầng:
`sign_category` (nhóm chức năng pháp lý, tầng 1) → `sign_type` (loại biển, tầng 2). Lý do dùng attribute thay vì
class: mọi biển có cùng geometry rule và QA rule; tách ~50 loại biển thành class sẽ nổ taxonomy và làm annotator mất
thời gian chọn label.

### 4.1 Tầng 1 — `sign_category` (bắt buộc chọn, default `__undefined__`)

| Giá trị | Công ước Viên | StVO (Đức) | MUTCD (Mỹ) | QCVN 41 (VN) | Nhận dạng điển hình |
|---|---|---|---|---|---|
| `danger_warning` | A | Gefahrzeichen (Z. 101–151) + Z. 625 chevron | Warning (W), nền vàng/cam | W (nguy hiểm và cảnh báo) | Đức/Viên: tam giác đỉnh lên, viền đỏ. Mỹ: **thoi vàng** hoặc chữ nhật vàng; trường học/người đi bộ màu vàng-xanh huỳnh quang |
| `priority` | B | Z. 205, 206, 301, 306, 307, 308, 208 | R1-1 STOP, R1-2 YIELD | R.122 (Dừng lại), W.208 (Giao nhau với đường ưu tiên), I.401 (Bắt đầu đường ưu tiên)… | Bát giác đỏ STOP; tam giác **đỉnh xuống** (nhường đường); thoi vàng viền trắng (đường ưu tiên, **chỉ ở hệ Viên**); tam giác viền đỏ có mũi tên đen to (ưu tiên ở nút tới) |
| `prohibitory` | C | Vorschriftzeichen dạng cấm (Z. 250–283, 274, 276, 277…) | Regulatory dạng cấm/giới hạn: SPEED LIMIT, DO NOT ENTER, NO TURN, NO PARKING | P (biển cấm) | Hình tròn **viền đỏ** nền trắng; tròn nền xanh viền đỏ (cấm dừng/đỗ); tròn trắng có vạch chéo đen (hết cấm/hết hạn chế). Mỹ: chữ nhật trắng chữ đen nội dung giới hạn/cấm |
| `mandatory` | D | Z. 209–222, 237–241 (tròn xanh) | Regulatory bắt buộc: KEEP RIGHT, lane-use ONLY | R (hiệu lệnh) | Hình tròn **nền xanh** ký hiệu trắng |
| `informative` | E, F, G | Richtzeichen (Z. 306 **trừ**, Z. 310–470, 350, 437…) | Guide (xanh lá/xanh dương/nâu), ONE WAY, street name | I (chỉ dẫn) | Chữ nhật/vuông nền xanh dương, xanh lá, vàng (biển hướng Đức), trắng; biển số đường; biển tên đường; vuông xanh có người đi bộ (Z. 350) |
| `supplementary_panel` | H | Zusatzzeichen | Plaque (tấm phụ dưới biển chính) | S (biển phụ) | Tấm nhỏ trắng/vàng gắn **ngay dưới** biển chính, ghi khoảng cách, giờ, loại xe, mũi tên |
| `unknown` | — | — | — | — | Nhìn thấy là biển nhưng không xác định được nhóm (quá nhỏ, mờ, mặt sau, bị che) |

**Quy tắc phân xử tầng 1 (theo thứ tự ưu tiên, dừng ở quy tắc đầu tiên khớp):**

1. STOP, nhường đường, đường ưu tiên, hết đường ưu tiên, ưu tiên ở nút tới, ưu tiên/nhường xe ngược chiều → **luôn**
   `priority`, bất kể hệ thống xếp vào nhóm nào (QCVN xếp "Dừng lại" vào R, "Giao nhau với đường ưu tiên" vào W; ta
   vẫn chọn `priority` vì downstream cần tách riêng nhóm quyền ưu tiên — đây là nhóm critical).
2. Tấm nhỏ gắn ngay dưới một biển khác, chỉ bổ sung điều kiện (khoảng cách, giờ, loại xe, mũi tên, chữ) →
   `supplementary_panel`. Tấm đứng một mình, có nội dung đầy đủ → không phải biển phụ.
3. Biển Mỹ (MUTCD): chọn theo chức năng — nền vàng/cam/vàng-xanh huỳnh quang → `danger_warning`; chữ nhật trắng có
   nội dung **cấm/giới hạn** → `prohibitory`; nội dung **bắt buộc làm** (KEEP RIGHT, ONLY) → `mandatory`; ONE WAY,
   biển chỉ hướng, biển tên đường → `informative`.
4. Biển hệ Viên (Đức, Israel…): chọn theo **hình dạng + màu** ở bảng trên.
5. Không đủ bằng chứng cho bước 3–4 → `unknown` (xem mục 7).

### 4.2 Tầng 2 — `sign_type` (bắt buộc chọn, default `__undefined__`)

`sign_type` **phải thuộc đúng nhóm** của `sign_category` đã chọn (tổ hợp chéo nhóm là lỗi major). Không chắc loại
cụ thể nhưng chắc nhóm → chọn `other_<nhóm>`. Không chắc cả nhóm → `sign_category = unknown` và `sign_type = unknown`.

| sign_category | sign_type được phép | Ghi chú / ví dụ luật |
|---|---|---|
| `priority` | `stop` · `give_way` · `priority_road` · `end_priority_road` · `priority_next_junction` · `priority_over_oncoming` · `give_way_to_oncoming` | StVO Z. 206 / MUTCD R1-1 = `stop`; Z. 205 / R1-2 = `give_way`; Z. 306 thoi vàng = `priority_road`; Z. 307 (thoi có vạch đen) = `end_priority_road`; Z. 301 (tam giác mũi tên đen to + vạch ngang) = `priority_next_junction` |
| `prohibitory` | `speed_limit` · `end_speed_limit` · `no_entry` · `closed_to_all_vehicles` · `no_overtaking` · `no_overtaking_trucks` · `vehicle_type_ban` · `dimension_weight_limit` · `no_turn` · `no_parking` · `no_stopping` · `end_restrictions` · `other_prohibitory` | Z. 274 / R2-1 / QCVN P.127 = `speed_limit`; Z. 267 / R5-1 DO NOT ENTER / P.102 = `no_entry` (tròn đỏ vạch ngang trắng); Z. 250 (tròn trắng viền đỏ trống) = `closed_to_all_vehicles`; Z. 276 = `no_overtaking`; Z. 277 (xe tải đỏ + xe con) = `no_overtaking_trucks`; biển cấm một loại xe (xe tải, xe máy…) = `vehicle_type_ban`; Z. 282 = `end_restrictions` |
| `mandatory` | `mandatory_direction` · `pass_side` · `roundabout` · `mandatory_path` · `other_mandatory` | Z. 209/211/214 (mũi tên rẽ/đi thẳng) = `mandatory_direction`; Z. 222 (mũi tên chéo xuống, "đi bên phải/trái chướng ngại") / QCVN R.302 = `pass_side`; Z. 215 / R.303 = `roundabout`; đường dành cho xe đạp/người đi bộ (Z. 237/239/240/241) = `mandatory_path` |
| `danger_warning` | `curve` · `general_danger` · `junction_warning` · `pedestrians_ahead` · `children` · `road_works` · `slippery_snow_ice` · `uneven_road` · `road_narrows` · `traffic_signals_ahead` · `animals` · `chevron_alignment` · `other_warning` | Z. 103/105 (cua đơn/cua kép), MUTCD W1-1…W1-6 = `curve`; Z. 101 (dấu "!") = `general_danger`; Z. 102 (nút giao) = `junction_warning`; Z. 101-51 bông tuyết = `slippery_snow_ice`; Z. 123 = `road_works`; Z. 625 / W1-8 = `chevron_alignment`; biển vàng chữ (END FREEWAY…) = `other_warning` |
| `informative` | `pedestrian_crossing` · `parking` · `one_way` · `dead_end` · `direction_guide` · `route_number` · `town_entry_exit` · `motorway_expressway` · `street_name` · `bus_stop` · `other_informative` | Z. 350 vuông xanh người đi bộ = `pedestrian_crossing` (**khác** tam giác cảnh báo người đi bộ = `danger_warning/pedestrians_ahead`); Z. 314 "P" = `parking`; biển chỉ hướng đi các nơi, bảng giá long môn, bảng exit = `direction_guide`; số quốc lộ/Bundesstraße (tấm vàng "226") = `route_number`; Z. 437 / MUTCD D3-1 = `street_name` |
| `supplementary_panel` | `panel_distance` · `panel_time` · `panel_vehicle_type` · `panel_direction` · `panel_text_other` | "↑ 300 m" = `panel_distance`; "7–18 h" = `panel_time`; hình xe tải = `panel_vehicle_type`; mũi tên = `panel_direction` |
| `unknown` | `unknown` | Chỉ đi cùng `sign_category = unknown` |

### 4.3 Các attribute còn lại

| Attribute | Giá trị | Default | Khi nào dùng |
|---|---|---|---|
| `value_text` | chữ tự do | `-` | Ghi **đúng** số/chữ quan trọng trên biển: tốc độ `30`, `120`; tải trọng `7.5t`; khoảng cách `300m`; giờ `7-18h`; chữ ngắn `END FREEWAY 1/2 MI`. Không có số/chữ → để `-`. Có nhưng không đọc được → `?`. Không đoán số: biển tốc độ mờ không chắc 30 hay 80 → `?` (xem mục 7). Biển chỉ hướng nhiều dòng chữ → chỉ cần `-` (không chép địa danh) |
| `relevance` | `ego` · `not_ego` · `unclear` | `__undefined__` (bắt buộc chọn) | Biển có áp dụng cho làn đường/chiều đi của xe quay ảnh không — quy tắc ở mục 4.4 |
| `facing` | `front` · `back` · `edge_on` | `front` | `back`: thấy mặt sau (tấm kim loại xám, khung giằng). `edge_on`: nhìn gần như từ cạnh, không thấy mặt biển |
| `occlusion` | `none` · `partial` · `heavy` | `none` | Tỉ lệ mặt biển bị vật khác che: `none` < 10%; `partial` 10–50%; `heavy` 50–90%. Che > 90% → không label |
| `readability` | `clear` · `degraded` · `illegible` | `clear` | `clear`: đọc được ký hiệu/số rõ. `degraded`: mờ, nhoè chuyển động, loá nắng, tối, nhỏ — **vẫn** xác định được loại. `illegible`: không đọc được ký hiệu (khi đó `sign_type` thường là `other_*` hoặc `unknown`) |
| `truncated` | checkbox | `false` | Biển bị mép ảnh cắt |
| `mount` | `roadside` · `overhead` · `other` | `roadside` | `overhead`: trên giá long môn/cần vươn qua đường. `other`: gắn tường, trên chân đế tạm, trên hàng rào |
| `temporary` | checkbox | `false` | Biển tạm/công trường: nền vàng ở Đức (ví dụ biển hướng "Umleitung" vàng), nền cam ở Mỹ, chân đế di động |
| `needs_review` | checkbox | `false` | ESCALATE cấp object (mục 7) |

### 4.4 Quy tắc `relevance` (dựa trên luật đặt biển)

Theo Công ước Viên, StVO, MUTCD và QCVN 41 (đều là giao thông bên phải): biển đặt ở **lề phải** theo chiều đi, có thể
**lặp lại ở bên trái** (dải phân cách, đảo giao thông, đường một chiều) hoặc **trên cao** phía trên phần đường; biển
chỉ có hiệu lực với dòng xe **nhìn thấy mặt biển**.

- `ego`: `facing = front` **và** biển thuộc phần đường của xe mình: ở lề phải phần đường mình; trên cao phía trên
  phần đường mình (kể cả phía trên làn khác cùng chiều); ở bên trái nhưng trên dải phân cách/đảo giao thông của phần
  đường mình, hoặc là biển lặp lại của biển bên phải; biển ở nút giao phía trước quay mặt về phía xe mình (ví dụ STOP
  ở cả hai bên nút giao chữ T).
- `not_ego`: `facing = back` hoặc `edge_on` (**luôn** `not_ego`); biển rõ ràng thuộc đường khác: đường nhánh/cắt
  ngang, đường song song ngăn bằng rào, phần đường chiều ngược lại, lối ra mà biển đặt bên trong nhánh rẽ đã tách khỏi
  phần đường mình.
- `unclear`: quay mặt về phía xe mình nhưng một ảnh không đủ để biết biển thuộc đường nào (ví dụ biển ở góc nút giao
  khi xe đang rẽ). Nếu `unclear` **và** `sign_type` là `stop`, `give_way`, `no_entry` hoặc `speed_limit` → bật
  thêm `needs_review` (critical).

## 5. Inclusion / exclusion

| Tình huống | Quyết định | Thể hiện trong CVAT |
|---|---|---|
| Biển chính thức, cạnh ngắn ≥ 10 px, thấy mặt trước | LABEL | box `traffic_sign` + đủ attribute |
| Biển phụ dưới biển chính | LABEL riêng | box `supplementary_panel` |
| Biển thấy mặt sau / từ cạnh, cạnh ngắn ≥ 10 px | LABEL | `facing = back`/`edge_on`, `sign_category = unknown`, `sign_type = unknown`, `relevance = not_ego`, `value_text = -`. **Không** suy loại biển từ hình dạng mặt sau |
| Biển tạm / công trường | LABEL | như biển thường + `temporary = true` |
| Bảng chevron vòng cua (Z. 625 / W1-8) | LABEL | `danger_warning / chevron_alignment` |
| Biển trạm xe buýt, biển tên đường, biển số đường | LABEL | `informative / bus_stop · street_name · route_number` |
| Đèn giao thông, vạch sơn, cọc tiêu, tấm sọc Leitbake, nón, rào | IGNORE | không vẽ |
| Biển quảng cáo, nhà thuốc, cửa hàng, tranh tường giống biển | IGNORE | không vẽ |
| Phản chiếu của biển trên capô/kính/vũng nước; sticker trên kính lái | IGNORE | không vẽ |
| Biển trên xe (xe buýt, xe tải) | IGNORE | không vẽ |
| Cạnh ngắn < 10 px | IGNORE | không vẽ |
| Che > 90% (chỉ còn cột hoặc một mẩu viền) | IGNORE | không vẽ |
| Ảnh đã quét hết, không có biển nào trong scope (kể cả ảnh chỉ có biển < 10 px) | IGNORE cả ảnh | không có box nào |

## 6. Visibility / occlusion

- **Kích thước:** đo cạnh ngắn của box ở **độ phân giải gốc** (GTSDB 1360×800, BDD 1280×720). 10–19 px: gần như
  luôn `readability = degraded` hoặc `illegible`; được phép xác định `sign_category` từ **hình dạng + màu** (ví dụ tam
  giác viền đỏ → `danger_warning`) nhưng `sign_type` chỉ chọn khi đọc được ký hiệu, nếu không → `other_<nhóm>`.
- **Bị che:** ước lượng % mặt biển bị che → `occlusion`. Box chỉ ôm phần thấy (mục 3). Che 50–90% mà vẫn nhận ra nhóm
  → label bình thường với `heavy`.
- **Mép ảnh:** `truncated = true`; phân loại theo phần nhìn thấy.
- **Mờ chuyển động / sương mù / ban đêm / loá nắng / ngược sáng:** `readability = degraded`. **Không đoán số tốc độ**:
  số không đọc chắc chắn → `value_text = ?`, `sign_type` vẫn là `speed_limit` nếu nhận ra hình tròn viền đỏ có số.
- **Phản chiếu:** không label (mục 5), kể cả khi phản chiếu rõ hơn biển thật.
- **Biển bị cây che một phần ở xa:** chỉ label khi phần thấy ≥ 10 px và nhận ra là biển; không chắc là biển hay biển
  quảng cáo → ESCALATE (mục 7).

## 7. Ambiguity / escalation

| Quyết định | Khi nào | Thể hiện trong CVAT (nhìn thấy trong export) |
|---|---|---|
| **LABEL** | Chắc là biển chính thức và xác định được ít nhất nhóm | box + `sign_category` ≠ `unknown` |
| **IGNORE** | Thuộc danh sách ngoài scope ở mục 1/5 | không có box (ảnh không còn biển nào → ảnh trống) |
| **UNKNOWN** | Chắc là biển nhưng không xác định được nhóm (nhỏ, mờ, mặt sau, bị che) | box + `sign_category = unknown` + `sign_type = unknown`; số không đọc được → `value_text = ?` |
| **ESCALATE** | (a) không chắc là biển chính thức hay biển thương mại/vật khác; (b) hai nhóm đều hợp lý sau khi áp quy tắc 4.1; (c) `relevance = unclear` với `stop`/`give_way`/`no_entry`/`speed_limit`; (d) biển tốc độ có `value_text = ?` và `relevance = ego`; (e) cả ảnh mờ/khó (đêm, loá, không rõ hệ thống biển) → vẫn label từng biển, bật `needs_review` cho các biển bị ảnh hưởng | vẫn vẽ box, điền **lựa chọn tốt nhất** cho mọi attribute, bật `needs_review = true` |

Ưu tiên: **UNKNOWN trung thực tốt hơn đoán sai.** Đoán sai nhóm critical (ví dụ gán `priority/stop` cho biển mờ không
chắc) tệ hơn `unknown` + `needs_review`.

Đường escalation: object có `needs_review = true` được reviewer (QA owner) xem lại
trong vòng review; quyết định cuối được ghi thành rule/ví dụ mới ở phiên bản guideline sau.

## 8. Temporal rule

Không áp dụng — task ảnh tĩnh (dùng Shape, không dùng Track; mỗi ảnh label độc lập).

## 9. Examples

Ảnh ví dụ thuộc split `example`; các dòng đánh dấu (calib) thuộc split `calibration` — chỉ nêu quyết định cho object
được nhắc tới. Object không nhắc tới trong ảnh vẫn label theo rule chung.

| sample_id | Thấy gì | Expected output | Rule áp dụng |
|---|---|---|---|
| GTS06 | Lề phải: biển tròn viền đỏ "30", bên dưới 2 tấm nhỏ: "↑ 3?? m ↑" (chữ số giữa bị nhoè) và "7–18 h" | 3 box. (1) `prohibitory / speed_limit`, `value_text = 30`, `relevance = ego`. (2) `supplementary_panel / panel_distance`, `value_text = ?` (không đọc chắc chữ số → **không đoán**), `readability = degraded`, `ego`. (3) `supplementary_panel / panel_time`, `value_text = 7-18h`, `ego` | 2 (mỗi tấm một box), 4.1 quy tắc 2, 4.3 `value_text`, 6 (không đoán số) |
| GTS23 | Nút giao chữ T phía trước, 2 biển STOP bát giác (đảo bên trái và lề phải); biển tròn xanh mũi tên chéo xuống phải ở đảo trái | 2 box `priority / stop`, cả hai `relevance = ego` (biển lặp lại hai bên). Biển tròn xanh: `mandatory / pass_side`, `ego` | 4.1 quy tắc 1, 4.4 (biển lặp lại bên trái vẫn là `ego`) — **critical** |
| BDD06 | Ảnh Mỹ, hai biển thoi vàng "END FREEWAY 1/2 MI" (dải giữa bên trái và lề phải) | 2 box `danger_warning / other_warning`, `value_text = END FREEWAY 1/2 MI`, cả hai `ego` (bên trái nằm trên dải phân cách của phần đường mình) | 0 (thoi vàng ở Mỹ = cảnh báo), 4.1 quy tắc 3, 4.4 |
| GTS05 (calib) | Góc phải: cột có mặt sau của một tấm tam giác và một tấm tròn (tấm kim loại xám) | 2 box, `facing = back`, `sign_category = unknown`, `sign_type = unknown`, `relevance = not_ego`, `value_text = -` | Mục 5 (mặt sau), 4.4 |
| BDD01 (calib) | Bảng xanh "23rd Avenue / 16th Avenue" + bảng vàng mũi tên trên giá long môn; **phản chiếu** của chính các bảng này trên capô | Bảng thật: `informative / direction_guide`, `mount = overhead`, `ego`. Phản chiếu trên capô: **không label** | 2 (gantry), mục 5 (phản chiếu) |
| BDD04 (calib) | Ảnh Mỹ, xa: thoi vàng mũi tên rẽ, ngay dưới là tấm vàng nhỏ "15"; biển tròn vàng nhỏ bên trái; biển trắng chữ đỏ lề phải | Thoi vàng: `danger_warning / curve` (hệ Mỹ). Tấm "15" gắn ngay dưới: box riêng `supplementary_panel / panel_text_other`, `value_text = 15`. Biển nhỏ không đọc được ký hiệu: chọn nhóm theo màu/hình, `sign_type = other_<nhóm>`, `readability = illegible` | 0 (hệ Mỹ), 2 (biển phụ box riêng), 6 (biển 10–19 px) |

## 10. Common mistakes

1. **Đọc thoi vàng theo sai hệ thống:** Đức = `priority / priority_road`; Mỹ = `danger_warning`. Luôn xác định hệ
   thống trước (mục 0).
2. **Nhầm nhường đường với cảnh báo:** tam giác **đỉnh xuống** = `priority / give_way`; tam giác **đỉnh lên** viền đỏ
   = `danger_warning`.
3. **Nhầm hai biển người đi bộ:** vuông xanh (Z. 350) = `informative / pedestrian_crossing`; tam giác viền đỏ có người
   = `danger_warning / pedestrians_ahead`.
4. **Nhầm cấm với hiệu lệnh:** tròn **viền đỏ** = `prohibitory`; tròn **nền xanh** = `mandatory`. Tròn trắng có vạch
   chéo đen = hết lệnh cấm (`end_speed_limit` / `end_restrictions`), vẫn là `prohibitory`.
5. **Đoán số tốc độ khi mờ** → sai critical. Không chắc → `value_text = ?` + `needs_review`.
6. **Gộp biển chính và biển phụ vào một box**, hoặc gán biển phụ cùng nhóm với biển chính. Biển phụ luôn là box riêng
   `supplementary_panel`.
7. **Label phản chiếu trên capô, sticker trên kính, biển trên xe buýt, tranh tường** — tất cả là IGNORE.
8. **Label đèn giao thông hoặc cọc tiêu/tấm sọc Leitbake** là biển — ngoài scope.
9. **Box ôm cả cột** hoặc thừa nhiều; box biển nhỏ vẽ ở zoom 100% bị lệch > 1 px.
10. **Bỏ sót biển xa ≥ 10 px** rồi để ảnh trống như ảnh không có biển — luôn quét hết ảnh ở zoom 200% (đặc biệt vùng xa ở giữa ảnh và hai lề) trước khi kết luận.
11. **Để sót `__undefined__`** ở `sign_category`, `sign_type`, `relevance` — trong export còn `__undefined__` là
    object chưa hoàn thành. Dùng chế độ **Attribute annotation** để đi qua từng object.
12. **Tổ hợp chéo nhóm** (ví dụ `sign_category = mandatory`, `sign_type = speed_limit`) — kiểm bảng 4.2.
13. **Gán `relevance = ego` cho biển mặt sau** — `back`/`edge_on` luôn là `not_ego`.
