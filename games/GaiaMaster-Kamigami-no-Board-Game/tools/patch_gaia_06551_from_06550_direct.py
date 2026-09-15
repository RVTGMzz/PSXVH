#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from collections import Counter
import hashlib
import shutil
import sys
import traceback
from pathlib import Path

import build_gaia_06551_batch45r2_font_micro_polish as r2
import build_gaia_06550_batch45_frontface_polish as b45
import batch43_wholegame_patch_06530 as b43

CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
LOG_NAME = "PATCH_LOG_0.6.55.1_R2.txt"
REPORT_NAME = "GaiaMaster_0.6.55.1_BATCH45R2_DIRECT_FINAL_REPORT.txt"


def die(msg: str):
    raise RuntimeError(msg)


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().lower()


def log_line(log, text=""):
    s = str(text)
    print(s, flush=True)
    log.write(s + "\n")
    log.flush()


def verify_batch43(clean: Path, built: Path) -> int:
    rows = b43.load_manifest()
    base = r2.base
    with clean.open("rb") as f:
        slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        clean_prg = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)
    cmap = dict(zip(base.CUSTOM_CHARS, base.safe_custom_codes(slps, clean_prg, len(base.CUSTOM_CHARS))))
    with built.open("rb") as f:
        prg = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)

    bad = []
    for off, jp, vi, field in rows:
        clean_cur = bytes(clean_prg[off:off + field])
        try:
            clean_norm = clean_cur.decode("cp932").strip(" \u3000")
        except Exception:
            clean_norm = None
        if clean_norm != jp:
            bad.append("CLEAN source 0x%X" % off)
            continue
        enc, _ = base.encode_runtime_text(vi, cmap)
        want = enc + b"\0" * (field - len(enc))
        got = bytes(prg[off:off + field])
        if got != want:
            bad.append("built field 0x%X" % off)
    if bad:
        die("Batch43 read-only verify failed: %d row(s): %s" % (len(bad), ", ".join(bad[:12])))
    return len(rows)


def _compress_native_a(g, y0=3, height=9):
    b = r2.base.bbox(g)
    if b is None:
        die("Native lowercase a glyph is empty")
    _x0, sy0, _x1, sy1 = b
    src_h = sy1 - sy0 + 1
    out = [[0] * 12 for _ in range(12)]
    for dy in range(height):
        sy = sy0 if height == 1 else sy0 + int(round(dy * (src_h - 1) / float(height - 1)))
        out[y0 + dy] = g[sy][:]
    return out


def historical_a_breve_v3(clean_slps: bytes) -> bytes:
    """Reproduce exactly the 0.6.14 historical lowercase ă rebuild.

    0.6.55.0 inherits this bitmap. It is intentionally NOT the generic
    make_vi_glyph() result, so R2 must use this as the source baseline.
    """
    base = r2.base
    fw = chr(ord("a") + 0xFEE0)
    pair = fw.encode("cp932")
    native_code = (pair[0] << 8) | pair[1]
    native_slot = base.mapping_value(clean_slps, native_code)
    if native_slot is None or not (0 <= native_slot < base.ATLAS_GLYPHS):
        die("Historical ă gate: native lowercase a mapping invalid")

    off = base.ATLAS_OFF + native_slot * base.GLYPH_BYTES
    native_raw = bytes(clean_slps[off:off + base.GLYPH_BYTES])
    g0 = base.decode_glyph(native_raw)
    hist = Counter(v for row in g0 for v in row if v != 0)
    if not hist:
        die("Historical ă gate: native lowercase a has no visible pixels")

    shadow = 7 if hist.get(7, 0) else None
    fill_candidates = [(count, idx) for idx, count in hist.items() if idx != shadow]
    fill_candidates.sort(reverse=True)
    if not fill_candidates:
        die("Historical ă gate: cannot derive fill palette")
    fill = fill_candidates[0][1]
    if shadow is None:
        other = [(count, idx) for idx, count in hist.items() if idx != fill]
        other.sort(reverse=True)
        shadow = other[0][1] if other else fill

    g = _compress_native_a(g0, y0=3, height=9)
    b = base.bbox(g)
    if b is None:
        die("Historical ă gate: compressed body vanished")
    x0, _y0, x1, _y1 = b
    cx = (x0 + x1) // 2
    mark = [
        (max(0, cx - 2), 0),
        (max(0, cx - 1), 1),
        (cx, 1),
        (min(11, cx + 1), 1),
        (min(11, cx + 2), 0),
    ]
    if shadow != fill:
        for x, y in mark:
            sx, sy = x + 1, y + 1
            if 0 <= sx < 12 and 0 <= sy < 12:
                g[sy][sx] = shadow
    for x, y in mark:
        g[y][x] = fill
    return base.encode_glyph(g)


def expected_06550_glyph(clean_slps: bytes, ch: str, cache: dict) -> bytes:
    if ch == "ă":
        return historical_a_breve_v3(clean_slps)
    glyph, _meta = r2.base.make_vi_glyph(clean_slps, ch, cache)
    return glyph


