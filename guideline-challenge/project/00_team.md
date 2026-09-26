# Team

Điền trước phút 15. Thay mọi placeholder; còn sót thì `make status` báo ở gate G1.

- **Team:** Nhóm 20 (ví dụ `team07`)
- **Nhóm peer test bài của mình:** Nhóm 6 (cặp đổi bài Nhóm 20 ↔ Nhóm 6)
- **Nhóm mình test bài của:** Nhóm 6
- **Problem family:** Traffic sign taxonomy — hierarchical sign taxonomy theo nhóm chức năng pháp lý cho biển nhỏ / xa / bị che
- **Nguồn ảnh:** `gtsdb` (6 ảnh) + `bdd100k` (6 ảnh) — bộ trao đổi 12 ảnh trong `project/dataraw/traffic_sign_gt/`

| Thành viên | GitHub | Vai trò chính | File phụ trách |
|---|---|---|---|
| Trần Minh Hiếu | [hieunekkkkkk](https://github.com/Minhhieunekk) | **spec owner** | `01_problem_statement.md`, `02_guideline.md` |
| Đỗ Nguyễn Việt Linh | [VietLinh-1203](https://github.com/VietLinh-1203) | **CVAT owner** | `03_cvat_labels.json`, `03_ontology_and_cvat_setup.md`, `sample_pack.csv`, `09_cvat_export_or_task_reference.txt` |
| Nguyễn Khải Hưng | [ingnett](https://github.com/ingnett) | **gold owner** | `04_edge_cases/` |
| Nguyễn Hải Nam | https://github.com/namng11 | **QA owner** | `05_qa_plan.md`, `06_calibration_report.csv`, `06_calibration_exports/` |
| Vũ Trung Hiếu | [2eSu](https://github.com/2eSu) | **handoff & review owner** | `07_blind_handoff/`, `08_revision_log.md`, `check_peer_accuracy.py` |

Gợi ý chia vai (nhóm 2–3 người thì gộp): **spec owner** (`01`, `02`), **CVAT owner** (`03_*`, `sample_pack.csv`,
`09`), **gold owner** (`04_edge_cases/`), **QA owner** (`05`, `06`, `07_blind_handoff/`). Mỗi file một người sửa
chính để tránh xung đột git. Calibration thì mọi người cùng label.
