#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import build_gaia_06550_batch45_frontface_polish as b45
import build_gaia_06100_hybrid_accent_b1_READABLE as base

VERSION = "0.6.55.1"
BATCH = "BATCH45R2"
CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"

TOOLS = Path(__file__).resolve().parent
PREV_BUILDER = TOOLS / "build_gaia_06550_batch45_frontface_polish.py"

TOP_STRUCTURAL = {"\u0302", "\u0306"}  # circumflex, breve
TOP_TONES = {"\u0301", "\u0300", "\u0309", "\u0303"}  # acute, grave, hook, tilde

# Only these glyph families change in R2. Every other frozen glyph must remain
# byte-identical to the 0.6.55.0 generator.
AFFECTED = {
    ch for ch in base.CUSTOM_CHARS
    if ch in ("Đ", "đ")
    or any(m in TOP_STRUCTURAL for m in base.decompose(ch)[1])
}


def die(msg: str):
    raise RuntimeError(msg)


def _fit_body_v2(g, marks):
    """Reserve one extra top row for circumflex/breve families.

    0.6.55.0 drew the structural mark immediately above the body and
    draw_dual() then dropped its shadow onto the body row. R2 reserves a third
    top row, so the mark can move up one pixel while the native 12x12
    architecture stays unchanged.
    """
    src = base.bbox(g)
    if src is None:
        die("Empty native base glyph")

    x0, sy0, x1, sy1 = src
    structural_top = any(m in TOP_STRUCTURAL for m in marks)
    any_top = any(
        m in marks
        for m in ("\u0306", "\u0302", "\u031B",
                  "\u0301", "\u0300", "\u0309", "\u0303")
    )
    bottom_mark = "\u0323" in marks

    top_need = 3 if structural_top else (2 if any_top else 0)
    bottom_limit = 10 if bottom_mark else 11

    if sy0 >= top_need and sy1 <= bottom_limit:
        return [row[:] for row in g], src, src, "native-preserved-r2"

    src_h = sy1 - sy0 + 1
    dst_y1 = min(sy1, bottom_limit)
    dst_y0 = max(top_need, dst_y1 - src_h + 1)

    if dst_y0 > dst_y1:
        dst_y0 = top_need
        dst_y1 = bottom_limit

    dst_h = dst_y1 - dst_y0 + 1
    if dst_h <= 0:
        die("No vertical room for glyph")

    out = [[0] * 12 for _ in range(12)]
    for dy in range(dst_h):
        sy = sy0 if dst_h == 1 else (
            sy0 + int(round(dy * (src_h - 1) / float(dst_h - 1)))
        )
        out[dst_y0 + dy] = g[sy][:]

    body = base.bbox(out)
    if body is None:
        die("Empty fitted R2 glyph body")
    return out, src, body, "minimal-fit-r2"


def _fit_x(points, shadow=True):
    """Shift a whole mark horizontally so fill and optional shadow stay 12x12."""
    pts = list(points)
    if not pts:
        return pts
    min_x = min(x for x, _ in pts)
    max_x = max(x for x, _ in pts) + (1 if shadow else 0)

    shift = 0
    if min_x < 0:
        shift += -min_x
    if max_x + shift > 11:
        shift -= (max_x + shift - 11)

    out = [(x + shift, y) for x, y in pts]
    if any(not (0 <= x < 12 and 0 <= y < 12) for x, y in out):
        die("R2 mark fill point escaped 12x12: %r -> %r" % (pts, out))
    if shadow and any(not (0 <= x + 1 < 12 and 0 <= y + 1 < 12) for x, y in out):
        die("R2 mark shadow point escaped 12x12: %r -> %r" % (pts, out))
    return out


def _draw(g, points, fill, shadow):
    """Draw a top/side mark with full fill+shadow bounds preserved."""
    pts = _fit_x(points, shadow=(shadow != fill))
    rendered = set(pts)
    if shadow != fill:
        rendered.update((x + 1, y + 1) for x, y in pts)
    base.draw_dual(g, pts, fill, shadow)
    return rendered