def patch_font_direct(clean: Path, src06550: Path, out06551: Path):
    base = r2.base
    with clean.open("rb") as f:
        clean_slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        clean_prg = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)
    if base.sha1_bytes(clean_slps) != base.EXPECTED_SLPS_SHA1:
        die("CLEAN SLPS hash mismatch")
    if base.sha1_bytes(clean_prg) != base.EXPECTED_PRG_SHA1:
        die("CLEAN PRGPACK hash mismatch")

    if out06551.exists():
        out06551.unlink()
    shutil.copy2(src06550, out06551)

    with out06551.open("rb") as f:
        built_slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        prg_before = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)

    old_cache = {}
    new_cache = {}
    plan = []
    historical_special = []
    for ch, slot in zip(base.CUSTOM_CHARS, base.PRODUCTION_SLOTS):
        old_glyph = expected_06550_glyph(clean_slps, ch, old_cache)
        new_glyph, meta = r2.make_vi_glyph_r2(clean_slps, ch, new_cache)
        off = base.ATLAS_OFF + slot * base.GLYPH_BYTES
        current = bytes(built_slps[off:off + base.GLYPH_BYTES])
        if current != old_glyph:
            die("0.6.55.0 direct source mismatch for %r slot=%d" % (ch, slot))
        if ch == "ă":
            historical_special.append(ch)
        if ch in r2.AFFECTED:
            if old_glyph == new_glyph:
                die("R2 affected glyph did not change from 0.6.55.0 baseline: %r" % ch)
            plan.append((ch, slot, old_glyph, new_glyph, meta))

    if len(plan) != len(r2.EXPECTED_AFFECTED):
        die("Direct R2 affected count drift: %d != %d" % (len(plan), len(r2.EXPECTED_AFFECTED)))

    new_slps = bytearray(built_slps)
    for ch, slot, _old, new, _meta in plan:
        off = base.ATLAS_OFF + slot * base.GLYPH_BYTES
        new_slps[off:off + base.GLYPH_BYTES] = new

    changed = set()
    with out06551.open("r+b") as f:
        base.write_changed_iso_file(f, base.SLPS_EXTENT, built_slps, bytes(new_slps), changed)
        for sec in sorted(changed):
            f.seek(sec * 2352)
            raw = f.read(2352)
            f.seek(sec * 2352)
            f.write(base.regen_sector(raw))

    with out06551.open("rb") as f:
        chk_slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        prg_after = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)
    if prg_after != prg_before:
        die("Direct R2 font-only patch changed PRGPACK")

    for ch, slot in zip(base.CUSTOM_CHARS, base.PRODUCTION_SLOTS):
        off = base.ATLAS_OFF + slot * base.GLYPH_BYTES
        cur = bytes(chk_slps[off:off + base.GLYPH_BYTES])
        if ch in r2.AFFECTED:
            want = next(n for c, s, _o, n, _m in plan if c == ch and s == slot)
        else:
            want = expected_06550_glyph(clean_slps, ch, old_cache)
        if cur != want:
            die("Direct R2 post-write glyph verify failed for %r slot=%d" % (ch, slot))

    return plan, len(changed), historical_special


def make_output_cue(src_bin: Path, out_bin: Path) -> Path:
    out_cue = out_bin.with_suffix(".cue")
    src_cue = src_bin.with_suffix(".cue")
    if src_cue.is_file():
        text = src_cue.read_text(encoding="utf-8", errors="replace")
        text = text.replace(src_bin.name, out_bin.name)
    else:
        text = 'FILE "%s" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' % out_bin.name
    out_cue.write_text(text, encoding="utf-8")
    return out_cue


def find_clean(root: Path) -> Path:
    for p in root.glob("*.bin"):
        if p.is_file() and sha1_file(p) == CLEAN_SHA1:
            return p.resolve()
    die("Exact CLEAN Japan BIN not found beside launcher; expected SHA1 %s" % CLEAN_SHA1)


def find_verified_06550(root: Path, clean: Path, log) -> Path:
    candidates = [p for p in root.glob("*.bin") if p.is_file() and p.resolve() != clean.resolve() and "0.6.55.0" in p.name]
    candidates.sort(key=lambda p: p.stat().st_mtime_ns, reverse=True)
    if not candidates:
        die("No 0.6.55.0 BIN found beside launcher")
    for p in candidates:
        log_line(log, "Checking 0.6.55.0 candidate: %s" % p.name)
        try:
            a = b45.b42.core.verify_output(clean, p)
            b = verify_batch43(clean, p)
            c = b45._verify_intro(clean, p)
            log_line(log, "  contract: Batch42=%d/560 Batch43=%d/102 intro=%d/19" % (a, b, c))
            if a == 560 and b == 102 and c == 19:
                return p.resolve()
        except Exception as e:
            log_line(log, "  reject: %r" % e)
    die("No 0.6.55.0 candidate passed 560+102+19 input contract")


