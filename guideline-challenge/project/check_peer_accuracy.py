"""Chấm accuracy export CVAT của nhóm peer so với ground truth của nhóm owner.

Chỉ cần Python 3 (thư viện chuẩn). Chạy từ thư mục guideline-challenge/:

    python project/check_peer_accuracy.py peer_export.zip
    python project/check_peer_accuracy.py peer_export.zip --iou 0.5 --out project/07_blind_handoff/peer_accuracy

Đầu vào: file export **CVAT for images 1.1** (.zip chứa annotations.xml, hoặc chính file .xml), label theo
`03_cvat_labels.json` và `02_guideline.md`. Ảnh được ghép theo tên file bỏ đuôi (BDD01.jpg ↔ BDD01).

Cách chấm (khớp với 05_qa_plan.md):
  1. Ghép box peer với box ground truth trên cùng ảnh bằng IoU (greedy, IoU cao nhất trước, ngưỡng --iou).
  2. Detection: precision / recall / F1 trên box `traffic_sign`.
  3. Attribute: tỉ lệ đúng từng attribute trên các cặp đã ghép.
  4. Critical: biển STOP / nhường đường / cấm đi vào / giới hạn tốc độ trong ground truth phải được vẽ, đúng
     sign_type, đúng relevance và (với speed_limit) đúng value_text — hoặc `?` kèm needs_review=true khi không
     đọc chắc số (guideline mục 6). Sai hoặc sót = critical escape.
  5. Geometry: IoU trung bình và tỉ lệ box đạt tolerance của guideline mục 3 (mỗi cạnh lệch ≤ 2 px, ≤ 1 px với
     biển có cạnh ngắn < 30 px).
  6. Quality gate PASS / REWORK / REJECT theo ngưỡng ở cuối file này.

Đầu ra (thư mục --out): matches.csv (từng box), per_image.csv, summary.md.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_GT = HERE / "cvat_annotations" / "ground_truth_12" / "annotations.xml"
DEFAULT_PACK = HERE / "sample_pack.csv"
DEFAULT_OUT = HERE / "07_blind_handoff" / "peer_accuracy"

LABEL = "traffic_sign"
ATTRIBUTES = ["sign_category", "sign_type", "value_text", "relevance", "facing", "occlusion",
              "readability", "truncated", "mount", "temporary", "needs_review"]
CRITICAL_TYPES = {"stop", "give_way", "no_entry", "speed_limit"}
FORCED = ["sign_category", "sign_type", "relevance"]  # default __undefined__, bắt buộc chọn

# Quality gate — giữ đồng bộ với 05_qa_plan.md
GATE = {
    "f1_pass": 0.85, "category_pass": 0.90, "type_pass": 0.80, "geometry_pass": 0.85,
    "f1_reject": 0.60,
}


# ---------------------------------------------------------------- đọc file

def read_xml_bytes(path: Path) -> bytes:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist() if n.endswith("annotations.xml")]
            if not names:
                sys.exit(f"✗ {path} không có annotations.xml — export lại bằng format 'CVAT for images 1.1'.")
            return archive.read(sorted(names, key=len)[0])
    return path.read_bytes()


def norm_value(name: str, value: str) -> str:
    value = (value or "").strip()
    if name == "value_text":
        value = value.lower().replace(" ", "")
        return "-" if value in ("", "__undefined__") else value
    return value.lower()


def parse(path: Path) -> dict:
    """Trả về {sample_id: [box, ...]}; box = {'box': (x1,y1,x2,y2), 'attrs': {...}}."""
    root = ET.parse(io.BytesIO(read_xml_bytes(path))).getroot()
    if root.tag != "annotations":
        sys.exit(f"✗ {path}: root XML không phải <annotations>.")
    if root.findall("track"):
        sys.exit(f"✗ {path} có <track>: guideline yêu cầu vẽ bằng Shape và export 'CVAT for images 1.1'.")
    images = {}
    for image in root.findall("image"):
        sample = Path(image.get("name", "")).stem
        boxes = []
        for node in image.findall("box"):
            if node.get("label") != LABEL:
                continue
            attrs = {a.get("name"): norm_value(a.get("name"), a.text) for a in node.findall("attribute")}
            boxes.append({"box": tuple(float(node.get(k)) for k in ("xtl", "ytl", "xbr", "ybr")), "attrs": attrs})
        images[sample] = boxes
    return images


def read_pack(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        return {row["sample_id"]: row["split"] for row in csv.DictReader(handle)}


# ---------------------------------------------------------------- hình học

def iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def edge_ok(gt, pred) -> bool:
    short = min(gt[2] - gt[0], gt[3] - gt[1])
    tol = 1.0 if short < 30 else 2.0
    return all(abs(g - p) <= tol + 1e-6 for g, p in zip(gt, pred))


def match(gt_boxes, pred_boxes, threshold):
    pairs = sorted(((iou(g["box"], p["box"]), gi, pi) for gi, g in enumerate(gt_boxes)
                    for pi, p in enumerate(pred_boxes)), reverse=True)
    used_g, used_p, matches = set(), set(), []
    for score, gi, pi in pairs:
        if score < threshold:
            break
        if gi in used_g or pi in used_p:
            continue
        used_g.add(gi)
        used_p.add(pi)
        matches.append((gi, pi, score))
    return matches, [i for i in range(len(gt_boxes)) if i not in used_g], \
        [i for i in range(len(pred_boxes)) if i not in used_p]


def critical_ok(g, p) -> bool:
    ga, pa = g["attrs"], p["attrs"]
    same = all(ga.get(k) == pa.get(k) for k in ("sign_category", "sign_type", "relevance"))
    if ga.get("sign_type") == "speed_limit":
        # Guideline mục 6/7: không đọc chắc số → value_text = ? + needs_review là quyết định đúng, không phải đoán sai.
        honest_unknown = pa.get("value_text") == "?" and pa.get("needs_review") == "true"
        same = same and (ga.get("value_text") == pa.get("value_text") or honest_unknown)
    return same


# ---------------------------------------------------------------- chấm

def ratio(a, b):
    return a / b if b else float("nan")


def pct(x):
    return "—" if x != x else f"{100 * x:.1f}%"


def evaluate(gt, peer, pack, threshold):
    rows, per_image = [], []
    total = defaultdict(int)
    attr_ok = defaultdict(int)
    ious, undefined = [], 0
    by_split = defaultdict(lambda: defaultdict(int))
    missing_images = [s for s in gt if s not in peer]
    extra_images = [s for s in peer if s not in gt]

    for sample in sorted(gt):
        g_boxes, p_boxes = gt[sample], peer.get(sample, [])
        matches, fn, fp = match(g_boxes, p_boxes, threshold)
        split = pack.get(sample, "-")
        img = defaultdict(int)
        img.update(gt=len(g_boxes), peer=len(p_boxes), tp=len(matches), fn=len(fn), fp=len(fp))
        for p in p_boxes:
            undefined += sum(p["attrs"].get(k, "__undefined__") == "__undefined__" for k in FORCED)
        for gi, pi, score in matches:
            g, p = g_boxes[gi], p_boxes[pi]
            ious.append(score)
            geo = edge_ok(g["box"], p["box"])
            total["geometry_ok"] += geo
            wrong = [k for k in ATTRIBUTES if g["attrs"].get(k) != p["attrs"].get(k)]
            for k in ATTRIBUTES:
                attr_ok[k] += k not in wrong
            img["category_ok"] += "sign_category" not in wrong
            img["type_ok"] += "sign_type" not in wrong
            crit = ""
            if g["attrs"].get("sign_type") in CRITICAL_TYPES:
                img["critical"] += 1
                if critical_ok(g, p):
                    crit = "ok"
                    total["critical_ok"] += 1
                else:
                    crit = "ESCAPE"
                    img["critical_escape"] += 1
            rows.append({"sample_id": sample, "split": split, "result": "TP", "iou": f"{score:.3f}",
                         "edge_tolerance": "ok" if geo else "fail", "critical": crit,
                         "gt_category": g["attrs"].get("sign_category"), "gt_type": g["attrs"].get("sign_type"),
                         "peer_category": p["attrs"].get("sign_category"), "peer_type": p["attrs"].get("sign_type"),
                         "gt_value": g["attrs"].get("value_text"), "peer_value": p["attrs"].get("value_text"),
                         "wrong_attributes": ";".join(wrong), "gt_box": fmt(g["box"]), "peer_box": fmt(p["box"])})
        for gi in fn:
            g = g_boxes[gi]
            crit = ""
            if g["attrs"].get("sign_type") in CRITICAL_TYPES:
                img["critical"] += 1
                img["critical_escape"] += 1
                crit = "ESCAPE (sót)"
            rows.append({"sample_id": sample, "split": split, "result": "FN (peer bỏ sót)", "critical": crit,
                         "gt_category": g["attrs"].get("sign_category"), "gt_type": g["attrs"].get("sign_type"),
                         "gt_value": g["attrs"].get("value_text"), "gt_box": fmt(g["box"])})
        for pi in fp:
            p = p_boxes[pi]
            rows.append({"sample_id": sample, "split": split, "result": "FP (peer vẽ thừa)",
                         "peer_category": p["attrs"].get("sign_category"), "peer_type": p["attrs"].get("sign_type"),
                         "peer_value": p["attrs"].get("value_text"), "peer_box": fmt(p["box"])})
        for key in ("gt", "peer", "tp", "fn", "fp", "category_ok", "type_ok", "critical", "critical_escape"):
            total[key] += img[key]
            by_split[split][key] += img[key]
        per_image.append({"sample_id": sample, "split": split, "present_in_export": sample in peer,
                          **{k: img[k] for k in ("gt", "peer", "tp", "fn", "fp", "category_ok", "type_ok",
                                                  "critical", "critical_escape")}})

    tp = total["tp"]
    precision, recall = ratio(tp, total["peer"]), ratio(tp, total["gt"])
    f1 = ratio(2 * precision * recall, precision + recall) if tp else 0.0
    metrics = {
        "precision": precision, "recall": recall, "f1": f1,
        "category_acc": ratio(total["category_ok"], tp), "type_acc": ratio(total["type_ok"], tp),
        "end_to_end": ratio(total["type_ok"], total["gt"] + total["fp"]),
        "geometry_ok": ratio(total["geometry_ok"], tp), "mean_iou": ratio(sum(ious), len(ious)),
        "critical_total": total["critical"], "critical_ok": total["critical_ok"],
        "critical_escape": total["critical"] - total["critical_ok"], "undefined": undefined,
        "attr_acc": {k: ratio(attr_ok[k], tp) for k in ATTRIBUTES},
        "counts": dict(total), "missing_images": missing_images, "extra_images": extra_images,
        "by_split": {k: dict(v) for k, v in by_split.items()},
    }
    metrics["gate"], metrics["gate_reason"] = gate(metrics)
    return metrics, rows, per_image


def gate(m):
    if m["critical_escape"] > 0:
        return "REJECT / ESCALATE", f"{m['critical_escape']} critical escape (sót hoặc sai biển STOP/nhường đường/cấm đi vào/tốc độ)"
    if m["missing_images"]:
        return "REJECT / ESCALATE", "export thiếu ảnh: " + ", ".join(m["missing_images"])
    if m["f1"] < GATE["f1_reject"]:
        return "REJECT / ESCALATE", f"F1 {pct(m['f1'])} < {pct(GATE['f1_reject'])}"
    fails = []
    for key, name in (("f1", "f1_pass"), ("category_acc", "category_pass"), ("type_acc", "type_pass"),
                      ("geometry_ok", "geometry_pass")):
        if not m[key] >= GATE[name]:
            fails.append(f"{key} {pct(m[key])} < {pct(GATE[name])}")
    if m["undefined"]:
        fails.append(f"{m['undefined']} attribute bắt buộc còn __undefined__")
    return ("REWORK", "; ".join(fails)) if fails else ("PASS", "đạt mọi ngưỡng")


def fmt(box):
    return ",".join(f"{v:.1f}" for v in box)


# ---------------------------------------------------------------- xuất

def write_outputs(out: Path, peer_path: Path, gt_path: Path, threshold, m, rows, per_image):
    out.mkdir(parents=True, exist_ok=True)
    fields = ["sample_id", "split", "result", "iou", "edge_tolerance", "critical", "gt_category", "gt_type",
              "peer_category", "peer_type", "gt_value", "peer_value", "wrong_attributes", "gt_box", "peer_box"]
    with (out / "matches.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with (out / "per_image.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_image[0]))
        writer.writeheader()
        writer.writerows(per_image)

    c = m["counts"]
    lines = [
        "# Peer accuracy report", "",
        f"- Ground truth: `{gt_path.name}` · Peer export: `{peer_path.name}` · IoU match ≥ {threshold}",
        f"- **Quality gate: {m['gate']}** — {m['gate_reason']}", "",
        "## Tổng quan", "",
        "| Metric | Giá trị |", "|---|---|",
        f"| Box ground truth / peer | {c.get('gt', 0)} / {c.get('peer', 0)} |",
        f"| TP / FN (sót) / FP (thừa) | {c.get('tp', 0)} / {c.get('fn', 0)} / {c.get('fp', 0)} |",
        f"| Precision / Recall / **F1** | {pct(m['precision'])} / {pct(m['recall'])} / **{pct(m['f1'])}** |",
        f"| sign_category đúng (trên box đã ghép) | {pct(m['category_acc'])} |",
        f"| sign_type đúng (trên box đã ghép) | {pct(m['type_acc'])} |",
        f"| End-to-end (ghép đúng + đúng type) / (GT + FP) | {pct(m['end_to_end'])} |",
        f"| Critical đúng / tổng · **escape** | {m['critical_ok']} / {m['critical_total']} · **{m['critical_escape']}** |",
        f"| Geometry đạt tolerance mục 3 / IoU trung bình | {pct(m['geometry_ok'])} / {m['mean_iou']:.3f} |"
        if m["mean_iou"] == m["mean_iou"] else "| Geometry | — |",
        f"| Attribute bắt buộc còn `__undefined__` | {m['undefined']} |", "",
        "## Accuracy từng attribute (trên box đã ghép)", "",
        "| Attribute | Đúng |", "|---|---|",
        *[f"| {k} | {pct(v)} |" for k, v in m["attr_acc"].items()], "",
        "## Theo split", "",
        "| Split | GT | Peer | TP | FN | FP | Category đúng | Type đúng | Critical escape |",
        "|---|---|---|---|---|---|---|---|---|",
        *[f"| {s} | {v.get('gt', 0)} | {v.get('peer', 0)} | {v.get('tp', 0)} | {v.get('fn', 0)} | {v.get('fp', 0)} | "
          f"{v.get('category_ok', 0)} | {v.get('type_ok', 0)} | {v.get('critical_escape', 0)} |"
          for s, v in sorted(m["by_split"].items())], "",
        "## Theo ảnh", "",
        "| Ảnh | Split | GT | Peer | TP | FN | FP | Type đúng | Critical escape |",
        "|---|---|---|---|---|---|---|---|---|",
        *[f"| {r['sample_id']} | {r['split']} | {r['gt']} | {r['peer']} | {r['tp']} | {r['fn']} | {r['fp']} | "
          f"{r['type_ok']} | {r['critical_escape']} |" for r in per_image], "",
    ]
    if m["missing_images"]:
        lines.append("Ảnh có trong ground truth nhưng thiếu trong export: " + ", ".join(m["missing_images"]))
    if m["extra_images"]:
        lines.append("Ảnh trong export nhưng không có ground truth (bỏ qua): " + ", ".join(m["extra_images"]))
    lines += ["", "Chi tiết từng box: `matches.csv`. Mỗi dòng FN/FP/ESCAPE cần phân loại guideline gap / data "
              "ambiguity / execution error trong `peer_feedback.md`."]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines


def main():
    parser = argparse.ArgumentParser(description="Chấm accuracy export CVAT của peer so với ground truth.")
    parser.add_argument("peer", type=Path, help="export CVAT for images 1.1 của peer (.zip hoặc .xml)")
    parser.add_argument("--gt", type=Path, default=DEFAULT_GT, help=f"ground truth (mặc định {DEFAULT_GT.name})")
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK, help="sample_pack.csv để chia theo split")
    parser.add_argument("--iou", type=float, default=0.5, help="ngưỡng IoU để ghép box (mặc định 0.5)")
    parser.add_argument("--only-split", choices=["example", "calibration", "blind"],
                        help="chỉ chấm ảnh thuộc một split")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="thư mục ghi báo cáo")
    args = parser.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    gt, peer, pack = parse(args.gt), parse(args.peer), read_pack(args.pack)
    if args.only_split:
        gt = {s: v for s, v in gt.items() if pack.get(s) == args.only_split}
        peer = {s: v for s, v in peer.items() if s in gt}
    m, rows, per_image = evaluate(gt, peer, pack, args.iou)
    lines = write_outputs(args.out, args.peer, args.gt, args.iou, m, rows, per_image)
    print("\n".join(lines[:22]))
    print(f"\n✓ Đã ghi {args.out / 'summary.md'}, matches.csv, per_image.csv")
    return 0 if m["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
