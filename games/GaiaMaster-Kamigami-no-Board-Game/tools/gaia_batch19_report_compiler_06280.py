#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaia Master 0.6.28.0 - Batch 19 repo-native report compiler.

Purpose
-------
Reconstruct the missing, reproducible analysis/report stage documented by
BATCH18/BATCH19 without patching the ROM or touching the frozen font/codepage.

Outputs
-------
- GaiaMaster_0.6.28.0_RESIDUAL_ALPHA.csv
- GaiaMaster_0.6.28.0_FIT_PRESSURE.csv
- GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv
- GaiaMaster_0.6.28.0_AUTO_EXACT_OVERRIDES.csv

This tool is intentionally conservative:
- exact locks are generated only from non-empty Translation Master vi_full rows
  that preserve runtime tokens and fit the original Japanese byte field;
- historical 0.6.14.1 exact locks are never replaced;
- semantic/style/consensus candidates are used for residual/pressure analysis,
  but are not silently written back into Translation Master;
- no font, renderer, pointer, atlas, BIN/CUE, or BDP data is modified.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

VERSION = "0.6.28.0"

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TR = ROOT / "translation"

MASTER_PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
HISTORICAL_EXACT = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"

RAW_TOKEN_RE = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
SPACE_RE = re.compile(r"\s+")


def die(msg: str) -> "None":
    raise SystemExit(f"[BLOCKED] {msg}")