def selftest() -> int:
    if r2.AFFECTED != r2.EXPECTED_AFFECTED:
        die("R2 affected set drift")
    if len(r2.AFFECTED) != 23:
        die("R2 affected count drift")
    if "ă" not in r2.AFFECTED:
        die("Historical ă must be in R2 affected set")
    if "BATCH4" in LOG_NAME or "BATCH5" in LOG_NAME:
        die("Direct patch log name collides with historical rename rules")
    print("GAIA MASTER 0.6.55.1 DIRECT FONT-ONLY SELFTEST PASS")
    print("input=verified_0.6.55.0")
    print("pre_contract=560+102+19")
    print("historical_a_breve=v3_special_baseline")
    print("affected=23")
    print("prgpatch=NONE")
    print("runtime=STILL_REQUIRED")
    return 0


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        return selftest()
    if len(sys.argv) != 2:
        print("Usage: patch_gaia_06551_from_06550_direct.py PACKAGE_ROOT | --selftest")
        return 2

    root = Path(sys.argv[1].strip().strip('"')).expanduser().resolve()
    log_path = root / LOG_NAME
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        try:
            log_line(log, "GAIA MASTER 0.6.55.1 - DIRECT 0.6.55.0 FONT-ONLY PATCH")
            log_line(log, "Package root: %s" % root)
            clean = find_clean(root)
            log_line(log, "[OK] CLEAN SHA1: %s" % sha1_file(clean))
            src = find_verified_06550(root, clean, log)
            log_line(log, "[OK] VERIFIED 0.6.55.0 INPUT: %s" % src.name)
            log_line(log, "Input 0.6.55.0 SHA1: %s" % sha1_file(src))

            out = src.with_name(src.name.replace("0.6.55.0", "0.6.55.1"))
            if out == src:
                out = root / (src.stem + " [R2 FONT].bin")

            plan, sectors, special = patch_font_direct(clean, src, out)

            pre42 = b45.b42.core.verify_output(clean, out)
            pre43 = verify_batch43(clean, out)
            preintro = b45._verify_intro(clean, out)
            if (pre42, pre43, preintro) != (560, 102, 19):
                die("Post-patch contract drift: %r" % ((pre42, pre43, preintro),))

            cue = make_output_cue(src, out)
            report = root / REPORT_NAME
            lines = [
                "GAIA MASTER 0.6.55.1 - BATCH45R2 DIRECT FONT-ONLY PATCH",
                "=" * 78,
                "CLEAN SHA1: %s" % sha1_file(clean),
                "Input 0.6.55.0 BIN: %s" % src.name,
                "Input 0.6.55.0 SHA1: %s" % sha1_file(src),
                "Pre-patch contract: Batch42 560/560 + Batch43 102/102 + intro 19/19",
                "Historical lowercase ă baseline: 0.6.14 v3 fresh rebuild",
                "R2 affected glyphs: %d/23" % len(plan),
                "Changed raw SLPS sectors: %d" % sectors,
                "PRGPACK changed by R2 font patch: NO",
                "Post-patch contract: 662/662 + intro 19/19",
                "Architecture: native 12x12 / 72-byte / 4bpp / mapping-only",
                "Frozen Vietnamese codepage: 60/60",
                "",
                "Changed glyphs:",
            ]
            for ch, slot, _old, _new, meta in plan:
                extra = ""
                if meta.get("stroke_meta"):
                    extra = " stroke=%r" % (meta["stroke_meta"],)
                lines.append("- U+%04X %s slot=%d body=%r final=%r%s" % (ord(ch), ch, slot, meta["body_bbox"], meta["final_bbox"], extra))
            lines += [
                "",
                "STATUS: BUILD/STATIC CONTRACT PASS ONLY",
                "RUNTIME SCREENSHOT STILL REQUIRED.",
                "Do NOT call Runtime PASS from this report alone.",
                "Output BIN: %s" % out.name,
                "Output CUE: %s" % cue.name,
            ]
            report.write_text("\n".join(lines) + "\n", encoding="utf-8")

            log_line(log, "[PASS] DIRECT FONT-ONLY PATCH COMPLETED")
            log_line(log, "[PASS] 662/662 + intro 19/19 preserved")
            log_line(log, "[PASS] historical ă source gate: v3 baseline")
            log_line(log, "Output BIN: %s" % out.name)
            log_line(log, "Output CUE: %s" % cue.name)
            log_line(log, "Report: %s" % report.name)
            log_line(log, "RUNTIME SCREENSHOT STILL REQUIRED")
            return 0
        except Exception as e:
            log_line(log, "RESULT: FAIL")
            log_line(log, "ERROR: %r" % e)
            for line in traceback.format_exc().splitlines():
                log_line(log, line)
            return 9


if __name__ == "__main__":
    raise SystemExit(main())
