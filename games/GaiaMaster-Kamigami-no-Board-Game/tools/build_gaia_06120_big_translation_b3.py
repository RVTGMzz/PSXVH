#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaia Master 0.6.12.0
LARGE Gameplay Translation Batch 3 + runtime hotfix wrapper.

Goals:
- keep 0.6.11.0 / exact 397 legacy coverage as the inner production path;
- fix the two intro '=' skeleton leftovers by correcting FRONT_DEMO fallback;
- globalize every proven Batch-2 accent rewrite to every identical old fallback;
- add a large curated fallback->accent map for more gameplay/card/item/event/menu text;
- scan standalone Japanese literals for safe repeated/dynamic occurrences;
- replace compact dynamic names such as ジガー -> Jig;
- hotfix the demonstrated lowercase ă breve shape after the inner build;
- never force a string that exceeds its original fixed field.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
from pathlib import Path
import re
import subprocess
import sys

VERSION = "0.6.12.0"
CLEAN_BIN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TR = ROOT / "translation"

INNER_BUILDER = TOOLS / "build_gaia_06110_hybrid_accent_b2.py"
MAPPING_HELPER = TOOLS / "build_gaia_0653_mapping_only.py"

FRONT_DEMO = TR / "FRONT_DEMO_ADDED_061.csv"
GAMEPLAY_OVR = TR / "GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv"
LIVE_DYNAMIC = TR / "DYNAMIC_LITERAL_OVERRIDES_0.6.11.0.csv"
NEW_DYNAMIC = TR / "DYNAMIC_LITERAL_OVERRIDES_0.6.12.0.csv"
EXTRA_MAP = TR / "BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv"
MASTER_PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]

FILES = {
    "SLPS_020.75": (24, 487424),
    "PRGPACK.BDP": (2679, 1534236),
}

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

def extract_extent(bin_bytes: bytes, extent: int, size: int) -> bytes:
    out = bytearray()
    sectors = (size + 2047) // 2048
    for i in range(sectors):
        raw = (extent + i) * 2352
        user = raw + 24
        if user + 2048 > len(bin_bytes):
            die(f"BIN too short while extracting extent {extent}+{i}")
        need = min(2048, size - len(out))
        out.extend(bin_bytes[user:user+need])
    return bytes(out)

def standalone(data: bytes, off: int, n: int) -> bool:
    before_ok = off == 0 or data[off-1] == 0
    after = off + n
    after_ok = after >= len(data) or data[after] == 0
    return before_ok and after_ok

def find_all(haystack: bytes, needle: bytes):
    pos = 0
    while True:
        p = haystack.find(needle, pos)
        if p < 0:
            return
        yield p
        pos = p + 1

def snapshot(d: Path):
    out = {}
    for p in d.iterdir():
        if p.is_file():
            try:
                s = p.stat()
                out[p.name] = (s.st_mtime_ns, s.st_size)
            except OSError:
                pass
    return out

def changed(d: Path, before):
    out = []
    for p in d.iterdir():
        if not p.is_file():
            continue
        try:
            s = p.stat()
        except OSError:
            continue
        old = before.get(p.name)
        if old is None or old != (s.st_mtime_ns, s.st_size):
            out.append(p)
    return out

def load_mapping_helper():
    spec = importlib.util.spec_from_file_location("gaia_mapping_helper", MAPPING_HELPER)
    if spec is None or spec.loader is None:
        die("Cannot import mapping helper")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def build_global_accent_map(master_rows, gameplay_rows, extra_rows):
    by_key = {
        (r["file"].strip(), norm_off(r["offset_hex"])): r
        for r in master_rows
    }
    mapping = {}
    provenance = {}

    # Reuse all already-curated Batch 2 candidates globally by their old fallback.
    for r in gameplay_rows:
        key = (r["file"].strip(), norm_off(r["offset_hex"]))
        src = by_key.get(key)
        if not src:
            continue
        old = (src.get("vi_game_current") or "").strip()
        target = (r.get("vi_accented") or "").strip()
        if not old or not target:
            continue
        validate_text(target, f"Batch2-global:{key}")
        if old not in mapping or runtime_len_estimate(target) < runtime_len_estimate(mapping[old]):
            mapping[old] = target
            provenance[old] = "Batch2 exemplar"

    # Batch 3 manual expansion wins over exemplar mapping.
    for r in extra_rows:
        old = (r.get("vi_game_current") or "").strip()
        target = (r.get("vi_accented") or "").strip()
        if not old or not target:
            continue
        validate_text(target, f"Batch3-map:{old}")
        mapping[old] = target
        provenance[old] = "Batch3 curated"

    return mapping, provenance

