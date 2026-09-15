#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static CI validator for Gaia Master B51R1.

No ROM/BIN is required. This validator proves:
- canonical B50 restore/hash/schema is intact;
- the known raw B50 frozen-codepage debt is exactly 19 chars / 64 rows;
- the 64-row B51R1 text-only correction overlay covers that debt one-for-one;
- corrected B50 candidates are all production-encodable with frozen 60 glyphs;
- corrected rows do not expand the approved B50 byte budget;
- B40/B43/intro overlap guards and legacy/master static contracts still pass.

It does NOT prove CLEAN source identity, BDP owner identity against the real ROM,
raw-sector output, a real build, or runtime behavior.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
OUT = ROOT / "translation" / "source_layer" / "checkpoint_B51" / "STATIC_VALIDATION.txt"
EXPECTED_RAW_UNSUPPORTED_CHARS = 19
EXPECTED_RAW_BAD_ROWS = 64

sys.path.insert(0, str(TOOLS))
import build_gaia_b51_guarded_exact_overlay as core  # noqa: E402
import build_gaia_b51r1_guarded_exact_overlay as r1  # noqa: E402


def unsupported_chars(text: str, cmap: dict[str, int]):
    bad = []
    i = 0
    while i < len(text):
        m = core.CONTROL_RE.match(text, i)
        if m:
            i = m.end()
            continue
        ch = text[i]
        if ch in cmap or ch == " " or 0x21 <= ord(ch) <= 0x7E:
            i += 1
            continue
        try:
            ch.encode("cp932")
        except UnicodeEncodeError:
            bad.append(ch)
        i += 1
    return bad


def raw_charset_census(fake_cmap: dict[str, int]):
    fields, raw_rows = core.read_csv(core.RESTORED)
    if fields != core.EXPECTED_B50_HEADER:
        raise RuntimeError(f"B50 schema drift:\nwant={core.EXPECTED_B50_HEADER}\ngot ={fields}")
    if len(raw_rows) != core.B50_ROWS:
        raise RuntimeError(f"B50 row gate: {len(raw_rows)} != {core.B50_ROWS}")

    unsupported = defaultdict(list)
    bad_rows = {}
    raw_by_key = {}
    for line, row in enumerate(raw_rows, 2):
        name = (row.get("file") or "").strip()
        off = core.parse_int(row.get("offset_hex") or "", f"B50 line {line} offset")
        key = (name, off)
        if key in raw_by_key:
            raise RuntimeError(f"B50 duplicate key during census: {key}")
        raw_by_key[key] = row
        text = row.get("vi_runtime_candidate") or ""
        bad = unsupported_chars(text, fake_cmap)
        if not bad:
            continue
        bad_rows[key] = (line, text, tuple(sorted(set(bad), key=ord)))
        for ch in bad:
            unsupported[ch].append((line, name, off, text))
    return unsupported, bad_rows, raw_by_key


def correction_coverage_gate(bad_rows, raw_by_key):
    corrections = r1.load_corrections()
    bad_keys = set(bad_rows)
    correction_keys = set(corrections)
    if bad_keys != correction_keys:
        missing = sorted(bad_keys - correction_keys)
        extra = sorted(correction_keys - bad_keys)
        raise RuntimeError(
            f"B51R1 correction coverage mismatch: missing={missing[:8]} extra={extra[:8]}"
        )
    for key, (old, new) in corrections.items():
        raw = raw_by_key[key]
        got = raw.get("vi_runtime_candidate") or ""
        if got != old:
            raise RuntimeError(f"Correction old-candidate mismatch {key}: {got!r} != {old!r}")
        if got == new:
            raise RuntimeError(f"Correction is a no-op: {key}")
    return corrections


