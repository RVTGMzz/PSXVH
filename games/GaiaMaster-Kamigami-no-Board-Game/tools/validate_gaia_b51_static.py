#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static CI validator for Gaia Master B51.

No ROM/BIN is required. This validator imports the committed B51 tool, restores
B50 from its archived parts, audits the whole B50 runtime charset against the
frozen 60-glyph codepage, then runs the B50 schema/byte/overlap and historical
static contracts when charset-safe.

It does NOT prove CLEAN source identity, BDP ownership against the real ROM,
raw-sector writing, build output, or runtime behavior.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
OUT = ROOT / "translation" / "source_layer" / "checkpoint_B51" / "STATIC_VALIDATION.txt"

sys.path.insert(0, str(TOOLS))
import build_gaia_b51_guarded_exact_overlay as b51  # noqa: E402


def charset_census(fake_cmap: dict[str, int]):
    fields, raw_rows = b51.read_csv(b51.RESTORED)
    if fields != b51.EXPECTED_B50_HEADER:
        raise RuntimeError(f"B50 schema drift:\nwant={b51.EXPECTED_B50_HEADER}\ngot ={fields}")
    if len(raw_rows) != b51.B50_ROWS:
        raise RuntimeError(f"B50 row gate: {len(raw_rows)} != {b51.B50_ROWS}")

    unsupported = defaultdict(list)
    rows_bad = []
    for line, r in enumerate(raw_rows, 2):
        text = r.get("vi_runtime_candidate") or ""
        i = 0
        bad_here = []
        while i < len(text):
            m = b51.CONTROL_RE.match(text, i)
            if m:
                i = m.end()
                continue
            ch = text[i]
            if ch in fake_cmap or ch == " " or 0x21 <= ord(ch) <= 0x7E:
                i += 1
                continue
            try:
                ch.encode("cp932")
            except UnicodeEncodeError:
                unsupported[ch].append((line, r.get("file") or "", r.get("offset_hex") or "", text))
                bad_here.append(ch)
            i += 1
        if bad_here:
            rows_bad.append((line, r.get("file") or "", r.get("offset_hex") or "", text, "".join(sorted(set(bad_here)))))
    return unsupported, rows_bad


def write_report(lines):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main() -> int:
    restored = b51.restore_b50()
    raw = restored.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if len(raw) != b51.B50_RAW_SIZE:
        raise RuntimeError(f"B50 restored size {len(raw)} != {b51.B50_RAW_SIZE}")
    if got != b51.B50_RAW_SHA256:
        raise RuntimeError(f"B50 restored SHA256 {got} != {b51.B50_RAW_SHA256}")

    # Static-only surrogate. Any frozen custom glyph remains two runtime bytes.
    fake_cmap = {ch: 0x889F + i for i, ch in enumerate(b51.legacy.CUSTOM_CHARS)}
    if len(fake_cmap) != 60:
        raise RuntimeError(f"Frozen custom-char count {len(fake_cmap)} != 60")

    unsupported, bad_rows = charset_census(fake_cmap)
    if unsupported:
        lines = [
            "GAIA MASTER B51 STATIC CI VALIDATION",
            "=" * 72,
            "B51 module import / Python syntax      : PASS",
            f"B50 restored SHA256                   : {got}",
            f"B50 restored size                     : {len(raw)}/{b51.B50_RAW_SIZE}",
            f"B50 exact candidate rows              : {b51.B50_ROWS}/{b51.B50_ROWS}",
            f"Frozen custom glyphs                  : {len(fake_cmap)}/60",
            f"Unsupported runtime characters        : {len(unsupported)}",
            f"Rows containing unsupported chars     : {len(bad_rows)}",
            "Runtime charset gate                   : FAIL",
            "ROM/font/pointer modified              : NO",
            "Runtime PASS claim                     : NO",
            "",
            "UNSUPPORTED CHARACTER CENSUS",
            "-" * 72,
        ]
        for ch in sorted(unsupported, key=ord):
            hits = unsupported[ch]
            lines.append(f"U+{ord(ch):04X} {ch!r} occurrences={len(hits)}")
            for line, file_name, off, text in hits[:20]:
                lines.append(f"  line={line} {file_name}+{off}  {text!r}")
            if len(hits) > 20:
                lines.append(f"  ... {len(hits)-20} more")
        lines += ["", "BAD ROWS", "-" * 72]
        for line, file_name, off, text, chars in bad_rows:
            lines.append(f"line={line} {file_name}+{off} unsupported={chars!r} text={text!r}")
        lines += [
            "",
            "RESULT: B51 STATIC CI FAIL - B50 CONTAINS GLYPHS OUTSIDE FROZEN CODEPAGE",
            "Do not add font glyphs automatically. Fix wording/candidates in a later B51 text-only correction layer.",
        ]
        write_report(lines)
        return 4

    rows = b51.load_b50(fake_cmap)
    b40, b43, intro, eq, counts, masters = b51.static_contracts(rows, fake_cmap)
    eq40, eq43, eqi = eq

    direct = sum(p.production_status == "DIRECT_FIT_VI_FULL" for p in rows)
    compact = len(rows) - direct
    gates = [
        (len(rows), b51.B50_ROWS, "B50 rows"),
        (direct, b51.B50_DIRECT, "B50 direct"),
        (compact, b51.B50_COMPACT, "B50 compact"),
        (len(b40), b51.B40_ROWS, "B40 rows"),
        (len(b43), b51.B43_ROWS, "B43 rows"),
        (len(intro), b51.INTRO_ROWS, "Intro rows"),
        (counts["legacy"], b51.LEGACY_KEYS, "Legacy keys"),
        (masters, b51.MASTER_ROWS, "Master rows"),
    ]
    for got_n, want_n, label in gates:
        if got_n != want_n:
            raise RuntimeError(f"{label}: {got_n} != {want_n}")

    lines = [
        "GAIA MASTER B51 STATIC CI VALIDATION",
        "=" * 72,
        "B51 module import / Python syntax      : PASS",
        f"B50 restored SHA256                   : {got}",
        f"B50 restored size                     : {len(raw)}/{b51.B50_RAW_SIZE}",
        f"B50 exact candidate rows              : {len(rows)}/{b51.B50_ROWS}",
        f"B50 direct vi_full                    : {direct}/{b51.B50_DIRECT}",
        f"B50 compact candidates                : {compact}/{b51.B50_COMPACT}",
        "Runtime charset / frozen-60 gate        : PASS",
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
    write_report(lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
