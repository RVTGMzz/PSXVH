#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a translation-first queue from Gaia Master 0.6.38 full scanner CSV.

This tool is deliberately source-only:
- requires a real scanner CSV with real file+offset evidence;
- subtracts all currently reviewed committed Japanese source strings;
- dedupes repeated Japanese while preserving every scanned occurrence;
- ranks HIGH + NUL/CTRL candidates first;
- never patches a ROM and never changes runtime translation data.

The queue is NOT a whole-game translation count. It is a review queue derived
from one specific scanner CSV after subtracting the current committed reviewed
source corpus.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
import re

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TR = ROOT / "translation"
MASTER_RE = re.compile(r"^TRANSLATION_MASTER_0\.6_part0[1-6]\.csv$", re.I)
JP_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]")
TRUSTED_NAME_MARKERS = (
    "SOURCE_FULL",
    "SOURCE_REVIEWED",
    "REVIEWED_",
    "_REVIEW_",
    "SOURCE_REVIEW_GAPS",
)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            raise RuntimeError(f"No CSV header: {path}")
        return list(r.fieldnames), list(r)


def write_csv(path: Path, fields, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def is_japanese(text: str) -> bool:
    return bool(text and JP_RE.search(text))


def trusted_source_file(path: Path) -> bool:
    if MASTER_RE.match(path.name):
        return True
    upper = path.name.upper()
    return any(marker in upper for marker in TRUSTED_NAME_MARKERS)


def reviewed_vi(row: dict[str, str]) -> str:
    for field in ("vi_full_reviewed", "vi_full"):
        value = (row.get(field) or "").strip()
        if value:
            return value
    return ""


def load_reviewed_japanese():
    covered: dict[str, list[tuple[str, str]]] = defaultdict(list)
    master_rows = 0
    master_reviewed = 0
    trusted_files = 0

    for path in sorted(TR.glob("*.csv")):
        fields, rows = read_csv(path)
        if "japanese" not in fields or not trusted_source_file(path):
            continue
        trusted_files += 1
        is_master = bool(MASTER_RE.match(path.name))
        if is_master:
            master_rows += len(rows)
        for row in rows:
            jp = (row.get("japanese") or "").strip()
            vi = reviewed_vi(row)
            if not is_japanese(jp) or not vi:
                continue
            covered[jp].append((path.name, vi))
            if is_master:
                master_reviewed += 1

    if master_rows != 596 or master_reviewed != 596:
        raise RuntimeError(
            f"Materialized Master gate failed: rows={master_rows} reviewed={master_reviewed}, expected 596/596"
        )
    return covered, trusted_files


def norm_confidence(raw: str) -> str:
    value = (raw or "").strip().upper()
    return value if value in {"HIGH", "MEDIUM"} else value or "UNKNOWN"


def norm_terminator(raw: str) -> str:
    value = (raw or "").strip().upper()
    return value or "UNKNOWN"


def rank_occurrence(row: dict[str, str]):
    confidence = norm_confidence(row.get("confidence") or "")
    terminator = norm_terminator(row.get("terminator") or "")
    anchor = (row.get("anchor") or "").strip()
    priority = (row.get("priority") or "").strip().upper()
    # Smaller tuple = better representative.
    return (
        0 if confidence == "HIGH" else 1,
        0 if terminator in {"NUL", "CTRL"} else 1,
        0 if anchor else 1,
        0 if priority == "UNSEEN-JAPANESE" else 1,
        int(row.get("byte_len") or 999999),
        (row.get("file") or ""),
        int((row.get("offset_hex") or "0"), 0),
    )


def occurrence_ref(row: dict[str, str]) -> str:
    return f"{(row.get('file') or '').strip()}+{(row.get('offset_hex') or '').strip()}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scanner_csv", type=Path)
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args()

    scan_path = args.scanner_csv.expanduser().resolve()
    if not scan_path.is_file():
        raise RuntimeError(f"Scanner CSV does not exist: {scan_path}")

    out_dir = (args.out_dir or scan_path.parent).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    fields, scan_rows = read_csv(scan_path)
    required = {
        "file", "offset_hex", "japanese", "byte_len", "terminator",
        "confidence", "priority",
    }
    missing_fields = sorted(required - set(fields))
    if missing_fields:
        raise RuntimeError(f"Scanner CSV missing required columns: {missing_fields}")

    reviewed, trusted_files = load_reviewed_japanese()

    valid_scan_rows = []
    malformed_offsets = []
    for row in scan_rows:
        jp = (row.get("japanese") or "").strip()
        if not is_japanese(jp):
            continue
        try:
            int((row.get("offset_hex") or "0"), 0)
        except ValueError:
            malformed_offsets.append((row.get("file"), row.get("offset_hex"), jp))
            continue
        valid_scan_rows.append(row)
    if malformed_offsets:
        raise RuntimeError(f"Malformed scanner offsets: {malformed_offsets[:10]}")

    # Keep only Japanese not yet represented in the reviewed committed corpus.
    new_rows = [r for r in valid_scan_rows if (r.get("japanese") or "").strip() not in reviewed]

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in new_rows:
        grouped[(row.get("japanese") or "").strip()].append(row)

    queue = []
    high_unique = 0
    medium_only_unique = 0
    for jp, occurrences in grouped.items():
        occurrences = sorted(occurrences, key=rank_occurrence)
        best = occurrences[0]
        best_conf = norm_confidence(best.get("confidence") or "")
        best_term = norm_terminator(best.get("terminator") or "")
        best_is_high = best_conf == "HIGH" and best_term in {"NUL", "CTRL"}
        if best_is_high:
            high_unique += 1
        else:
            medium_only_unique += 1

        anchors = sorted({(r.get("anchor") or "").strip() for r in occurrences if (r.get("anchor") or "").strip()})
        refs = [occurrence_ref(r) for r in occurrences]
        priorities = sorted({(r.get("priority") or "").strip() for r in occurrences if (r.get("priority") or "").strip()})
        queue.append({
            "queue_tier": "HIGH-FIRST" if best_is_high else "REVIEW-MEDIUM",
            "japanese": jp,
            "best_file": (best.get("file") or "").strip(),
            "best_offset_hex": (best.get("offset_hex") or "").strip(),
            "best_byte_len": (best.get("byte_len") or "").strip(),
            "best_confidence": best_conf,
            "best_terminator": best_term,
            "occurrence_count": str(len(occurrences)),
            "scanner_priorities": " | ".join(priorities),
            "anchors": " | ".join(anchors),
            "all_exact_refs": " | ".join(refs),
            "vi_full": "",
            "translation_status": "NEEDS_SOURCE_TRANSLATION",
        })

    queue.sort(key=lambda r: (
        0 if r["queue_tier"] == "HIGH-FIRST" else 1,
        0 if r["anchors"] else 1,
        -int(r["occurrence_count"]),
        int(r["best_byte_len"] or 999999),
        r["japanese"],
    ))

    high_queue = [r for r in queue if r["queue_tier"] == "HIGH-FIRST"]

    queue_path = out_dir / "GaiaMaster_TRANSLATION_QUEUE_REVIEWED_DEDUPED.csv"
    high_path = out_dir / "GaiaMaster_TRANSLATION_QUEUE_HIGH_FIRST.csv"
    occurrence_path = out_dir / "GaiaMaster_TRANSLATION_QUEUE_NEW_OCCURRENCES.csv"
    report_path = out_dir / "GaiaMaster_TRANSLATION_QUEUE_REPORT.txt"

    queue_fields = [
        "queue_tier", "japanese", "best_file", "best_offset_hex", "best_byte_len",
        "best_confidence", "best_terminator", "occurrence_count", "scanner_priorities",
        "anchors", "all_exact_refs", "vi_full", "translation_status",
    ]
    write_csv(queue_path, queue_fields, queue)
    write_csv(high_path, queue_fields, high_queue)

    occurrence_fields = [
        "file", "offset_hex", "japanese", "byte_len", "chars", "kana", "kanji",
        "jp_ratio", "terminator", "confidence", "known_same_offset",
        "known_text_elsewhere", "master_offset_text", "priority", "anchor",
    ]
    write_csv(
        occurrence_path,
        occurrence_fields,
        [{k: r.get(k, "") for k in occurrence_fields} for r in new_rows],
    )

    raw_unseen_unique = len({
        (r.get("japanese") or "").strip()
        for r in valid_scan_rows
        if (r.get("priority") or "").strip().upper() == "UNSEEN-JAPANESE"
    })
    reviewed_overlap_occurrences = len(valid_scan_rows) - len(new_rows)

    report_lines = [
        "GAIA MASTER - REVIEWED-DEDUPED FULL SCAN TRANSLATION QUEUE",
        "=" * 76,
        f"Scanner CSV                    : {scan_path.name}",
        f"Scanner candidate rows         : {len(scan_rows)}",
        f"Valid Japanese scanner rows    : {len(valid_scan_rows)}",
        f"Raw scanner UNSEEN unique      : {raw_unseen_unique}",
        f"Reviewed committed unique JP   : {len(reviewed)}",
        f"Trusted reviewed source files  : {trusted_files}",
        f"Reviewed-overlap occurrences   : {reviewed_overlap_occurrences}",
        f"NEW source occurrences         : {len(new_rows)}",
        f"NEW UNIQUE Japanese queue      : {len(queue)}",
        f"HIGH-FIRST unique              : {high_unique}",
        f"REVIEW-MEDIUM unique           : {medium_only_unique}",
        "Runtime/build changes          : 0",
        "Whole-game translation claim  : NO",
        "",
        "QUEUE POLICY:",
        "- Japanese is deduped for translation, but every real scanner file+offset is retained.",
        "- HIGH-FIRST means the best occurrence is HIGH and NUL/CTRL terminated.",
        "- Existing reviewed committed Japanese is subtracted before queue creation.",
        "- MEDIUM candidates still require source review because scanner false positives are possible.",
        "- vi_full is intentionally blank for the next translation pass.",
        "",
        f"Full queue : {queue_path.name}",
        f"High queue : {high_path.name}",
        f"Occurrences: {occurrence_path.name}",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print("\n".join(report_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