def read_csv(path: Path) -> Tuple[List[str], List[dict]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            die(f"No CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def write_csv(path: Path, fields: Sequence[str], rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields), lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def norm_off(value: str) -> str:
    return hex(int(str(value).strip(), 0)).lower()


def norm_key_text(text: str) -> str:
    # Batch 18 explicitly normalizes normal/full-width whitespace.
    text = (text or "").replace("\u3000", " ")
    return SPACE_RE.sub(" ", text).strip()


def runtime_tokens(text: str) -> Tuple[str, ...]:
    return tuple(m.group(0) for m in RAW_TOKEN_RE.finditer(text or ""))


def token_safe(japanese: str, candidate: str) -> bool:
    # Preserve token identity AND order.
    return runtime_tokens(japanese) == runtime_tokens(candidate)


def runtime_len_estimate(text: str) -> int:
    """
    Mirror the proven 0.6.14 wrapper estimate:
    ordinary display units consume 2 bytes; raw runtime tokens stay ASCII-width.
    """
    n = 0
    pos = 0
    text = text or ""
    for match in RAW_TOKEN_RE.finditer(text):
        n += (match.start() - pos) * 2
        n += len(match.group(0).encode("ascii"))
        pos = match.end()
    n += (len(text) - pos) * 2
    return n


def japanese_field_bytes(text: str) -> Optional[int]:
    try:
        return len((text or "").encode("cp932"))
    except UnicodeEncodeError:
        return None


def row_key(row: dict) -> Tuple[str, str]:
    return row["file"].strip(), norm_off(row["offset_hex"])


def pick_value(row: dict, names: Sequence[str]) -> str:
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def batch_number(path: Path) -> int:
    m = re.search(r"BATCH(\d+)", path.name, re.I)
    return int(m.group(1)) if m else -1


def load_latest_map(pattern: str, key_columns: Sequence[str], value_columns: Sequence[str]) -> Dict[str, Tuple[str, str]]:
    """
    Load batch maps in ascending order; later batches override earlier ones.
    Returns normalized key -> (value, source filename).
    """
    result: Dict[str, Tuple[str, str]] = {}
    paths = sorted(TR.glob(pattern), key=lambda p: (batch_number(p), p.name))
    for path in paths:
        _, rows = read_csv(path)
        for row in rows:
            key = pick_value(row, key_columns)
            value = pick_value(row, value_columns)
            if not key or not value:
                continue
            result[norm_key_text(key)] = (value, path.name)
    return result


def consensus_map(rows: Sequence[dict], key_column: str) -> Dict[str, str]:
    """
    Batch 18 rule: if duplicates with an existing vi_full unanimously agree,
    use that consensus for an untranslated copy.
    """
    buckets: Dict[str, set] = defaultdict(set)
    for row in rows:
        key = norm_key_text(row.get(key_column, ""))
        vi = (row.get("vi_full") or "").strip()
        if key and vi:
            buckets[key].add(vi)
    return {key: next(iter(values)) for key, values in buckets.items() if len(values) == 1}


def shorten_variants(text: str) -> List[Tuple[str, str]]:
    """
    Conservative deterministic compact variants for ANALYSIS only.
    They are never written back into Translation Master automatically.
    """
    text = (text or "").strip()
    if not text:
        return []

    variants: List[Tuple[str, str]] = [("full", text)]
    replacements = [
        ("một ", "1 "),
        ("Một ", "1 "),
        ("thẻ Vũ khí", "thẻ VK"),
        ("Thẻ Vũ khí", "Thẻ VK"),
        ("thẻ Sự kiện", "thẻ SK"),
        ("Thẻ Sự kiện", "Thẻ SK"),
        ("Zenny", "Z"),
        (" zenny", " Z"),
        ("lãnh địa", "đất"),
        ("Lãnh địa", "Đất"),
        ("Dựng tượng ", "Dựng "),
    ]

    compact = text
    for old, new in replacements:
        compact = compact.replace(old, new)
    compact = SPACE_RE.sub(" ", compact).strip()
    if compact and compact != text:
        variants.append(("compact", compact))

    seen = set()
    out = []
    for label, candidate in variants:
        if candidate not in seen:
            seen.add(candidate)
            out.append((label, candidate))
    return out


def load_historical_exact() -> Dict[Tuple[str, str], dict]:
    if not HISTORICAL_EXACT.is_file():
        die(f"Missing historical exact lock file: {HISTORICAL_EXACT}")
    _, rows = read_csv(HISTORICAL_EXACT)
    out = {}
    for row in rows:
        try:
            out[(row["file"].strip(), norm_off(row["offset_hex"]))] = row
        except Exception as exc:
            die(f"Bad historical exact row: {row!r}: {exc}")
    return out


def build_candidates(
    row: dict,
    semantic: Dict[str, Tuple[str, str]],
    style: Dict[str, Tuple[str, str]],
    consensus_jp: Dict[str, str],
    consensus_fallback: Dict[str, str],
) -> List[Tuple[str, str]]:
    jp = row.get("japanese", "")
    fallback = row.get("vi_game_current", "")
    jp_key = norm_key_text(jp)
    fb_key = norm_key_text(fallback)

    base: List[Tuple[str, str]] = []

    if jp_key in semantic:
        value, source = semantic[jp_key]
        base.append((f"semantic:{source}", value))

    if jp_key in consensus_jp:
        base.append(("consensus:japanese", consensus_jp[jp_key]))

    vi_full = (row.get("vi_full") or "").strip()
    if vi_full:
        base.append(("vi_full", vi_full))

    if fb_key in style:
        value, source = style[fb_key]
        base.append((f"style:{source}", value))

    if fb_key in consensus_fallback:
        base.append(("consensus:fallback", consensus_fallback[fb_key]))

    expanded: List[Tuple[str, str]] = []
    for source, text in base:
        for variant, candidate in shorten_variants(text):
            suffix = "" if variant == "full" else f":{variant}"
            expanded.append((source + suffix, candidate))

    seen = set()
    result = []
    for source, text in expanded:
        text = text.strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append((source, text))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "checkpoints" / VERSION / "reports",
        help="Output directory (default: checkpoints/0.6.28.0/reports)",
    )
    args = parser.parse_args()

    missing = [str(p) for p in MASTER_PARTS if not p.is_file()]
    if missing:
        die("Missing Translation Master parts:\n  " + "\n  ".join(missing))

    all_rows: List[dict] = []
    for part in MASTER_PARTS:
        _, rows = read_csv(part)
        for row in rows:
            row = dict(row)
            row["_master_part"] = part.name
            all_rows.append(row)

    if len(all_rows) != 596:
        die(f"Translation Master row-count gate failed: expected 596, got {len(all_rows)}")

    semantic = load_latest_map(
        "BATCH*_JP_EXACT_*.csv",
        ("japanese", "japanese_literal"),
        ("vi_fantasy", "vi_accented", "vi_full"),
    )
    style = load_latest_map(
        "BATCH*_STYLE_*.csv",
        ("legacy_fallback", "vi_game_current"),
        ("vi_fantasy", "vi_accented", "vi_full"),
    )
    consensus_jp = consensus_map(all_rows, "japanese")
    consensus_fallback = consensus_map(all_rows, "vi_game_current")
    historical_exact = load_historical_exact()

    residual_rows: List[dict] = []
    pressure_rows: List[dict] = []
    exact_rows: List[dict] = []
    auto_override_rows: List[dict] = []

    fit_count = 0
    meaning_count = 0
    historical_protected = 0
    token_rejected = 0

    for row in all_rows:
        jp = row.get("japanese", "")
        field_bytes = japanese_field_bytes(jp)
        if field_bytes is None:
            continue

        key = row_key(row)
        candidates = build_candidates(row, semantic, style, consensus_jp, consensus_fallback)

        safe_candidates: List[Tuple[str, str, int]] = []
        for source, text in candidates:
            if not token_safe(jp, text):
                token_rejected += 1
                continue
            safe_candidates.append((source, text, runtime_len_estimate(text)))

        if safe_candidates:
            meaning_count += 1

        fitting = [item for item in safe_candidates if item[2] <= field_bytes]
        if fitting:
            fit_count += 1

        if row.get("status", "").strip() == "IN_ALPHA_05" and not safe_candidates:
            residual_rows.append({
                "master_part": row["_master_part"],
                "file": key[0],
                "offset_hex": key[1],
                "japanese": jp,
                "vi_game_current": row.get("vi_game_current", ""),
                "status": row.get("status", ""),
                "note": row.get("note", ""),
            })

        if safe_candidates and not fitting:
            shortest = min(safe_candidates, key=lambda item: (item[2], len(item[1]), item[0]))
            source, text, candidate_bytes = shortest
            pressure_rows.append({
                "master_part": row["_master_part"],
                "file": key[0],
                "offset_hex": key[1],
                "japanese": jp,
                "field_bytes": field_bytes,
                "candidate": text,
                "candidate_bytes": candidate_bytes,
                "over_bytes": candidate_bytes - field_bytes,
                "candidate_source": source,
                "tokens": " ".join(runtime_tokens(jp)),
                "vi_game_current": row.get("vi_game_current", ""),
            })

        # Batch 19 exact-offset lock: ONLY direct vi_full is auto-exported.
        vi_full = (row.get("vi_full") or "").strip()
        if not vi_full:
            continue
        if not token_safe(jp, vi_full):
            continue

        vi_bytes = runtime_len_estimate(vi_full)
        if vi_bytes > field_bytes:
            continue

        if key in historical_exact:
            historical_protected += 1
            continue

        exact_rows.append({
            "master_part": row["_master_part"],
            "file": key[0],
            "offset_hex": key[1],
            "japanese": jp,
            "vi_full": vi_full,
            "field_bytes": field_bytes,
            "vi_bytes": vi_bytes,
            "free_bytes": field_bytes - vi_bytes,
            "action": "EXPORT",
            "note": "Batch 19 direct vi_full exact-offset lock; historical 0.6.14.1 keys excluded",
        })
        auto_override_rows.append({
            "file": key[0],
            "offset_hex": key[1],
            "vi_accented": vi_full,
            "category": "batch19-auto-exact",
            "note": "Generated from fitting Translation Master vi_full; token-safe; historical 0.6.14.1 locks preserved",
        })

    out_dir = args.out_dir.expanduser().resolve()
    write_csv(
        out_dir / f"GaiaMaster_{VERSION}_RESIDUAL_ALPHA.csv",
        ("master_part", "file", "offset_hex", "japanese", "vi_game_current", "status", "note"),
        residual_rows,
    )
    write_csv(
        out_dir / f"GaiaMaster_{VERSION}_FIT_PRESSURE.csv",
        (
            "master_part", "file", "offset_hex", "japanese", "field_bytes",
            "candidate", "candidate_bytes", "over_bytes", "candidate_source",
            "tokens", "vi_game_current",
        ),
        sorted(pressure_rows, key=lambda r: (-int(r["over_bytes"]), r["file"], int(r["offset_hex"], 16))),
    )
    write_csv(
        out_dir / f"GaiaMaster_{VERSION}_EXACT_OFFSET_LOCKS.csv",
        (
            "master_part", "file", "offset_hex", "japanese", "vi_full",
            "field_bytes", "vi_bytes", "free_bytes", "action", "note",
        ),
        sorted(exact_rows, key=lambda r: (r["file"], int(r["offset_hex"], 16))),
    )
    write_csv(
        out_dir / f"GaiaMaster_{VERSION}_AUTO_EXACT_OVERRIDES.csv",
        ("file", "offset_hex", "vi_accented", "category", "note"),
        sorted(auto_override_rows, key=lambda r: (r["file"], int(r["offset_hex"], 16))),
    )

    summary = [
        f"GAIA MASTER {VERSION} BATCH 19 REPORT COMPILER",
        "=" * 72,
        f"Translation Master rows : {len(all_rows)}",
        f"Semantic map entries    : {len(semantic)}",
        f"STYLE map entries       : {len(style)}",
        f"Consensus JP entries    : {len(consensus_jp)}",
        f"Consensus FB entries    : {len(consensus_fallback)}",
        f"Rows with meaning       : {meaning_count}",
        f"Rows with fitting cand. : {fit_count}",
        f"RESIDUAL_ALPHA rows     : {len(residual_rows)}",
        f"FIT_PRESSURE rows       : {len(pressure_rows)}",
        f"EXACT_OFFSET locks      : {len(exact_rows)}",
        f"Historical protected    : {historical_protected}",
        f"Token-rejected cand.    : {token_rejected}",
        "",
        "SAFETY:",
        "- report-only; no ROM/BIN/CUE/BDP/font modification",
        "- frozen codepage/font architecture untouched",
        "- historical 0.6.14.1 exact locks never overwritten",
        "- AUTO_EXACT_OVERRIDES contains direct fitting vi_full only",
        "",
        f"Output: {out_dir}",
    ]
    (out_dir / f"GaiaMaster_{VERSION}_REPORT_SUMMARY.txt").write_text(
        "\n".join(summary) + "\n", encoding="utf-8"
    )

    print("\n".join(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
