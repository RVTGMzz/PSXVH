#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inventory committed Japanese translation sources not yet covered by reviewed source text.

Scope:
- scans only committed CSV files under translation/;
- never scans/builds a ROM;
- never invents offsets;
- never changes Translation Master or runtime data;
- dedupes Japanese text separately from exact source rows.

A Japanese string is considered source-reviewed when it appears in a trusted
source-review file with a non-empty source-level Vietnamese field. The current
materialized Translation Master is trusted because all 596 vi_full rows were
proved by the 2026-09-15 editorial source audit.

This report is NOT whole-game coverage. It only describes residual Japanese
present in committed translation CSV sources.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
MASTER_RE = re.compile(r"^TRANSLATION_MASTER_0\.6_part0[1-6]\.csv$", re.I)
JP_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]")

# These filename markers identify files whose purpose is explicitly reviewed
# or natural source-level Vietnamese, rather than byte-fit runtime wording.
TRUSTED_NAME_MARKERS = (
    "SOURCE_FULL",
    "SOURCE_REVIEWED",
    "REVIEWED_",
    "_REVIEW_",
    "SOURCE_REVIEW_GAPS",
)

# Source-level Vietnamese field names used by the reviewed companions.
TRUSTED_VI_FIELDS = (
    "vi_full_reviewed",
    "vi_full",
)

# Runtime/compact fields are deliberately NOT accepted as proof of source-level
# editorial coverage.
DISPLAY_VI_FIELDS = (
    "vi_full_reviewed",
    "vi_full",
    "vi_accented",
    "vi_runtime_current",
    "vi_game_current",
    "vi_compact",
    "vietnamese",
)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            return [], []
        return list(r.fieldnames), list(r)


def is_japanese_source(text: str) -> bool:
    return bool(text and JP_RE.search(text))


def is_trusted_source_file(path: Path) -> bool:
    name = path.name.upper()
    if MASTER_RE.match(path.name):
        return True
    return any(marker in name for marker in TRUSTED_NAME_MARKERS)


def reviewed_vi(row: dict[str, str]) -> str:
    for field in TRUSTED_VI_FIELDS:
        value = (row.get(field) or "").strip()
        if value:
            return value
    return ""


def display_vi(row: dict[str, str]) -> str:
    for field in DISPLAY_VI_FIELDS:
        value = (row.get(field) or "").strip()
        if value:
            return value
    return ""


def exact_source_file(row: dict[str, str]) -> str:
    return (row.get("file") or row.get("file_scope") or row.get("target_file") or "").strip()