def write_report(lines):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main() -> int:
    restored = core.restore_b50()
    raw = restored.read_bytes()
    got_sha = hashlib.sha256(raw).hexdigest()
    if len(raw) != core.B50_RAW_SIZE:
        raise RuntimeError(f"B50 restored size {len(raw)} != {core.B50_RAW_SIZE}")
    if got_sha != core.B50_RAW_SHA256:
        raise RuntimeError(f"B50 restored SHA256 {got_sha} != {core.B50_RAW_SHA256}")

    # Static surrogate: every frozen custom glyph occupies two runtime bytes.
    fake_cmap = {ch: 0x889F + i for i, ch in enumerate(core.legacy.CUSTOM_CHARS)}
    if len(fake_cmap) != 60:
        raise RuntimeError(f"Frozen custom-char count {len(fake_cmap)} != 60")

    unsupported, bad_rows, raw_by_key = raw_charset_census(fake_cmap)
    if len(unsupported) != EXPECTED_RAW_UNSUPPORTED_CHARS:
        raise RuntimeError(
            f"Raw B50 unsupported-char census drift: {len(unsupported)} != {EXPECTED_RAW_UNSUPPORTED_CHARS}"
        )
    if len(bad_rows) != EXPECTED_RAW_BAD_ROWS:
        raise RuntimeError(
            f"Raw B50 bad-row census drift: {len(bad_rows)} != {EXPECTED_RAW_BAD_ROWS}"
        )

    corrections = correction_coverage_gate(bad_rows, raw_by_key)
    rows = r1.load_b50_r1(fake_cmap)

    # load_b50_r1() already encodes every corrected candidate. Make the closure
    # explicit so a future encoder change cannot silently broaden the charset.
    corrected_bad = []
    for p in rows:
        bad = unsupported_chars(p.vi, fake_cmap)
        if bad:
            corrected_bad.append((p.file, p.offset, p.vi, bad))
    if corrected_bad:
        raise RuntimeError(f"B51R1 still has unsupported runtime chars: {corrected_bad[:8]}")

    b40, b43, intro, eq, counts, masters = r1.static_contracts_r1(rows, fake_cmap)
    eq40, eq43, eqi = eq
    direct = sum(p.production_status == "DIRECT_FIT_VI_FULL" for p in rows)
    compact = len(rows) - direct

    gates = [
        (len(rows), core.B50_ROWS, "B50 rows"),
        (len(corrections), r1.EXPECTED_CORRECTIONS, "B51R1 corrections"),
        (direct, core.B50_DIRECT, "B50 direct"),
        (compact, core.B50_COMPACT, "B50 compact"),
        (len(b40), core.B40_ROWS, "B40 rows"),
        (len(b43), core.B43_ROWS, "B43 rows"),
        (len(intro), core.INTRO_ROWS, "Intro rows"),
        (counts["legacy"], core.LEGACY_KEYS, "Legacy keys"),
        (masters, core.MASTER_ROWS, "Master rows"),
    ]
    for got_n, want_n, label in gates:
        if got_n != want_n:
            raise RuntimeError(f"{label}: {got_n} != {want_n}")

    lines = [
        "GAIA MASTER B51R1 STATIC CI VALIDATION",
        "=" * 72,
        "B51/B51R1 module import + syntax       : PASS",
        f"B50 restored SHA256                   : {got_sha}",
        f"B50 restored size                     : {len(raw)}/{core.B50_RAW_SIZE}",
        f"B50 exact candidate rows              : {len(rows)}/{core.B50_ROWS}",
        f"Raw B50 unsupported characters        : {len(unsupported)}/{EXPECTED_RAW_UNSUPPORTED_CHARS} (known debt)",
        f"Raw B50 rows needing charset cleanup  : {len(bad_rows)}/{EXPECTED_RAW_BAD_ROWS} (known debt)",
        f"B51R1 exact-key text corrections      : {len(corrections)}/{r1.EXPECTED_CORRECTIONS}",
        "Corrected frozen-60 charset gate       : PASS (0 unsupported rows)",
        "B50 canonical checkpoint mutated       : NO",
        "New font glyphs added                  : 0",
        f"B50 direct vi_full                    : {direct}/{core.B50_DIRECT}",
        f"B50 compact candidates                : {compact}/{core.B50_COMPACT}",
        f"B40 protected manifest                : {len(b40)}/{core.B40_ROWS}",
        f"B43 protected manifest                : {len(b43)}/{core.B43_ROWS}",
        f"Combined historical exact manifests   : {len(b40)+len(b43)}/{core.B40_ROWS+core.B43_ROWS}",
        f"Intro protected manifest              : {len(intro)}/{core.INTRO_ROWS}",
        f"Equivalent B51R1/B40 overlaps         : {eq40}",
        f"Equivalent B51R1/B43 overlaps         : {eq43}",
        f"Equivalent B51R1/Intro overlaps       : {eqi}",
        f"Legacy Alpha static contract          : {counts['legacy']}/{core.LEGACY_KEYS}",
        f"Translation Master row contract       : {masters}/{core.MASTER_ROWS}",
        "Duplicate/overlap/byte/token gates     : PASS",
        "ROM/font/pointer modified              : NO",
        "CLEAN source identity tested           : NO (requires real CLEAN BIN)",
        "Build/output bytes tested              : NO (requires runtime base BIN)",
        "Runtime PASS claim                     : NO",
        "",
        "RESULT: B51R1 STATIC CI PASS",
    ]
    write_report(lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