def _draw_unshifted(g, points, fill, shadow):
    """Preserve an anchor exactly; allow legacy-style shadow clipping only."""
    pts = list(points)
    if any(not (0 <= x < 12 and 0 <= y < 12) for x, y in pts):
        die("Anchored R2 fill point escaped 12x12: %r" % (pts,))
    base.draw_dual(g, pts, fill, shadow)
    return set(pts)


def _stroke_span(stem_x, left_extent, width=4):
    """Return a fixed-width horizontal span that must cross stem_x."""
    start = stem_x - left_extent
    start = max(0, min(12 - width, start))
    pts = list(range(start, start + width))
    if stem_x not in pts:
        die("Stroke span lost its stem anchor: stem=%d span=%r" % (stem_x, pts))
    return pts


def _right_stem_x(g, body_bbox, fill):
    """Find the real right-hand vertical stem of lowercase native d.

    Restricting the search to the right half avoids mistaking the left bowl
    stroke for the ascender. Longest vertical run is the primary signal;
    fill-pixel count breaks shadow/tie cases.
    """
    x0, y0, x1, y1 = body_bbox
    cx = (x0 + x1) // 2
    candidates = range(max(x0, cx), x1 + 1)

    def score(x):
        longest = 0
        run = 0
        fill_count = 0
        visible = 0
        for y in range(y0, y1 + 1):
            v = g[y][x]
            if v:
                visible += 1
                run += 1
                longest = max(longest, run)
                if v == fill:
                    fill_count += 1
            else:
                run = 0
        # Prefer a real continuous stem, then actual fill, then total pixels.
        # Rightmost x is only the final tie-break.
        return (longest, fill_count, visible, x)

    return max(candidates, key=score)


def _tone_points_for_structural(mark, cx, top2, top3, is_breve=False):
    """Place stacked tone marks in a side lane so they don't overwrite ^ / breve."""
    # Breve is two pixels wider than circumflex, so its tone lane starts one
    # pixel farther out. This matters for ắ: the old shared lane would collide
    # with the breve's right shoulder.
    lane = 4 if is_breve else 3
    if mark == "\u0301":  # acute, upper-right
        return [(cx + lane, top3), (cx + lane - 1, top2)]
    if mark == "\u0300":  # grave, upper-left
        return [(cx - lane, top3), (cx - lane + 1, top2)]
    if mark == "\u0309":  # hook above, compact upper-right
        return [(cx + lane - 1, top3), (cx + lane, top3), (cx + lane, top2)]
    if mark == "\u0303":  # tilde, compact upper-right wave
        return [(cx + lane - 1, top3), (cx + lane, top2), (cx + lane + 1, top3)]
    raise ValueError(mark)


