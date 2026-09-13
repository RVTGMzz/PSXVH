#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaia Master 0.6.13.0
Compact Japanese Reduction Batch 4 + lowercase ă glyph hotfix v2.

This wrapper intentionally keeps 0.6.12.0 as the inner production build so:
- 397/397 legacy coverage remains mandatory;
- Batch 2 + Batch 3 translation work remains intact;
- only curated compact additions are layered on top;
- lowercase ă is corrected after the inner build.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import importlib.util
from pathlib import Path
import re
import subprocess
import sys

VERSION = "0.6.13.0"
CLEAN_BIN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TR = ROOT / "translation"

INNER_BUILDER = TOOLS / "build_gaia_06120_big_translation_b3.py"
MAPPING_HELPER = TOOLS / "build_gaia_0653_mapping_only.py"

COMPACT_OVR = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv"
NEW_DYNAMIC = TR / "DYNAMIC_LITERAL_OVERRIDES_0.6.13.0.csv"
INNER_DYNAMIC = TR / "DYNAMIC_LITERAL_OVERRIDES_0.6.12.0.csv"
MASTER_PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]

FROZEN_CUSTOM_ORDER = "àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ"
FROZEN_CUSTOM = set(FROZEN_CUSTOM_ORDER)
RAW_TOKEN_RE = re.compile(r"%(?:[-+0-9.#]*[A-Za-z])|/[Vv]")

def die(msg: str) -> None:
    print(f"[BLOCKED] {msg}")
    raise SystemExit(1)

def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def norm_off(s: str) -> str:
    return hex(int(str(s).strip(), 0)).lower()

def runtime_len_estimate(text: str) -> int:
    n = 0
    pos = 0
    for m in RAW_TOKEN_RE.finditer(text):
        n += (m.start() - pos) * 2
        n += len(m.group(0).encode("ascii"))
        pos = m.end()
    n += (len(text) - pos) * 2
    return n

def validate_text(text: str, where: str) -> None:
    for ch in text:
        if ord(ch) < 128:
            continue
        try:
            ch.encode("cp932")
            continue
        except UnicodeEncodeError:
            pass
        if ch not in FROZEN_CUSTOM:
            die(f"{where}: unsupported custom glyph {ch!r} U+{ord(ch):04X}")

def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            die(f"No CSV header: {path}")
        return r.fieldnames, list(r)

