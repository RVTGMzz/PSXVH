#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gaia Master read-only PS1 graphic asset census.

Purpose:
- verify the exact CLEAN Japan BIN;
- extract SLPS_020.75 and PRGPACK.BDP in memory;
- enumerate top-level PRGPACK nested BDP owners;
- find structurally valid embedded PS-X TIM images;
- highlight the proven Character Select owner (entry 29) and nearby assets.

This tool NEVER patches the BIN and does not alter the production architecture.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import math
import struct
import sys
from collections import Counter
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
BASE = TOOLS / "build_gaia_06100_hybrid_accent_b1_READABLE.py"
CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"

CHAR_SELECT_OWNER = 29
CHAR_SELECT_TEXT_OFFSETS = (0xBFBEC, 0xBFD2C, 0xBFE4C)
TIM_MAGIC = b"\x10\x00\x00\x00"
MODE_NAMES = {0: "4bpp", 1: "8bpp", 2: "16bpp", 3: "24bpp"}


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().lower()


def find_clean_bin(requested: Path) -> Path | None:
    requested = requested.expanduser().resolve()
    ordered: list[Path] = []
    if requested.is_file() and requested.suffix.lower() == ".bin":
        ordered.append(requested)
    base_dir = requested.parent if requested.suffix else requested
    for root in (base_dir, base_dir.parent):
        if root.exists() and root.is_dir():
            ordered.extend(root.glob("*.bin"))
            ordered.extend(root.glob("*/*.bin"))

    seen: set[Path] = set()
    for p in ordered:
        try:
            rp = p.resolve()
        except OSError:
            continue
        if rp in seen or not rp.is_file():
            continue
        seen.add(rp)
        try:
            got = sha1_file(rp)
        except OSError:
            continue
        print(f"[CHECK] {rp.name}")
        print(f"        SHA1 {got}")
        if got == CLEAN_SHA1:
            print(f"[OK] CLEAN Japan BIN: {rp}")
            return rp
    return None