def make_vi_glyph_r2(slps, ch, base_cache):
    """Generate only runtime-evidenced R2 families; delegate all others unchanged."""
    if ch not in AFFECTED:
        return base.make_vi_glyph(slps, ch, base_cache)

    letter, marks = base.decompose(ch)
    if letter not in base_cache:
        base_cache[letter] = base.native_base(slps, letter)

    native_code, native_slot, _raw, base_grid = base_cache[letter]
    fill, shadow, _hist = base.choose_layers(base_grid)

    g, src_bbox, body_bbox, fit_mode = _fit_body_v2(base_grid, marks)
    x0, y0, x1, y1 = body_bbox
    cx = (x0 + x1) // 2

    top1 = max(0, y0 - 1)
    top2 = max(0, y0 - 2)
    top3 = max(0, y0 - 3)

    structural_fill = set()
    tone_fill = set()
    stroke_meta = None

    # Structural marks first. R2 moves ^ / breve UP one pixel versus 0.6.55.0.
    if "\u0306" in marks:  # breve
        structural_fill |= _draw(g, [
            (cx - 2, top2),
            (cx - 1, top3),
            (cx, top3),
            (cx + 1, top3),
            (cx + 2, top2),
        ], fill, shadow)

    if "\u0302" in marks:  # circumflex
        structural_fill |= _draw(g, [
            (cx - 1, top2),
            (cx, top3),
            (cx + 1, top2),
        ], fill, shadow)

    horn_anchor = None
    if "\u031B" in marks:  # preserved 0.6.55.0 horn behavior
        hx = min(10, x1)
        hy = min(10, y0 + 1)
        horn_anchor = (hx, hy)
        _draw(g, [
            (hx, hy),
            (min(10, hx + 1), max(0, hy - 1)),
        ], fill, shadow)

    if "stroke" in marks:
        if ch == "Đ":
            # Uppercase D has its vertical stem on the LEFT. Restore the
            # pre-Batch45 vertical placement; there was no runtime evidence
            # that uppercase Đ needed the one-pixel raise.
            stem_x = x0
            yy = max(y0, min(y1, (y0 + y1) // 2))
            xs = _stroke_span(stem_x, left_extent=1, width=4)
            points = [(x, yy) for x in xs]
            _draw_unshifted(g, points, fill, shadow)
            stroke_meta = ("uppercase-left-stem", stem_x, yy)
        elif ch == "đ":
            # Lowercase d has its ascender on the RIGHT. Batch45 still anchored
            # to x0, which only grazed the wrong side of the glyph. Find the
            # actual right stem and cross through it. Runtime screenshot asks
            # for one further pixel UP from Batch45, hence center-2 here.
            stem_x = _right_stem_x(g, body_bbox, fill)
            yy = max(y0, min(y1, (y0 + y1) // 2 - 2))
            xs = _stroke_span(stem_x, left_extent=2, width=4)
            points = [(x, yy) for x in xs]
            _draw_unshifted(g, points, fill, shadow)
            stroke_meta = ("lowercase-right-stem", stem_x, yy)
        else:
            die("Unexpected stroke glyph %r" % ch)

    structural_top = any(m in TOP_STRUCTURAL for m in marks)

    # Tone marks. For circumflex/breve combinations, use a separate side lane
    # instead of drawing on the same coordinates as the structural mark.
    for tone in ("\u0301", "\u0300", "\u0309", "\u0303"):
        if tone not in marks:
            continue
        if structural_top:
            pts = _tone_points_for_structural(
                tone, cx, top2, top3, is_breve=("\u0306" in marks)
            )
            tone_fill |= _draw(g, pts, fill, shadow)
            continue

        if tone == "\u0301":  # acute
            if horn_anchor is not None:
                hx, hy = horn_anchor
                _draw(g, [
                    (min(10, hx + 3), max(0, hy - 4)),
                    (min(10, hx + 2), max(0, hy - 3)),
                ], fill, shadow)
            else:
                _draw(g, [(cx + 1, top2), (cx, top1)], fill, shadow)

        elif tone == "\u0300":  # grave
            if horn_anchor is not None:
                hx, hy = horn_anchor
                _draw(g, [
                    (max(0, hx - 2), max(0, hy - 4)),
                    (max(0, hx - 1), max(0, hy - 3)),
                ], fill, shadow)
            else:
                _draw(g, [(cx - 1, top2), (cx, top1)], fill, shadow)

        elif tone == "\u0309":  # hook above
            _draw(g, [
                (cx, top2), (cx + 1, top2),
                (cx + 1, top1), (cx, top1),
            ], fill, shadow)

        elif tone == "\u0303":  # tilde
            _draw(g, [
                (cx - 2, top1), (cx - 1, top2),
                (cx, top1), (cx + 1, top1), (cx + 2, top2),
            ], fill, shadow)

    if "\u0323" in marks:  # dot below unchanged
        dot_y = min(11, y1 + 1)
        _draw_unshifted(g, [(cx, dot_y)], fill, shadow)

    if structural_fill & tone_fill:
        die("R2 structural/tone rendered-pixel collision in %r: %r" %
            (ch, sorted(structural_fill & tone_fill)))

    final_bbox = base.bbox(g)
    if final_bbox is None:
        die("R2 generated empty glyph %r" % ch)

    return base.encode_glyph(g), {
        "base": letter,
        "native_code": native_code,
        "native_slot": native_slot,
        "fill": fill,
        "shadow": shadow,
        "src_bbox": src_bbox,
        "body_bbox": body_bbox,
        "final_bbox": final_bbox,
        "fit": fit_mode,
        "marks": [
            "stroke" if x == "stroke" else "U+%04X" % ord(x)
            for x in marks
        ],
        "stroke_meta": stroke_meta,
        "structural_fill": sorted(structural_fill),
        "tone_fill": sorted(tone_fill),
    }


def _font_plan(clean: Path):
    with clean.open("rb") as f:
        clean_slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        clean_prg = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)

    if base.sha1_bytes(clean_slps) != base.EXPECTED_SLPS_SHA1:
        die("CLEAN SLPS hash mismatch")
    if base.sha1_bytes(clean_prg) != base.EXPECTED_PRG_SHA1:
        die("CLEAN PRGPACK hash mismatch")

    cache_old = {}
    cache_new = {}
    rows = []
    for ch, slot in zip(base.CUSTOM_CHARS, base.PRODUCTION_SLOTS):
        old_glyph, _old_meta = base.make_vi_glyph(clean_slps, ch, cache_old)
        new_glyph, new_meta = make_vi_glyph_r2(clean_slps, ch, cache_new)

        if len(old_glyph) != base.GLYPH_BYTES or len(new_glyph) != base.GLYPH_BYTES:
            die("Glyph byte-size gate failed for %r" % ch)

        old_box = base.bbox(base.decode_glyph(old_glyph))
        new_box = base.bbox(base.decode_glyph(new_glyph))
        if old_box is None or new_box is None:
            die("Empty glyph bbox for %r" % ch)
        if any(v < 0 or v > 11 for v in new_box):
            die("Glyph bbox escaped 12x12 for %r: %r" % (ch, new_box))

        changed = old_glyph != new_glyph
        if ch not in AFFECTED and changed:
            die("Unaffected glyph changed unexpectedly: %r" % ch)
        if ch in AFFECTED and not changed:
            die("Affected glyph did not change: %r" % ch)

        rows.append((ch, slot, old_glyph, new_glyph, new_meta))
    return clean_slps, rows


def _geometry_gate(rows):
    by = {ch: meta for ch, _slot, _old, _new, meta in rows}

    upper = by["Đ"].get("stroke_meta")
    lower = by["đ"].get("stroke_meta")
    if not upper or upper[0] != "uppercase-left-stem":
        die("Uppercase Đ left-stem gate failed")
    if not lower or lower[0] != "lowercase-right-stem":
        die("Lowercase đ right-stem gate failed")

    # Ensure lowercase stroke really crosses its detected stem and remains inside.
    _tag, stem_x, yy = lower
    if not (0 <= stem_x <= 11 and 0 <= yy <= 11):
        die("Lowercase đ stem/crossbar escaped 12x12")

    # Every structural+tone glyph must have disjoint rendered coordinates
    # (fill and shadow), not merely disjoint fill anchors.
    for ch, _slot, _old, _new, meta in rows:
        if ch not in AFFECTED:
            continue
        sf = set(tuple(p) for p in meta.get("structural_fill", []))
        tf = set(tuple(p) for p in meta.get("tone_fill", []))
        if sf & tf:
            die("Static accent collision remains in %r" % ch)

    return True


def patch_font(clean: Path, built: Path):
    clean_slps, rows = _font_plan(clean)
    _geometry_gate(rows)

    with built.open("rb") as f:
        built_slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        prg_before = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)

    new_slps = bytearray(built_slps)
    changed_chars = []

    for ch, slot, old_glyph, new_glyph, meta in rows:
        off = base.ATLAS_OFF + slot * base.GLYPH_BYTES
        current = bytes(new_slps[off:off + base.GLYPH_BYTES])

        # Strong source gate: the 0.6.55.0 output must still contain exactly the
        # glyph that its own generator would have installed.
        if current != old_glyph:
            die("0.6.55.0 glyph source mismatch for %r slot=%d" % (ch, slot))

        if ch in AFFECTED:
            new_slps[off:off + base.GLYPH_BYTES] = new_glyph
            changed_chars.append((ch, slot, meta))

    changed_sectors = set()
    with built.open("r+b") as f:
        base.write_changed_iso_file(
            f, base.SLPS_EXTENT, built_slps, bytes(new_slps), changed_sectors
        )
        for sec in sorted(changed_sectors):
            f.seek(sec * 2352)
            raw = f.read(2352)
            f.seek(sec * 2352)
            f.write(base.regen_sector(raw))

    with built.open("rb") as f:
        check_slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        prg_after = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)

    if prg_after != prg_before:
        die("Font-only R2 patch unexpectedly changed PRGPACK")

    for ch, slot, old_glyph, new_glyph, _meta in rows:
        off = base.ATLAS_OFF + slot * base.GLYPH_BYTES
        cur = bytes(check_slps[off:off + base.GLYPH_BYTES])
        want = new_glyph if ch in AFFECTED else old_glyph
        if cur != want:
            die("Post-write glyph verification failed for %r" % ch)

    return changed_chars, len(changed_sectors)


def selftest():
    if not PREV_BUILDER.is_file():
        die("Missing 0.6.55.0 builder")
    if not AFFECTED:
        die("Affected glyph set is empty")
    if "Đ" not in AFFECTED or "đ" not in AFFECTED:
        die("Đ/đ missing from affected set")
    for required in ("â", "ê", "ô", "ă", "ấ", "ế", "ố"):
        if required in base.CUSTOM_CHARS and required not in AFFECTED:
            die("Structural accent family missing %r" % required)

    untouched = set(base.CUSTOM_CHARS) - AFFECTED
    if not untouched:
        die("R2 scope unexpectedly covers the entire frozen codepage")

    print("=" * 78)
    print("GAIA MASTER 0.6.55.1 BATCH45R2 STATIC SELFTEST PASS")
    print("=" * 78)
    print("architecture=native_12x12_mapping_only")
    print("frozen_codepage=%d" % len(base.CUSTOM_CHARS))
    print("affected_glyphs=%d" % len(AFFECTED))
    print("unaffected_glyphs=%d (must remain byte-identical at CLEAN-runtime gate)" %
          len(untouched))
    print("uppercase_D=LEFT_STEM_PRE_BATCH45_VERTICAL")
    print("lowercase_d=RIGHT_STEM_AUTO_ANCHORED_CENTER_MINUS_2")
    print("circumflex_breve=UP_1PX_WITH_EXTRA_TOP_ROW")
    print("stacked_tones=SEPARATE_SIDE_LANE")
    print("runtime_test=STILL_REQUIRED")
    return 0


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        return selftest()
    if len(sys.argv) != 2:
        print("Usage: %s CLEAN.bin | --selftest" % Path(sys.argv[0]).name)
        return 2

    clean = Path(sys.argv[1]).expanduser().resolve()
    if not clean.is_file():
        print("[ERROR] CLEAN BIN not found:", clean)
        return 2

    got = base.sha1_file(clean).lower()
    if got != CLEAN_SHA1:
        print("[ERROR] Need CLEAN SHA1 %s; got %s" % (CLEAN_SHA1, got))
        return 3

    out = clean.parent
    before = b45.b42.core.snapshot(out)

    cp = subprocess.run(
        [sys.executable, str(PREV_BUILDER), str(clean)],
        cwd=str(TOOLS),
        check=False,
    )
    if cp.returncode:
        die("0.6.55.0 builder failed: %d" % cp.returncode)

    bins = [
        p for p in b45.b42.core.changed(out, before)
        if p.suffix.lower() == ".bin" and p.resolve() != clean.resolve()
    ]
    bins.sort(key=lambda p: p.stat().st_mtime_ns, reverse=True)
    if not bins:
        die("No 0.6.55.0 output BIN")

    built = next((p for p in bins if "0.6.55.0" in p.name), bins[0])

    # Before touching font pixels, retain all proven translation contracts.
    if b45.b42.core.verify_output(clean, built) != b45.BASE:
        die("Batch42 exact gate failed before R2 font patch")
    if b45._verify_intro(clean, built) != 19:
        die("Batch45 intro gate failed before R2 font patch")

    changed_chars, changed_sectors = patch_font(clean, built)

    # Font-only patch must not disturb any exact PRGPACK contract.
    if b45.b42.core.verify_output(clean, built) != b45.BASE:
        die("Batch42 exact gate failed after R2 font patch")
    if b45._verify_intro(clean, built) != 19:
        die("Batch45 intro gate failed after R2 font patch")

    old = built
    new = old.with_name(
        old.name.replace("0.6.55.0", VERSION).replace("BATCH45", BATCH)
    )
    if new == old:
        new = old.with_name(clean.stem + " [VI 0.6.55.1 FONT MICRO POLISH].bin")
    if new.exists():
        new.unlink()
    old.rename(new)

    for cue in [
        p for p in b45.b42.core.changed(out, before)
        if p.suffix.lower() == ".cue"
    ]:
        try:
            text = cue.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if old.name in text or "0.6.55.0" in cue.name:
            nc = cue.with_name(
                cue.name.replace("0.6.55.0", VERSION).replace("BATCH45", BATCH)
            )
            if nc == cue:
                nc = cue.with_name(
                    clean.stem + " [VI 0.6.55.1 FONT MICRO POLISH].cue"
                )
            if nc.exists():
                nc.unlink()
            nc.write_text(
                text.replace(old.name, new.name)
                    .replace("0.6.55.0", VERSION)
                    .replace("BATCH45", BATCH),
                encoding="utf-8",
            )
            if cue.exists() and cue != nc:
                cue.unlink()
            break

    report = out / "GaiaMaster_0.6.55.1_BATCH45R2_FINAL_REPORT.txt"
    report_lines = [
        "GAIA MASTER 0.6.55.1 - BATCH45R2 FONT MICRO POLISH",
        "=" * 78,
        "Input CLEAN SHA1: %s" % got,
        "Batch42 master exact fields preserved: 560/560",
        "Batch43 whole-game visible fields inherited: 102/102",
        "Combined exact contract inherited: 662/662",
        "Intro polish preserved: 19/19",
        "Unsafe intro '=' removal preserved: PASS",
        "PRGPACK changed by R2 font patch: NO",
        "Frozen Vietnamese codepage: 60/60",
        "Architecture: native 12x12 / 72-byte / 4bpp / mapping-only",
        "Renderer hook / pointer redirect / 12x16 / 6x12: NONE",
        "",
        "RUNTIME-EVIDENCED FONT FIXES:",
        "- Đ uppercase: restored left-stem rule + pre-Batch45 vertical placement",
        "- đ lowercase: right-stem auto-anchor, crossbar one more pixel up vs 0.6.55.0",
        "- circumflex/breve families: structural mark raised one pixel",
        "- stacked structural+tone marks: separate side lane to avoid fill collision",
        "",
        "STATIC FONT GATES:",
        "- all 60 glyphs remain exactly 72 bytes",
        "- all generated bboxes remain inside 12x12",
        "- every unaffected glyph is byte-identical to 0.6.55.0 generator",
        "- structural/tone rendered pixels (fill+shadow) are disjoint",
        "- output glyph bytes re-read and verified after sector regeneration",
        "- PRGPACK byte-for-byte unchanged by font-only R2 patch",
        "",
        "Changed custom glyphs: %d" % len(changed_chars),
        "Changed raw SLPS sectors: %d" % changed_sectors,
    ]
    for ch, slot, meta in changed_chars:
        extra = ""
        if meta.get("stroke_meta"):
            extra = " stroke=%r" % (meta["stroke_meta"],)
        report_lines.append(
            "- U+%04X %s slot=%d body=%r final=%r%s" %
            (ord(ch), ch, slot, meta["body_bbox"], meta["final_bbox"], extra)
        )
    report_lines += [
        "",
        "STATUS: STATIC/BUILD GATES ONLY",
        "RUNTIME SCREENSHOT STILL REQUIRED.",
        "Do NOT call Runtime PASS from this report alone.",
        "Output BIN: %s" % new.name,
    ]
    report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("[OK] 0.6.55.1 font micro-polish applied")
    print("[OK] Exact translation contract preserved: 662 inherited")
    print("[OK] Intro polish preserved: 19/19")
    print("[OK] Changed glyphs:", len(changed_chars))
    print("[OK] Changed SLPS raw sectors:", changed_sectors)
    print("Output:", new)
    print("Report:", report)
    print("[NOTE] Runtime screenshot still required.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print("[ERROR]", repr(exc))
        raise SystemExit(9)