def patch_breve_a(output_bin: Path, clean_bin: Path, m):
    """
    Runtime screenshot proved lowercase ă's breve is upside-down/hat-like.
    Keep the same codepage/slot and only redraw the two mark rows as a cup.
    """
    with clean_bin.open("rb") as rf:
        clean_slps = m.read_iso_file(rf, m.SLPS_EXTENT, m.SLPS_SIZE)
        clean_prg = m.read_iso_file(rf, m.PRG_EXTENT, m.PRG_SIZE)

    with output_bin.open("rb") as rf:
        out_slps = m.read_iso_file(rf, m.SLPS_EXTENT, m.SLPS_SIZE)

    # Reproduce the production custom-code allocator used by the frozen path.
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
            b = raw[k]; k += 1
            grid[y][x] = b & 0xF
            grid[y][x+1] = (b >> 4) & 0xF

    body_pts = [(x,y) for y in range(2,11) for x in range(12) if grid[y][x]]
    if not body_pts:
        die("ă glyph body unexpectedly empty")
    x0 = min(x for x,y in body_pts)
    x1 = max(x for x,y in body_pts)
    cx = (x0+x1)//2

    vals = [grid[y][x] for y in range(2,11) for x in range(12) if grid[y][x]]
    fill = max(vals) if vals else 0xF

    # Erase only the old top mark. Body begins at y=2 in the frozen generator.
    for y in (0,1):
        for x in range(12):
            grid[y][x] = 0

    # Proper breve = shallow cup/smile, opposite of the previous cap/hat.
    for x,y in [
        (max(0,cx-2),0), (min(11,cx+2),0),
        (max(0,cx-1),1), (cx,1), (min(11,cx+1),1),
    ]:
        grid[y][x] = fill

    newraw = bytearray()
    for row in grid:
        for x in range(0,12,2):
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
            rawsec = wf.read(2352)
            wf.seek(sec*2352)
            wf.write(m.regen_sector(rawsec))

    return {
        "char": "ă",
        "code": f"{code:04X}",
        "slot": slot,
        "atlas_off": hex(goff),
        "sectors": len(changed_sectors),
    }

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: build_gaia_06120_big_translation_b3.py CLEAN_GAME.bin")
        return 2

    clean_bin = Path(sys.argv[1]).expanduser().resolve()
    if not clean_bin.is_file():
        die(f"Input does not exist: {clean_bin}")
    got_sha = sha1_file(clean_bin).lower()
    if got_sha != CLEAN_BIN_SHA1:
        die(f"Need CLEAN Japan BIN SHA1 {CLEAN_BIN_SHA1}; got {got_sha}")

    required = [
        INNER_BUILDER, MAPPING_HELPER, FRONT_DEMO, GAMEPLAY_OVR,
        LIVE_DYNAMIC, NEW_DYNAMIC, EXTRA_MAP, *MASTER_PARTS
    ]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        die("Missing source files:\n  " + "\n  ".join(missing))

    all_master = []
    part_data = {}
    for path in MASTER_PARTS:
        fields, rows = read_csv(path)
        part_data[path] = (fields, rows)
        all_master.extend(rows)

    _, gameplay_rows = read_csv(GAMEPLAY_OVR)
    _, extra_rows = read_csv(EXTRA_MAP)
    global_map, provenance = build_global_accent_map(all_master, gameplay_rows, extra_rows)

    promoted = []
    skipped_long = []
    for path, (fields, rows) in part_data.items():
        for r in rows:
            old = (r.get("vi_game_current") or "").strip()
            if not old or old not in global_map:
                continue
            target = global_map[old]
            old_len = len(r["japanese"].encode("cp932"))
            new_len = runtime_len_estimate(target)
            if new_len <= old_len:
                # Prefer new compact accented target when current vi_full is blank
                # or longer than this compact runtime-safe wording.
                current = (r.get("vi_full") or "").strip()
                if not current or runtime_len_estimate(target) <= runtime_len_estimate(current):
                    r["vi_full"] = target
                    promoted.append((r["file"], norm_off(r["offset_hex"]), old, target, provenance[old]))
            else:
                skipped_long.append((r["file"], norm_off(r["offset_hex"]), old, target, new_len, old_len))

    # Front fallback skeleton hotfix. These were the only two '=' front rows.
    front_fields, front_rows = read_csv(FRONT_DEMO)
    front_fixed = 0
    for r in front_rows:
        off = norm_off(r["offset_hex"])
        if off == "0xc00d0":
            r["vi_no_accents"] = "NGUOI CO"
            front_fixed += 1
        elif off == "0xc00e4":
            r["vi_no_accents"] = "THEGIOI BANCO"
            front_fixed += 1
    if front_fixed != 2:
        die(f"Front skeleton hotfix expected 2 rows, got {front_fixed}")

    # Safe repeated/dynamic literal scan from CLEAN data.
    clean_bytes = clean_bin.read_bytes()
    extracted = {name: extract_extent(clean_bytes, ext, size)
                 for name,(ext,size) in FILES.items()}

    # Existing translated rows after global promotion.
    key_to_row = {
        (r["file"].strip(), norm_off(r["offset_hex"])): r
        for rowspec in part_data.values() for r in rowspec[1]
    }

    # New dynamic compact names override any pre-existing dynamic file.
    _, dyn_rows = read_csv(NEW_DYNAMIC)
    literal_candidates = []
    for r in dyn_rows:
        literal_candidates.append((
            r["japanese"],
            r["vi_accented"].strip(),
            (r.get("file_scope") or "AUTO").strip(),
            "dynamic-name",
        ))

    # Also scan standalone occurrences of promoted master literals.
    # Only rows with an accented vi_full that truly fits their source are candidates.
    seen_lit = set((jp,vi,scope) for jp,vi,scope,_ in literal_candidates)
    for rowspec in part_data.values():
        for r in rowspec[1]:
            vi = (r.get("vi_full") or "").strip()
            jp = (r.get("japanese") or "")
            if not vi or not jp:
                continue
            validate_text(vi, f"scan:{r['file']}:{r['offset_hex']}")
            try:
                jp_len = len(jp.encode("cp932"))
            except UnicodeEncodeError:
                continue
            if runtime_len_estimate(vi) > jp_len:
                continue
            tup = (jp,vi,r["file"].strip())
            if tup in seen_lit:
                continue
            seen_lit.add(tup)
            literal_candidates.append((jp,vi,r["file"].strip(),"master-repeat"))

    append_path = MASTER_PARTS[-1]
    append_fields, append_rows = part_data[append_path]
    existing_keys = set(key_to_row)
    injected = []
    ignored = []

    for jp, vi, scope, reason in literal_candidates:
        validate_text(vi, f"literal:{jp}")
        try:
            jp_b = jp.encode("cp932")
        except UnicodeEncodeError:
            ignored.append((jp,vi,"jp-encode"))
            continue
        if runtime_len_estimate(vi) > len(jp_b):
            ignored.append((jp,vi,"too-long"))
            continue
        names = list(FILES) if scope.upper() == "AUTO" else [scope]
        for name in names:
            if name not in extracted:
                continue
            data = extracted[name]
            for off in find_all(data, jp_b):
                if not standalone(data, off, len(jp_b)):
                    continue
                key = (name, hex(off))
                if key in existing_keys:
                    # Existing master row already receives its promoted vi_full.
                    continue
                append_rows.append({
                    "file": name,
                    "offset_hex": hex(off),
                    "japanese": jp,
                    "vi_full": vi,
                    "vi_game_current": "",
                    "status": "BATCH3_REPEAT_SCAN",
                    "note": reason,
                })
                existing_keys.add(key)
                injected.append((key,jp,vi,reason))

    # Back up every repository source we temporarily mutate.
    mutable = [FRONT_DEMO, LIVE_DYNAMIC, *MASTER_PARTS]
    backups = {p: p.read_bytes() for p in mutable}

    out_dir = clean_bin.parent
    before = snapshot(out_dir)

    try:
        write_csv(FRONT_DEMO, front_fields, front_rows)
        LIVE_DYNAMIC.write_bytes(NEW_DYNAMIC.read_bytes())
        for path,(fields,rows) in part_data.items():
            write_csv(path, fields, rows)

        print("="*82)
        print("GAIA MASTER 0.6.12.0 - LARGE GAMEPLAY TRANSLATION BATCH 3")
        print("="*82)
        print(f"Global accent dictionary       : {len(global_map)} fallbacks")
        print(f"Master rows promoted           : {len(promoted)}")
        print(f"Too-long promotions skipped    : {len(skipped_long)}")
        print(f"Standalone repeat rows injected: {len(injected)}")
        print(f"Dynamic names configured       : {len(dyn_rows)}")
        print("Front '=' skeleton rows fixed  : 2")
        print("Font hotfix                    : lowercase ă breve after inner build")
        print()

        cp = subprocess.run(
            [sys.executable, str(INNER_BUILDER), str(clean_bin)],
            cwd=str(TOOLS),
            check=False,
        )
        if cp.returncode != 0:
            die(f"Inner 0.6.11.0 builder failed with exit code {cp.returncode}")

    finally:
        for p,data in backups.items():
            try:
                p.write_bytes(data)
            except Exception as e:
                print(f"[CRITICAL] Restore failed {p}: {e}", file=sys.stderr)

    # Locate the 0.6.11.0 BIN created by the inner builder.
    after_inner = changed(out_dir, before)
    bins = [p for p in after_inner if p.suffix.lower()==".bin" and p.resolve()!=clean_bin]
    bins.sort(key=lambda p: p.stat().st_mtime_ns, reverse=True)
    if not bins:
        die("Inner build returned success but no new BIN was found")
    inner_bin = bins[0]

    m = load_mapping_helper()
    breve_meta = patch_breve_a(inner_bin, clean_bin, m)

    # Rename all new 0.6.11.0 artifacts to 0.6.12.0.
    current = changed(out_dir, before)
    renamed = []
    for p in sorted(current, key=lambda x: len(x.name), reverse=True):
        if not p.exists() or p.resolve()==clean_bin:
            continue
        new_name = p.name.replace("0.6.11.0","0.6.12.0").replace("06110","06120")
        if new_name == p.name:
            continue
        q = p.with_name(new_name)
        if q.exists():
            q.unlink()
        p.rename(q)
        renamed.append((p.name,q.name))

    # Rewrite CUE file references.
    for p in out_dir.glob("*0.6.12.0*.cue"):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            txt = txt.replace("0.6.11.0","0.6.12.0").replace("06110","06120")
            p.write_text(txt, encoding="utf-8")
        except Exception as e:
            print(f"[WARN] CUE rewrite failed: {p.name}: {e}")

    report = out_dir / "GaiaMaster_0.6.12.0_BATCH3_REPORT.txt"
    lines = [
        "GAIA MASTER 0.6.12.0 - LARGE GAMEPLAY TRANSLATION BATCH 3",
        "="*82,
        f"Input CLEAN SHA1: {got_sha}",
        "Inner production path: 0.6.11.0 -> exact 0.6.10.0 legacy 397/397 gate",
        "",
        f"Global accent dictionary: {len(global_map)}",
        f"Master rows promoted: {len(promoted)}",
        f"Too-long promotions skipped: {len(skipped_long)}",
        f"Standalone repeat rows injected: {len(injected)}",
        f"Dynamic names configured: {len(dyn_rows)}",
        "Front skeleton fixes: NGUOI=CO -> NGUOI CO; THEGIOI=BANCO -> THEGIOI BANCO",
        "",
        "Runtime-name compact map:",
    ]
    for r in dyn_rows:
        lines.append(f"- {r['japanese']} -> {r['vi_accented']}")
    lines += [
        "",
        "Font hotfix:",
        f"- char={breve_meta['char']} code={breve_meta['code']} slot={breve_meta['slot']} atlas={breve_meta['atlas_off']}",
        "- breve redrawn as cup/smile instead of cap/hat",
        f"- raw sectors changed by glyph hotfix: {breve_meta['sectors']}",
        "",
        "Targeted screenshot regressions:",
        "- intro Japanese-looking glyph at old '=' positions",
        "- lowercase ă shape in 'năng'",
        "- LUOT / other no-accent fallbacks",
        "- ジガー and other short dynamic character names",
        "",
        "Build result: SOURCE PIPELINE COMPLETED; RUNTIME TEST REQUIRED",
    ]
    report.write_text("\n".join(lines)+"\n", encoding="utf-8")

    print()
    print("[OK] 0.6.12.0 Batch 3 build completed")
    print(f"Report: {report.name}")
    for p in sorted(changed(out_dir,before)):
        if p.exists():
            print("  ", p.name)
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("[ERROR]", repr(e))
        raise SystemExit(9)
