#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

from batch29_stage_06390 import build_plan, staged_sources

VERSION = "0.6.40.0"
BATCH = "BATCH30"
TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TR = ROOT / "translation"
INNER = TOOLS / "build_gaia_06140_translation_b5.py"
BASE_READABLE = TOOLS / "build_gaia_06100_hybrid_accent_b1_READABLE.py"
FINAL_MANIFEST = TR / "BATCH29_FINAL_EXACT_SET_0.6.39.0.csv"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
EXPECTED_FINAL = 295


def die(msg):
    raise RuntimeError(msg)


def sha1_file(path: Path):
    h = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            b = f.read(8 * 1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


def snapshot(folder: Path):
    out = {}
    for p in folder.iterdir():
        if p.is_file():
            st = p.stat()
            out[p.resolve()] = (st.st_size, st.st_mtime_ns)
    return out


def changed(folder: Path, before):
    out = []
    for p in folder.iterdir():
        if not p.is_file():
            continue
        rp = p.resolve()
        st = p.stat()
        sig = (st.st_size, st.st_mtime_ns)
        if rp not in before or before[rp] != sig:
            out.append(p)
    return out


def load_base():
    spec = importlib.util.spec_from_file_location("gaia06100_readable", BASE_READABLE)
    if spec is None or spec.loader is None:
        die("Cannot load readable 0.6.10 production source")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if mod.EXPECTED_BIN_SHA1.lower() != CLEAN_SHA1:
        die("Readable 0.6.10 clean SHA contract drift")
    return mod


def final_expected_map():
    out = {}
    for r in read_csv(FINAL_MANIFEST):
        k = key(r)
        text = (r.get("vi_accented") or "").strip()
        if k in out and out[k] != text:
            die(f"Final candidate conflict at {k}: {out[k]!r} vs {text!r}")
        out[k] = text
    if len(out) != EXPECTED_FINAL:
        die(f"Final exact candidate count {len(out)} != {EXPECTED_FINAL}")
    return out


def master_index():
    out = {}
    for p in PARTS:
        for r in read_csv(p):
            k = key(r)
            if k in out:
                die(f"Duplicate original Translation Master key: {k}")
            out[k] = r
    return out


def verify_output(clean_bin: Path, built_bin: Path):
    base = load_base()
    expected = final_expected_map()
    master = master_index()

    with clean_bin.open("rb") as f:
        clean_slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        clean_prg = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)
    codes = base.safe_custom_codes(clean_slps, clean_prg, len(base.CUSTOM_CHARS))
    cmap = dict(zip(base.CUSTOM_CHARS, codes))

    with built_bin.open("rb") as f:
        built_slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        built_prg = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)

    failures = []
    verified = 0
    by_file = {"SLPS_020.75": built_slps, "PRGPACK.BDP": built_prg}
    for k, text in sorted(expected.items(), key=lambda x: (x[0][0], int(x[0][1], 16))):
        src = master.get(k)
        if src is None:
            failures.append(f"missing master source {k}")
            continue
        blob = by_file.get(k[0])
        if blob is None:
            failures.append(f"unsupported exact file {k[0]} at {k[1]}")
            continue
        jp = src.get("japanese") or ""
        orig = jp.encode("cp932")
        encoded, _ = base.encode_runtime_text(text, cmap)
        if len(encoded) > len(orig):
            failures.append(f"expected text over field after production encoding {k}: {len(encoded)}>{len(orig)}")
            continue
        want = encoded + b"\x00" * (len(orig) - len(encoded))
        off = int(k[1], 16)
        got = bytes(blob[off:off + len(orig)])
        if got != want:
            failures.append(
                f"byte mismatch {k[0]} {k[1]} {text!r}: want={want.hex().upper()} got={got.hex().upper()}"
            )
            continue
        verified += 1

    if failures:
        preview = "\n".join(failures[:30])
        die(f"Final exact output verification failed: {len(failures)} row(s)\n{preview}")
    if verified != EXPECTED_FINAL:
        die(f"Final exact verification count {verified} != {EXPECTED_FINAL}")
    return verified


def rename_outputs(out_dir: Path, before, clean_bin: Path):
    renames = []
    current = changed(out_dir, before)
    for p in sorted(current, key=lambda x: len(x.name), reverse=True):
        if not p.exists() or p.resolve() == clean_bin.resolve():
            continue
        new_name = (
            p.name
            .replace("0.6.14.0", VERSION)
            .replace("06140", "06400")
            .replace("BATCH5", BATCH)
        )
        if new_name == p.name:
            continue
        q = p.with_name(new_name)
        if q.exists():
            q.unlink()
        p.rename(q)
        renames.append((p.name, q.name))

    for p in out_dir.glob(f"*{VERSION}*.cue"):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            txt = (
                txt.replace("0.6.14.0", VERSION)
                .replace("06140", "06400")
                .replace("BATCH5", BATCH)
            )
            p.write_text(txt, encoding="utf-8")
        except Exception as e:
            print(f"[WARN] CUE rewrite failed: {p.name}: {e}")
    return renames


