#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only runtime-base finder for Gaia Master B51R1.

Given the exact CLEAN Japan BIN, scan .bin files in a directory and report which
ones satisfy the B51R1 build-base contract:

- raw image size matches CLEAN;
- not the CLEAN image itself;
- PRGPACK BDP parses/checksums correctly;
- frozen 60-glyph runtime mapping is present;
- B40/Batch42 exact fields verify 560/560;
- B43 exact fields verify 102/102 using the historical padded-field contract;
- intro exact text verifies 19/19.

This tool never writes to any BIN.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import build_gaia_b51_guarded_exact_overlay as core  # noqa: E402
import build_gaia_b51r1_guarded_exact_overlay as r1  # noqa: E402


def audit_candidate(path: Path, clean: Path, clean_size: int, cmap: dict[str, int], manifests):
    b40, b43, intro = manifests
    result = {
        "path": path,
        "sha1": None,
        "size": path.stat().st_size,
        "mapping": False,
        "b40": 0,
        "b43": 0,
        "intro": 0,
        "pass": False,
        "reason": "",
    }
    try:
        result["sha1"] = core.hash_file(path)
        if path.resolve() == clean.resolve() or result["sha1"].lower() == core.CLEAN_SHA1:
            result["reason"] = "CLEAN image, not a runtime base"
            return result
        if result["size"] != clean_size:
            result["reason"] = f"raw-image size mismatch {result['size']} != {clean_size}"
            return result

        with path.open("rb") as f:
            slps = core.legacy.read_iso_file(f, core.legacy.SLPS_EXTENT, core.legacy.SLPS_SIZE)
            prg = core.legacy.read_iso_file(f, core.legacy.PRG_EXTENT, core.legacy.PRG_SIZE)
        core.legacy.parse_bdp_entries(prg)

        core.verify_codepage(slps, cmap)
        result["mapping"] = True
        result["b40"] = core.verify_exact_blob(slps, prg, b40, "candidate B40/Batch42")
        result["b43"] = core.verify_exact_blob(slps, prg, b43, "candidate B43")
        result["intro"] = core.verify_exact_blob(slps, prg, intro, "candidate Intro19")
        result["pass"] = True
        result["reason"] = "PASS frozen60 + 560/102/19"
        return result
    except Exception as e:
        result["reason"] = str(e)
        return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Find a proven B51R1 runtime base without modifying files")
    ap.add_argument("clean_bin", type=Path, help="exact CLEAN Japan BIN")
    ap.add_argument("--dir", type=Path, default=None, help="directory containing candidate .bin files")
    ap.add_argument("--recursive", action="store_true", help="scan candidate directory recursively")
    args = ap.parse_args()

    clean = args.clean_bin.expanduser().resolve()
    if not clean.is_file():
        raise RuntimeError(f"CLEAN BIN not found: {clean}")

    clean_sha1, _clean_slps, _clean_prg, cmap = core.read_clean(clean)
    scan_dir = (args.dir or clean.parent).expanduser().resolve()
    if not scan_dir.is_dir():
        raise RuntimeError(f"Candidate directory not found: {scan_dir}")

    # Historical expected bytes only. No B50/B51 writes happen here.
    b40 = r1.load_hist_manifest_r1(core.B40, core.B40_ROWS, cmap)
    b43 = r1.load_hist_manifest_r1(core.B43, core.B43_ROWS, cmap)
    intro = core.intro_manifest(cmap)
    manifests = (b40, b43, intro)

    pattern = "**/*.bin" if args.recursive else "*.bin"
    candidates = sorted(
        (p.resolve() for p in scan_dir.glob(pattern) if p.is_file()),
        key=lambda p: p.name.lower(),
    )
    if not candidates:
        print(f"[ERROR] No .bin files found under: {scan_dir}")
        return 2

    print("GAIA MASTER B51R1 - READ-ONLY RUNTIME BASE FINDER")
    print("=" * 78)
    print("CLEAN SHA1      :", clean_sha1)
    print("Candidate dir   :", scan_dir)
    print("Candidate files :", len(candidates))
    print("Required gates  : frozen60 + B40 560/560 + B43 102/102 + intro 19/19")
    print("")

    results = [audit_candidate(p, clean, clean.stat().st_size, cmap, manifests) for p in candidates]
    good = [r for r in results if r["pass"]]

    for r in results:
        state = "PASS" if r["pass"] else "FAIL"
        print(f"[{state}] {r['path'].name}")
        if r["sha1"]:
            print(f"  SHA1   : {r['sha1']}")
        if r["pass"]:
            print("  frozen : 60/60")
            print(f"  B40    : {r['b40']}/{core.B40_ROWS}")
            print(f"  B43    : {r['b43']}/{core.B43_ROWS}")
            print(f"  intro  : {r['intro']}/{core.INTRO_ROWS}")
        print(f"  reason : {r['reason']}")

    print("")
    if not good:
        print("RESULT: NO VALID B51R1 RUNTIME BASE FOUND")
        print("No files were modified.")
        return 4

    print(f"RESULT: {len(good)} VALID B51R1 RUNTIME BASE(S) FOUND")
    print("Recommended --build-from candidates:")
    for r in good:
        print(f'  "{r["path"]}"')
    print("No files were modified.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("[ERROR]", repr(e))
        raise SystemExit(9)