def write_csv(path: Path, fields, rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def snapshot(d: Path):
    out = {}
    for p in d.iterdir():
        if p.is_file():
            try:
                st = p.stat()
                out[p.name] = (st.st_mtime_ns, st.st_size)
            except OSError:
                pass
    return out

def changed(d: Path, before):
    out = []
    for p in d.iterdir():
        if not p.is_file():
            continue
        try:
            st = p.stat()
        except OSError:
            continue
        old = before.get(p.name)
        if old is None or old != (st.st_mtime_ns, st.st_size):
            out.append(p)
    return out

def load_mapping_helper():
    spec = importlib.util.spec_from_file_location("gaia_mapping_helper", MAPPING_HELPER)
    if spec is None or spec.loader is None:
        die("Cannot import mapping helper")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def patch_breve_a_v2(output_bin: Path, clean_bin: Path, m):
    """
    0.6.12 proved the correct slot was being patched, but it reused the dark
    shadow palette index as the new breve fill and left part of the old
    shadow in row 2. This v2:
    - derives native fill from the glyph histogram, excluding shadow index 7;
    - clears old mark pixels plus the stale row-2 shadow;
    - draws a LOWER shallow cup in the bright fill;
    - draws the dark shadow one pixel down/right.
    """
    with clean_bin.open("rb") as rf:
        clean_slps = m.read_iso_file(rf, m.SLPS_EXTENT, m.SLPS_SIZE)
        clean_prg = m.read_iso_file(rf, m.PRG_EXTENT, m.PRG_SIZE)

    with output_bin.open("rb") as rf:
        out_slps = m.read_iso_file(rf, m.SLPS_EXTENT, m.SLPS_SIZE)

    max_idx = max(code & 0x7FFF for code in m.valid_codes())
    map_end = m.MAPPING_OFF + (max_idx + 1) * 2
    scan_slps = b"".join((
        bytes(clean_slps[:m.ATLAS_OFF]),
        bytes(clean_slps[m.ATLAS_OFF + m.ATLAS_GLYPHS*m.GLYPH_BYTES:m.MAPPING_OFF]),
        bytes(clean_slps[map_end:]),
    ))

    safe_codes = []
    for code in m.valid_codes():
        if code < 0x889F:
            continue
        pair = bytes([(code >> 8) & 0xFF, code & 0xFF])
        try:
            pair.decode("cp932")
        except Exception:
            continue
        if m.count_pair(clean_prg, pair) + m.count_pair(scan_slps, pair) == 0:
            safe_codes.append(code)
            if len(safe_codes) == len(FROZEN_CUSTOM_ORDER):
                break

    if len(safe_codes) != len(FROZEN_CUSTOM_ORDER):
        die(f"Could not reconstruct frozen custom codes: {len(safe_codes)}")

    idx = FROZEN_CUSTOM_ORDER.index("ă")
    code = safe_codes[idx]
    slot = m.mapping_value(out_slps, code)
    if slot is None or not (0 <= slot < m.ATLAS_GLYPHS):
        die(f"ă mapping invalid: code {code:04X} -> {slot}")

    goff = m.ATLAS_OFF + slot*m.GLYPH_BYTES
    raw = bytearray(out_slps[goff:goff+m.GLYPH_BYTES])
    if len(raw) != m.GLYPH_BYTES:
        die("ă glyph read failed")

    grid = [[0]*12 for _ in range(12)]
    k = 0
    for y in range(12):
        for x in range(0, 12, 2):
            b = raw[k]
            k += 1
            grid[y][x] = b & 0xF
            grid[y][x+1] = (b >> 4) & 0xF

    hist = Counter(
        grid[y][x]
        for y in range(3, 12)
        for x in range(12)
        if grid[y][x] != 0
    )
    if not hist:
        die("ă glyph body unexpectedly empty")

    shadow = 7 if hist.get(7, 0) else None
    fill_candidates = [(count, idx) for idx, count in hist.items() if idx != 0 and idx != shadow]
    if not fill_candidates:
        die(f"Could not derive bright fill palette; hist={dict(hist)}")
    fill_candidates.sort(reverse=True)
    fill = fill_candidates[0][1]
    if shadow is None:
        other = [(count, idx) for idx, count in hist.items() if idx != fill]
        other.sort(reverse=True)
        shadow = other[0][1] if other else fill

    body_pts = [
        (x, y)
        for y in range(3, 12)
        for x in range(12)
        if grid[y][x] != 0
    ]
    x0 = min(x for x, y in body_pts)
    x1 = max(x for x, y in body_pts)
    cx = (x0 + x1) // 2

    lo = max(0, cx - 3)
    hi = min(11, cx + 3)
    for y in (0, 1):
        for x in range(lo, hi + 1):
            grid[y][x] = 0
    for x in range(lo, hi + 1):
        if grid[2][x] == shadow:
            grid[2][x] = 0

    pts = [
        (max(0, cx-2), 1),
        (min(11, cx+2), 1),
        (max(0, cx-1), 2),
        (cx, 2),
        (min(11, cx+1), 2),
    ]

    if shadow != fill:
        for x, y in pts:
            sx, sy = x + 1, y + 1
            if 0 <= sx < 12 and 0 <= sy < 12:
                grid[sy][sx] = shadow
    for x, y in pts:
        grid[y][x] = fill

    newraw = bytearray()
    for row in grid:
        for x in range(0, 12, 2):
            newraw.append((row[x] & 0xF) | ((row[x+1] & 0xF) << 4))

    patched_slps = bytearray(out_slps)
    patched_slps[goff:goff+m.GLYPH_BYTES] = newraw

    changed_sectors = set()
    with output_bin.open("r+b") as wf:
        m.write_changed_iso_file(
            wf, m.SLPS_EXTENT, bytes(out_slps), bytes(patched_slps), changed_sectors
        )
        for sec in sorted(changed_sectors):
            wf.seek(sec*2352)
            secraw = wf.read(2352)
            wf.seek(sec*2352)
            wf.write(m.regen_sector(secraw))

    return {
        "char": "ă",
        "code": f"{code:04X}",
        "slot": slot,
        "atlas_off": hex(goff),
        "fill": fill,
        "shadow": shadow,
        "sectors": len(changed_sectors),
    }

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: build_gaia_06130_translation_b4.py CLEAN_GAME.bin")
        return 2

    clean_bin = Path(sys.argv[1]).expanduser().resolve()
    if not clean_bin.is_file():
        die(f"Input does not exist: {clean_bin}")

    got_sha = sha1_file(clean_bin).lower()
    if got_sha != CLEAN_BIN_SHA1:
        die(f"Need CLEAN Japan BIN SHA1 {CLEAN_BIN_SHA1}; got {got_sha}")

    required = [INNER_BUILDER, MAPPING_HELPER, COMPACT_OVR, NEW_DYNAMIC, INNER_DYNAMIC, *MASTER_PARTS]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        die("Missing source files:\n  " + "\n  ".join(missing))

    part_data = {}
    key_to_row = {}
    for path in MASTER_PARTS:
        fields, rows = read_csv(path)
        part_data[path] = (fields, rows)
        for r in rows:
            key = (r["file"].strip(), norm_off(r["offset_hex"]))
            key_to_row[key] = r

    _, compact_rows = read_csv(COMPACT_OVR)
    applied = []
    skipped_long = []
    missing_keys = []
    for o in compact_rows:
        key = (o["file"].strip(), norm_off(o["offset_hex"]))
        r = key_to_row.get(key)
        if not r:
            missing_keys.append(key)
            continue
        text = o["vi_accented"].strip()
        validate_text(text, f"{COMPACT_OVR.name}:{key}")
        try:
            old_len = len(r["japanese"].encode("cp932"))
        except Exception:
            continue
        new_len = runtime_len_estimate(text)
        if new_len <= old_len:
            r["vi_full"] = text
            applied.append((key, text, new_len, old_len))
        else:
            skipped_long.append((key, text, new_len, old_len))

    mutable = [INNER_DYNAMIC, *MASTER_PARTS]
    backups = {p: p.read_bytes() for p in mutable}

    out_dir = clean_bin.parent
    before = snapshot(out_dir)

    try:
        INNER_DYNAMIC.write_bytes(NEW_DYNAMIC.read_bytes())
        for path, (fields, rows) in part_data.items():
            write_csv(path, fields, rows)

        print("=" * 84)
        print("GAIA MASTER 0.6.13.0 - COMPACT JAPANESE REDUCTION BATCH 4")
        print("=" * 84)
        print(f"Compact candidates : {len(compact_rows)}")
        print(f"Applied and fit     : {len(applied)}")
        print(f"Too long skipped   : {len(skipped_long)}")
        print(f"Missing keys        : {len(missing_keys)}")
        print("Dynamic map         : 0.6.13.0 expanded names/items")
        print("Font hotfix         : lowercase ă v2 after inner build")
        print()

        cp = subprocess.run(
            [sys.executable, str(INNER_BUILDER), str(clean_bin)],
            cwd=str(TOOLS),
            check=False,
        )
        if cp.returncode != 0:
            die(f"Inner 0.6.12.0 builder failed with exit code {cp.returncode}")
    finally:
        for p, data in backups.items():
            try:
                p.write_bytes(data)
            except Exception as e:
                print(f"[CRITICAL] Restore failed {p}: {e}", file=sys.stderr)

    after_inner = changed(out_dir, before)
    bins = [p for p in after_inner if p.suffix.lower() == ".bin" and p.resolve() != clean_bin]
    bins.sort(key=lambda p: p.stat().st_mtime_ns, reverse=True)
    if not bins:
        die("Inner build returned success but no new BIN was found")
    inner_bin = bins[0]

    m = load_mapping_helper()
    breve = patch_breve_a_v2(inner_bin, clean_bin, m)

    current = changed(out_dir, before)
    for p in sorted(current, key=lambda x: len(x.name), reverse=True):
        if not p.exists() or p.resolve() == clean_bin:
            continue
        new_name = (
            p.name
            .replace("0.6.12.0", "0.6.13.0")
            .replace("06120", "06130")
            .replace("BATCH3", "BATCH4")
        )
        if new_name == p.name:
            continue
        q = p.with_name(new_name)
        if q.exists():
            q.unlink()
        p.rename(q)

    for p in out_dir.glob("*0.6.13.0*.cue"):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            txt = txt.replace("0.6.12.0", "0.6.13.0").replace("06120", "06130")
            p.write_text(txt, encoding="utf-8")
        except Exception as e:
            print(f"[WARN] CUE rewrite failed: {p.name}: {e}")

    report = out_dir / "GaiaMaster_0.6.13.0_BATCH4_REPORT.txt"
    lines = [
        "GAIA MASTER 0.6.13.0 - COMPACT JAPANESE REDUCTION BATCH 4",
        "=" * 84,
        f"Input CLEAN SHA1: {got_sha}",
        "Inner production path: 0.6.12.0 -> 0.6.11.0 -> exact 397/397 legacy gate",
        "",
        f"Compact candidates: {len(compact_rows)}",
        f"Applied and fit: {len(applied)}",
        f"Too-long candidates skipped safely: {len(skipped_long)}",
        f"Missing compact keys: {len(missing_keys)}",
        "",
        "Dynamic Japanese reduction:",
        f"- expanded literals: {sum(1 for _ in read_csv(NEW_DYNAMIC)[1])}",
        "- character names + weapon/card names + some board/location labels",
        "",
        "Lowercase ă hotfix v2:",
        f"- code={breve['code']} slot={breve['slot']} atlas={breve['atlas_off']}",
        f"- bright fill index={breve['fill']} shadow index={breve['shadow']}",
        "- stale row-2 shadow removed",
        "- breve redrawn one row lower as a shallow cup with native shadow",
        f"- changed sectors={breve['sectors']}",
        "",
        "RUNTIME TEST REQUIRED",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print("[OK] 0.6.13.0 Batch 4 completed")
    print("Report:", report.name)
    for p in sorted(changed(out_dir, before)):
        if p.exists():
            print(" ", p.name)
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("[ERROR]", repr(e))
        raise SystemExit(9)