def selftest():
    required = [INNER, BASE_READABLE, FINAL_MANIFEST, *PARTS]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        die("Missing Batch30 builder dependencies:\n  " + "\n  ".join(missing))
    plan = build_plan()
    expected = final_expected_map()
    if len(expected) != plan["counts"]["final_verify"]:
        die(f"Final manifest/stage drift: {len(expected)} vs {plan['counts']['final_verify']}")
    base = load_base()
    if not callable(getattr(base, "encode_runtime_text", None)):
        die("Readable 0.6.10 production encoder missing")
    with staged_sources(plan):
        pass
    print("=" * 84)
    print("GAIA MASTER 0.6.40.0 BATCH30 BUILDER SELFTEST PASS")
    print("=" * 84)
    print(f"New exact targets     : {plan['counts']['targets']}")
    print(f"Final exact verify    : {len(expected)}")
    print(f"Legacy shadows        : {plan['counts']['shadows']}")
    print(f"Dynamic sinks         : {plan['counts']['sinks']}")
    print(f"Legacy gate           : {plan['counts']['legacy']}/397")
    print(f"Gameplay masks        : {plan['counts']['gameplay_mask']}")
    print(f"Compact13 masks       : {plan['counts']['compact13_mask']}")
    print(f"Compact14 masks       : {plan['counts']['compact14_mask']}")
    print(f"Global-map preserves  : {plan['counts']['preserve']}")
    print("Source restore        : PASS")
    return 0


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        return selftest()
    if len(sys.argv) > 2:
        print(f"Usage: {Path(sys.argv[0]).name} [CLEAN_GAME.bin] | --selftest")
        return 2

    clean_bin = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) == 2 else (TOOLS / "GaiaMaster - Kamigami no Board Game (Japan).bin")
    if not clean_bin.is_file():
        print("[ERROR] CLEAN Japan BIN not found:")
        print(clean_bin)
        return 2
    got_sha = sha1_file(clean_bin).lower()
    if got_sha != CLEAN_SHA1:
        print(f"[ERROR] Need CLEAN Japan BIN SHA1 {CLEAN_SHA1}; got {got_sha}")
        return 3

    plan = build_plan()
    expected = final_expected_map()
    out_dir = clean_bin.parent
    before = snapshot(out_dir)

    print("=" * 84)
    print("GAIA MASTER 0.6.40.0 - BATCH30 ACCENT SWEEP PRODUCTION BUILD")
    print("=" * 84)
    print(f"Input CLEAN SHA1       : {got_sha}")
    print(f"New exact targets      : {len(plan['targets'])}")
    print(f"Final exact verify set : {len(expected)}")
    print(f"Legacy shadows         : {plan['counts']['shadows']}")
    print(f"Dynamic sinks          : {plan['counts']['sinks']}")
    print(f"Legacy gate contract   : {plan['counts']['legacy']}/397")
    print()

    with staged_sources(plan):
        cp = subprocess.run(
            [sys.executable, str(INNER), str(clean_bin)],
            cwd=str(TOOLS),
            check=False,
        )
        if cp.returncode != 0:
            die(f"Inner 0.6.14.0 production builder failed with exit code {cp.returncode}")

    current = changed(out_dir, before)
    bins = [p for p in current if p.suffix.lower() == ".bin" and p.resolve() != clean_bin]
    bins.sort(key=lambda p: p.stat().st_mtime_ns, reverse=True)
    if not bins:
        die("Inner build succeeded but no changed output BIN was found")
    built_bin = bins[0]

    verified = verify_output(clean_bin, built_bin)
    renames = rename_outputs(out_dir, before, clean_bin)
    final_bins = [p for p in changed(out_dir, before) if p.suffix.lower() == ".bin" and p.resolve() != clean_bin]
    final_bins.sort(key=lambda p: p.stat().st_mtime_ns, reverse=True)
    final_bin = final_bins[0] if final_bins else built_bin

    report = out_dir / f"GaiaMaster_{VERSION}_{BATCH}_FINAL_REPORT.txt"
    lines = [
        f"GAIA MASTER {VERSION} - {BATCH} ACCENT SWEEP PRODUCTION BUILD",
        "=" * 84,
        f"Input CLEAN SHA1: {got_sha}",
        f"Batch29 new exact targets staged: {len(plan['targets'])}",
        f"Final exact fields byte-verified in output BIN: {verified}/{EXPECTED_FINAL}",
        f"Legacy shadow rows: {plan['counts']['shadows']}",
        f"Dynamic sink rows: {plan['counts']['sinks']}",
        f"0.6.11 exact keys masked: {plan['counts']['gameplay_mask']}",
        f"0.6.13 exact keys masked: {plan['counts']['compact13_mask']}",
        f"0.6.14 exact keys masked: {plan['counts']['compact14_mask']}",
        f"Global fallback entries preserved: {plan['counts']['preserve']}",
        f"Legacy Alpha key contract: {plan['counts']['legacy']}/397",
        "Source staging restoration: PASS",
        f"Output BIN: {final_bin.name}",
        "",
        "Architecture unchanged:",
        "- native 12x12 / 72-byte / 4bpp / LOW nibble first",
        "- static mapping-only",
        "- frozen 60-glyph Vietnamese codepage",
        "- no renderer hook / pointer redirect / narrow-font path",
        "",
        "STATUS: BUILD + BYTE VERIFICATION PASS",
        "RUNTIME TEST STILL REQUIRED",
        "The whole-game Japanese scanner is a separate read-only step.",
        "Do not call Runtime PASS until screenshots/logs from actual gameplay are reviewed.",
    ]
    if renames:
        lines += ["", "Renamed inner outputs:"] + [f"- {a} -> {b}" for a, b in renames]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"[OK] {VERSION} {BATCH} production build completed")
    print(f"[OK] Final exact byte verification: {verified}/{EXPECTED_FINAL}")
    print("[OK] Sources restored after staging")
    print(f"Output: {final_bin}")
    print(f"Report: {report}")
    print("[NOTE] Runtime screenshots/logs are still required before Runtime PASS.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("[ERROR]", repr(e))
        raise SystemExit(9)