def exact_offset(row: dict[str, str]) -> str:
    return (row.get("offset_hex") or row.get("offset") or "").strip()


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=Path("gaia_translation_residual_audit"))
    args = ap.parse_args()
    out_dir = args.out_dir.resolve()

    csv_files = sorted(TR.glob("*.csv"))
    if not csv_files:
        raise RuntimeError(f"No translation CSV files found in {TR}")

    parsed: dict[Path, tuple[list[str], list[dict[str, str]]]] = {}
    japanese_csv_files = []
    trusted_files = []
    covered_japanese: dict[str, list[tuple[str, str]]] = defaultdict(list)

    # Pass 1: build reviewed Japanese coverage from canonical/reviewed files.
    for path in csv_files:
        fields, rows = read_csv(path)
        parsed[path] = (fields, rows)
        if "japanese" not in fields:
            continue
        japanese_csv_files.append(path)
        if not is_trusted_source_file(path):
            continue
        trusted_files.append(path)
        for row in rows:
            jp = (row.get("japanese") or "").strip()
            if not is_japanese_source(jp):
                continue
            vi = reviewed_vi(row)
            if not vi:
                continue
            covered_japanese[jp].append((path.name, vi))

    # Materialized Master must contribute all 596 exact rows.
    master_rows = 0
    master_reviewed = 0
    for path in csv_files:
        if not MASTER_RE.match(path.name):
            continue
        fields, rows = parsed[path]
        master_rows += len(rows)
        for row in rows:
            jp = (row.get("japanese") or "").strip()
            vi = (row.get("vi_full") or "").strip()
            if is_japanese_source(jp) and vi:
                master_reviewed += 1
    if master_rows != 596 or master_reviewed != 596:
        raise RuntimeError(
            f"Materialized Master source gate failed: rows={master_rows} reviewed={master_reviewed}, expected 596/596"
        )

    # Pass 2: collect every committed Japanese source row not represented in
    # reviewed source coverage. Trusted files are scanned too, so a blank row
    # in one of them cannot silently disappear.
    residual_rows: list[dict[str, str]] = []
    source_file_counts = Counter()
    residual_unique_sources: dict[str, list[dict[str, str]]] = defaultdict(list)

    for path in japanese_csv_files:
        _fields, rows = parsed[path]
        for row_index, row in enumerate(rows, start=2):
            jp = (row.get("japanese") or "").strip()
            if not is_japanese_source(jp):
                continue
            if jp in covered_japanese:
                continue

            item = {
                "source_csv": path.name,
                "csv_line": str(row_index),
                "source_file": exact_source_file(row),
                "offset_hex": exact_offset(row),
                "japanese": jp,
                "existing_vi": display_vi(row),
                "source_status": (row.get("status") or row.get("source") or row.get("note") or "").strip(),
            }
            residual_rows.append(item)
            residual_unique_sources[jp].append(item)
            source_file_counts[path.name] += 1

    # One summary row per unique Japanese string. Do not pretend a repeated
    # Japanese phrase at many offsets is many new translations.
    unique_rows: list[dict[str, str]] = []
    for jp in sorted(residual_unique_sources):
        items = residual_unique_sources[jp]
        csv_names = sorted({i["source_csv"] for i in items})
        source_files = sorted({i["source_file"] for i in items if i["source_file"]})
        offsets = sorted({i["offset_hex"] for i in items if i["offset_hex"]})
        existing_vis = []
        seen_vi = set()
        for i in items:
            vi = i["existing_vi"]
            if vi and vi not in seen_vi:
                existing_vis.append(vi)
                seen_vi.add(vi)
        first = items[0]
        unique_rows.append({
            "japanese": jp,
            "committed_row_count": str(len(items)),
            "source_csv_count": str(len(csv_names)),
            "source_csvs": " | ".join(csv_names),
            "source_files": " | ".join(source_files),
            "known_offsets": " | ".join(offsets),
            "first_source_csv": first["source_csv"],
            "first_offset_hex": first["offset_hex"],
            "existing_vi_candidates": " | ".join(existing_vis[:8]),
            "needs_source_review": "YES",
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / "GAIA_COMMITTED_RESIDUAL_JAPANESE_ROWS_2026-09-15.csv"
    unique_path = out_dir / "GAIA_COMMITTED_RESIDUAL_JAPANESE_UNIQUE_2026-09-15.csv"
    report_path = out_dir / "GAIA_COMMITTED_RESIDUAL_JAPANESE_REPORT_2026-09-15.txt"

    row_fields = [
        "source_csv", "csv_line", "source_file", "offset_hex", "japanese",
        "existing_vi", "source_status",
    ]
    unique_fields = [
        "japanese", "committed_row_count", "source_csv_count", "source_csvs",
        "source_files", "known_offsets", "first_source_csv", "first_offset_hex",
        "existing_vi_candidates", "needs_source_review",
    ]
    write_csv(rows_path, row_fields, residual_rows)
    write_csv(unique_path, unique_fields, unique_rows)

    with report_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("GAIA MASTER - COMMITTED RESIDUAL JAPANESE SOURCE AUDIT\n")
        f.write("=" * 72 + "\n")
        f.write(f"Translation CSV files scanned       : {len(csv_files)}\n")
        f.write(f"CSV files with japanese column      : {len(japanese_csv_files)}\n")
        f.write(f"Trusted reviewed source files       : {len(trusted_files)}\n")
        f.write(f"Materialized Master reviewed rows   : {master_reviewed} / 596\n")
        f.write(f"Reviewed unique Japanese strings    : {len(covered_japanese)}\n")
        f.write(f"Residual committed source rows      : {len(residual_rows)}\n")
        f.write(f"Residual UNIQUE Japanese strings    : {len(unique_rows)}\n")
        f.write("Runtime/build changes               : 0\n")
        f.write("Whole-game coverage claim           : NO\n")
        f.write("\nTop residual source CSVs by row count:\n")
        for name, count in source_file_counts.most_common(30):
            f.write(f"- {count:5d}  {name}\n")
        f.write("\nScope note:\n")
        f.write(
            "Residual means Japanese found in committed translation CSV sources but not "
            "present in the current reviewed/source-full Japanese coverage set. It is not "
            "the missing 0.6.38 whole-game scanner corpus and must not be added to the "
            "6,361 unseen count as if it were newly scanned ROM data.\n"
        )

    print(report_path.read_text(encoding="utf-8"), end="")
    print(f"Rows CSV   : {rows_path}")
    print(f"Unique CSV : {unique_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
