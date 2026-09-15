#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static CI validator for Gaia Master B51.

This deliberately requires no ROM/BIN. It proves that the committed B51 tool can
be imported, reconstructs the canonical B50 checkpoint, validates its schema and
all 1229 candidate byte budgets with a synthetic two-byte Vietnamese codepage,
and re-runs the committed historical overlap/static contracts.

It does NOT prove CLEAN source identity, BDP ownership against the real ROM, raw
sector writing, or runtime behavior. Those remain B51 dry-run/build/runtime gates.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
OUT = ROOT / "translation" / "source_layer" / "checkpoint_B51" / "STATIC_VALIDATION.txt"

sys.path.insert(0, str(TOOLS))
import build_gaia_b51_guarded_exact_overlay as b51  # noqa: E402


def main() -> int:
    restored = b51.restore_b50()
    raw = restored.read_bytes()
    if len(raw) != b51.B50_RAW_SIZE:
        raise RuntimeError(f"B50 restored size {len(raw)} != {b51.B50_RAW_SIZE}")
    got = hashlib.sha256(raw).hexdigest()
    if got != b51.B50_RAW_SHA256:
        raise RuntimeError(f"B50 restored SHA256 {got} != {b51.B50_RAW_SHA256}")

    # Static-only surrogate. B51's runtime encoder only needs a deterministic
    # two-byte code for each frozen Vietnamese glyph to validate encoded lengths.
    fake_cmap = {
        ch: 0x889F + i
        for i, ch in enumerate(b51.legacy.CUSTOM_CHARS)
    }
    if len(fake_cmap) != 60:
        raise RuntimeError(f"Frozen custom-char count {len(fake_cmap)} != 60")

    rows = b51.load_b50(fake_cmap)
    b40, b43, intro, eq, counts, masters = b51.static_contracts(rows, fake_cmap)
    eq40, eq43, eqi = eq

    if len(rows) != b51.B50_ROWS:
        raise RuntimeError(f"B50 rows {len(rows)} != {b51.B50_ROWS}")
    if len(b40) != b51.B40_ROWS:
        raise RuntimeError(f"B40 rows {len(b40)} != {b51.B40_ROWS}")
    if len(b43) != b51.B43_ROWS:
        raise RuntimeError(f"B43 rows {len(b43)} != {b51.B43_ROWS}")
    if len(intro) != b51.INTRO_ROWS:
        raise RuntimeError(f"Intro rows {len(intro)} != {b51.INTRO_ROWS}")
    if counts["legacy"] != b51.LEGACY_KEYS:
        raise RuntimeError(f"Legacy static keys {counts['legacy']} != {b51.LEGACY_KEYS}")
    if masters != b51.MASTER_ROWS:
        raise RuntimeError(f"Master rows {masters} != {b51.MASTER_ROWS}")

    direct = sum(p.production_status == "DIRECT_FIT_VI_FULL" for p in rows)
    compact = len(rows) - direct
    if direct != b51.B50_DIRECT or compact != b51.B50_COMPACT:
        raise RuntimeError(
            f"B50 production split {direct}/{compact} != "
            f"{b51.B50_DIRECT}/{b51.B50_COMPACT}"
        )

    lines = [
        "GAIA MASTER B51 STATIC CI VALIDATION",
        "=" * 72,
        f"B51 module import / Python syntax      : PASS",
        f"B50 restored SHA256                   : {got}",
        f"B50 restored size                     : {len(raw)}/{b51.B50_RAW_SIZE}",
        f"B50 exact candidate rows              : {len(rows)}/{b51.B50_ROWS}",
        f"B50 direct vi_full                    : {direct}/{b51.B50_DIRECT}",
        f"B50 compact candidates                : {compact}/{b51.B50_COMPACT}",
        f"B40 protected manifest                : {len(b40)}/{b51.B40_ROWS}",
        f"B43 protected manifest                : {len(b43)}/{b51.B43_ROWS}",
        f"Combined historical exact manifests   : {len(b40)+len(b43)}/{b51.B40_ROWS+b51.B43_ROWS}",
        f"Intro protected manifest              : {len(intro)}/{b51.INTRO_ROWS}",
        f"Equivalent B50/B40 overlaps           : {eq40}",
        f"Equivalent B50/B43 overlaps           : {eq43}",
        f"Equivalent B50/Intro overlaps         : {eqi}",
        f"Legacy Alpha static contract          : {counts['legacy']}/{b51.LEGACY_KEYS}",
        f"Translation Master row contract       : {masters}/{b51.MASTER_ROWS}",
        "Duplicate/overlap/byte/token gates     : PASS",
        "ROM/font/pointer modified              : NO",
        "CLEAN source identity tested           : NO (requires real CLEAN BIN)",
        "Build/output bytes tested              : NO (requires runtime base BIN)",
        "Runtime PASS claim                     : NO",
        "",
        "RESULT: B51 STATIC CI PASS",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