def load_base():
    spec = importlib.util.spec_from_file_location("gaia06100_readable_asset_census", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load readable production helper")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def entropy(blob: bytes) -> float:
    if not blob:
        return 0.0
    n = len(blob)
    counts = Counter(blob)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def parse_block(blob: bytes, off: int):
    if off + 12 > len(blob):
        return None
    size = struct.unpack_from("<I", blob, off)[0]
    if size < 12 or off + size > len(blob):
        return None
    x, y, w, h = struct.unpack_from("<HHHH", blob, off + 4)
    if not w or not h:
        return None
    # TIM rectangles are expressed in 16-bit words. Keep bounds conservative.
    if x >= 1024 or y >= 512 or w > 1024 or h > 512:
        return None
    expected = 12 + (w * h * 2)
    if size != expected:
        return None
    return {"size": size, "x": x, "y": y, "w_words": w, "h": h}


def parse_tim_at(blob: bytes, off: int):
    if off + 8 > len(blob) or blob[off:off + 4] != TIM_MAGIC:
        return None
    flags = struct.unpack_from("<I", blob, off + 4)[0]
    # Standard PS-X TIM uses only mode bits 0..2 and CLUT flag bit 3.
    if flags & ~0xF:
        return None
    mode = flags & 0x7
    if mode not in MODE_NAMES:
        return None
    has_clut = bool(flags & 0x8)
    pos = off + 8
    clut = None
    if has_clut:
        clut = parse_block(blob, pos)
        if clut is None:
            return None
        # Do not cap total CLUT entries: valid TIMs may carry multiple palettes.
        # Structural block-size and VRAM geometry checks above remain the gate.
        pos += clut["size"]

    image = parse_block(blob, pos)
    if image is None:
        return None
    pos += image["size"]

    words = image["w_words"]
    if mode == 0:
        pixel_width = words * 4
    elif mode == 1:
        pixel_width = words * 2
    elif mode == 2:
        pixel_width = words
    else:
        # 24bpp stores 3 bytes/pixel in a 16-bit-word row width.
        pixel_width = (words * 2) // 3

    if pixel_width <= 0 or pixel_width > 4096:
        return None

    return {
        "offset": off,
        "end": pos,
        "total_bytes": pos - off,
        "flags": flags,
        "mode": MODE_NAMES[mode],
        "has_clut": has_clut,
        "clut_x": "" if clut is None else clut["x"],
        "clut_y": "" if clut is None else clut["y"],
        "clut_w": "" if clut is None else clut["w_words"],
        "clut_h": "" if clut is None else clut["h"],
        "img_x": image["x"],
        "img_y": image["y"],
        "img_w_words": words,
        "img_h": image["h"],
        "pixel_width": pixel_width,
    }


def scan_tim(blob: bytes):
    out = []
    pos = 0
    while True:
        pos = blob.find(TIM_MAGIC, pos)
        if pos < 0:
            break
        cand = parse_tim_at(blob, pos)
        if cand is not None:
            out.append(cand)
            # Do not skip to the end: nested/adjacent headers can still be useful.
        pos += 1
    return out


def owner_index(entries, off: int):
    for idx, start, end in entries:
        if start <= off < end:
            return idx, start, end
    return None, None, None


def proximity_tag(off: int, owner):
    if owner == CHAR_SELECT_OWNER:
        distance = min(abs(off - t) for t in CHAR_SELECT_TEXT_OFFSETS)
        if distance <= 0x4000:
            return "CHAR_SELECT_OWNER_NEAR_TEXT"
        return "CHAR_SELECT_OWNER"
    return ""


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} CLEAN_GAME.bin")
        return 2

    requested = Path(sys.argv[1])
    clean = find_clean_bin(requested)
    if clean is None:
        print("[ERROR] CLEAN Japan BIN with expected SHA1 not found.")
        print("Expected:", CLEAN_SHA1)
        return 3

    base = load_base()
    with clean.open("rb") as f:
        slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        prg = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)

    if hashlib.sha1(slps).hexdigest().lower() != base.EXPECTED_SLPS_SHA1:
        raise RuntimeError("SLPS clean hash mismatch")
    if hashlib.sha1(prg).hexdigest().lower() != base.EXPECTED_PRG_SHA1:
        raise RuntimeError("PRGPACK clean hash mismatch")

    entries = base.parse_bdp_entries(prg)

    # Per-owner census.
    owner_rows = []
    for idx, start, end in entries:
        block = prg[start:end]
        tims = scan_tim(block)
        owner_rows.append({
            "owner": idx,
            "start_hex": f"0x{start:X}",
            "end_hex": f"0x{end:X}",
            "size": end - start,
            "entropy": f"{entropy(block):.4f}",
            "tim_count": len(tims),
            "char_select_owner": "YES" if idx == CHAR_SELECT_OWNER else "NO",
        })

    tim_rows = []
    for file_name, blob in (("PRGPACK.BDP", prg), ("SLPS_020.75", slps)):
        entries_for_file = entries if file_name == "PRGPACK.BDP" else []
        for t in scan_tim(blob):
            owner, owner_start, owner_end = owner_index(entries_for_file, t["offset"])
            row = {
                "file": file_name,
                "offset_hex": f"0x{t['offset']:X}",
                "end_hex": f"0x{t['end']:X}",
                "total_bytes": t["total_bytes"],
                "owner": "" if owner is None else owner,
                "owner_local_hex": "" if owner_start is None else f"0x{t['offset'] - owner_start:X}",
                "mode": t["mode"],
                "has_clut": "YES" if t["has_clut"] else "NO",
                "pixel_width": t["pixel_width"],
                "height": t["img_h"],
                "img_x": t["img_x"],
                "img_y": t["img_y"],
                "img_w_words": t["img_w_words"],
                "clut_x": t["clut_x"],
                "clut_y": t["clut_y"],
                "clut_w": t["clut_w"],
                "clut_h": t["clut_h"],
                "target_tag": proximity_tag(t["offset"], owner),
            }
            tim_rows.append(row)

    out_dir = clean.parent
    owners_csv = out_dir / "GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_OWNERS.csv"
    tim_csv = out_dir / "GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_TIM.csv"
    report = out_dir / "GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_REPORT.txt"

    with owners_csv.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["owner", "start_hex", "end_hex", "size", "entropy", "tim_count", "char_select_owner"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(owner_rows)

    with tim_csv.open("w", encoding="utf-8-sig", newline="") as f:
        fields = [
            "file", "offset_hex", "end_hex", "total_bytes", "owner", "owner_local_hex",
            "mode", "has_clut", "pixel_width", "height", "img_x", "img_y", "img_w_words",
            "clut_x", "clut_y", "clut_w", "clut_h", "target_tag",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(tim_rows)

    tagged = [r for r in tim_rows if r["target_tag"]]
    owner29 = next((r for r in owner_rows if r["owner"] == CHAR_SELECT_OWNER), None)
    lines = [
        "GAIA MASTER GRAPHIC ASSET CENSUS 0.1",
        "=" * 78,
        f"CLEAN BIN SHA1        : {sha1_file(clean)}",
        f"PRGPACK BDP owners    : {len(entries)}",
        f"Valid TIM candidates  : {len(tim_rows)}",
        f"Character Select owner: {CHAR_SELECT_OWNER}",
        f"Owner 29 size         : {owner29['size'] if owner29 else 'NOT FOUND'}",
        f"Owner 29 TIM count    : {owner29['tim_count'] if owner29 else 'NOT FOUND'}",
        f"Target-tagged TIMs    : {len(tagged)}",
        "",
        "TARGET-TAGGED TIM CANDIDATES:",
    ]
    if tagged:
        for r in tagged[:100]:
            lines.append(
                f"- {r['file']}+{r['offset_hex']} owner={r['owner']} "
                f"local={r['owner_local_hex']} {r['mode']} "
                f"{r['pixel_width']}x{r['height']} {r['target_tag']}"
            )
    else:
        lines.append("- none")
    lines += [
        "",
        "INTERPRETATION:",
        "- A hit is a structurally valid standard PS-X TIM candidate, not proof of on-screen ownership.",
        "- Entry 29 is highlighted because Character Select text ownership is already proven there.",
        "- No hit in entry 29 means the remaining UI may use raw/custom/compressed graphics, not that it is text.",
        "- READ ONLY: this tool never patches the BIN.",
        "",
        f"Owners CSV: {owners_csv.name}",
        f"TIM CSV   : {tim_csv.name}",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print("[ERROR]", repr(exc))
        raise SystemExit(9)
