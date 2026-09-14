#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only exact CP932 target locator for Gaia Master runtime residuals.

Default target is the runtime-proven chapter card:
    冒険のはじまり

Additional exact Japanese strings can be supplied on the command line. This is
intended for text copied from gameplay screenshots so Story / purchase prompts
can be mapped to exact clean-ROM offsets without guessing.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
BASE = TOOLS / "build_gaia_06100_hybrid_accent_b1_READABLE.py"
CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
DEFAULT_TARGETS = ("冒険のはじまり",)


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
        if got == CLEAN_SHA1:
            return rp
    return None


def load_base():
    spec = importlib.util.spec_from_file_location("gaia06100_readable_target_locator", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load readable production helper")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_all(blob: bytes, needle: bytes):
    pos = 0
    while True:
        pos = blob.find(needle, pos)
        if pos < 0:
            return
        yield pos
        pos += 1


def owner_for(entries, off: int):
    for idx, start, end in entries:
        if start <= off < end:
            return idx, start, end
    return None, None, None


def nul_field(blob: bytes, off: int, max_len=512):
    end = blob.find(b"\0", off, min(len(blob), off + max_len + 1))
    if end < 0:
        return None
    return end - off


def decode_context(blob: bytes, off: int, raw_len: int, radius=48):
    a = max(0, off - radius)
    b = min(len(blob), off + raw_len + radius)
    raw = blob[a:b]
    # Replacement mode is deliberate here: context is diagnostic only.
    text = raw.decode("cp932", errors="replace")
    text = "".join(ch if ch >= " " else " " for ch in text)
    return " ".join(text.split())


def main() -> int:
    if len(sys.argv) < 2:
        print(f'Usage: {Path(sys.argv[0]).name} CLEAN_GAME.bin ["日本語 target" ...]')
        return 2

    clean = find_clean_bin(Path(sys.argv[1]))
    if clean is None:
        print("[ERROR] CLEAN Japan BIN with expected SHA1 not found.")
        print("Expected:", CLEAN_SHA1)
        return 3

    targets = tuple(sys.argv[2:]) or DEFAULT_TARGETS
    base = load_base()
    with clean.open("rb") as f:
        slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        prg = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)
    entries = base.parse_bdp_entries(prg)

    lines = [
        "GAIA MASTER RUNTIME TARGET LOCATOR 0.1",
        "=" * 78,
        f"CLEAN BIN SHA1: {sha1_file(clean)}",
        f"Targets        : {len(targets)}",
        "",
    ]

    total = 0
    for target in targets:
        try:
            needle = target.encode("cp932")
        except UnicodeEncodeError:
            lines += [f"[TARGET] {target}", "  ERROR: not encodable as CP932", ""]
            continue

        hits = []
        for file_name, blob in (("PRGPACK.BDP", prg), ("SLPS_020.75", slps)):
            for off in find_all(blob, needle):
                owner, owner_start, owner_end = owner_for(entries, off) if file_name == "PRGPACK.BDP" else (None, None, None)
                field = nul_field(blob, off)
                hits.append((file_name, blob, off, owner, owner_start, owner_end, field))
        total += len(hits)

        lines.append(f"[TARGET] {target}")
        lines.append(f"  CP932 bytes : {needle.hex(' ')}")
        lines.append(f"  Hits        : {len(hits)}")
        if not hits:
            lines.append("  RESULT      : no exact CP932 hit in PRGPACK.BDP / SLPS_020.75")
        for file_name, blob, off, owner, owner_start, owner_end, field in hits:
            owner_text = "none"
            local_text = ""
            if owner is not None:
                owner_text = str(owner)
                local_text = f" owner_local=0x{off - owner_start:X}"
            field_text = "none" if field is None else str(field)
            lines.append(
                f"  - {file_name}+0x{off:X} owner={owner_text}{local_text} "
                f"nul_field_bytes={field_text}"
            )
            lines.append(f"    context: {decode_context(blob, off, len(needle))}")
        lines.append("")

    lines += [
        f"TOTAL EXACT HITS: {total}",
        "",
        "RULES:",
        "- This is a locator only. A hit is not automatically safe to patch.",
        "- Production promotion still requires CLEAN source identity, owner boundary, NUL/field budget,",
        "  frozen 60-glyph codepage, token-order identity, and no overlap with the 560 Batch42 fields.",
        "- READ ONLY: this tool never patches the BIN.",
    ]

    out = clean.parent / "GaiaMaster_RUNTIME_TARGET_LOCATOR_0.1_REPORT.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("Report:", out)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print("[ERROR]", repr(exc))
        raise SystemExit(9)
