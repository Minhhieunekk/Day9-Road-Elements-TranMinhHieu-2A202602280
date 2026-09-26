# Ground truth biển báo — CVAT for images 1.1

`ground_truth_12/` là **bộ ground truth chuẩn** của nhóm cho 12 ảnh trao đổi với peer trong
`dataraw/traffic_sign_gt/` (6 GTSDB + 6 BDD100K), label theo `02_guideline.md` và `03_cvat_labels.json`.

| File | Nội dung |
|---|---|
| `ground_truth_12/annotations.xml` | 12 ảnh, 53 box `traffic_sign` |
| `ground_truth_12/ground_truth_12_cvat_for_images_1.1.zip` | cùng nội dung, để import vào CVAT |

Chia split theo `sample_pack.csv`: example GTS06, GTS23, BDD06 · calibration GTS05, BDD01, BDD04, BDD05 ·
blind GTS18, BDD09, GTS17, GTS08, BDD21. **Không gửi folder này cho peer.**

## Chấm peer

Từ thư mục `guideline-challenge/`:

```bash
python project/check_peer_accuracy.py <export_cua_peer>.zip                    # cả 12 ảnh
python project/check_peer_accuracy.py <export_cua_peer>.zip --only-split blind  # chỉ 5 ảnh blind
```

Peer phải tạo task từ đúng 12 ảnh (hoặc 5 ảnh blind), vẽ bằng **Shape**, export **CVAT for images 1.1**. Báo cáo ghi
vào `07_blind_handoff/peer_accuracy/` (`summary.md`, `matches.csv`, `per_image.csv`); quality gate theo
`05_qa_plan.md`.

## Xem ground truth trong CVAT

Tạo task từ 12 ảnh trong `dataraw/traffic_sign_gt/` với labels = `03_cvat_labels.json` (tab Raw), giữ **Sorting
method = lexicographical**, rồi **Actions → Upload annotations → CVAT 1.1** → chọn file zip.

**Calibration:** không import ground truth vào task calibration của từng người — mọi người phải label độc lập trước,
rồi mới so với ground truth.
