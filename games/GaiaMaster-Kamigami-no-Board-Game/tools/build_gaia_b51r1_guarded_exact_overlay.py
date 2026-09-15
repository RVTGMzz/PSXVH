#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gaia Master B51R1 guarded exact-offset overlay.

B51R1 keeps canonical B50 immutable and applies a 64-row TEXT-ONLY correction
layer for runtime candidates that use Vietnamese glyphs outside the frozen
60-glyph production codepage.

No glyphs are added. No font/mapping bytes are changed. All B51 CLEAN-source,
overlap, historical-regression, BDP checksum and raw-sector guards are inherited.

Usage:
  python build_gaia_b51r1_guarded_exact_overlay.py CLEAN.bin
  python build_gaia_b51r1_guarded_exact_overlay.py CLEAN.bin --build-from BASE.bin

Runtime PASS is never claimed here.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TR = ROOT / "translation" / "source_layer"
CORRECTIONS = TR / "B51_RUNTIME_CHARSET_CORRECTIONS.csv"
EXPECTED_CORRECTIONS = 64

sys.path.insert(0, str(TOOLS))
import build_gaia_b51_guarded_exact_overlay as core  # noqa: E402


def load_corrections():
    fields, rows = core.read_csv(CORRECTIONS)
    want_fields = ["file", "offset_hex", "old_candidate", "new_candidate", "reason"]
    if fields != want_fields:
        raise RuntimeError(f"B51R1 correction schema drift: {fields!r}")
    if len(rows) != EXPECTED_CORRECTIONS:
        raise RuntimeError(f"B51R1 correction row gate: {len(rows)} != {EXPECTED_CORRECTIONS}")

    out = {}
    for line, r in enumerate(rows, 2):
        name = (r.get("file") or "").strip()
        if name not in {"PRGPACK.BDP", "SLPS_020.75"}:
            raise RuntimeError(f"Correction line {line}: unsupported file {name!r}")
        off = core.parse_int(r.get("offset_hex") or "", f"correction line {line} offset")
        old = r.get("old_candidate") or ""
        new = r.get("new_candidate") or ""
        if not old or not new or old == new:
            raise RuntimeError(f"Correction line {line}: invalid old/new candidate")
        if (r.get("reason") or "").strip() != "frozen60":
            raise RuntimeError(f"Correction line {line}: unexpected reason")
        key = (name, off)
        if key in out:
            raise RuntimeError(f"Duplicate B51R1 correction key: {key}")
        out[key] = (old, new)
    return out


def load_b50_r1(cmap: dict[str, int]):
    """Load canonical B50 while applying exact-key text-only corrections."""
    fields, raw_rows = core.read_csv(core.RESTORED)
    if fields != core.EXPECTED_B50_HEADER:
        raise RuntimeError(f"B50 schema drift:\nwant={core.EXPECTED_B50_HEADER}\ngot ={fields}")
    if len(raw_rows) != core.B50_ROWS:
        raise RuntimeError(f"B50 row gate: {len(raw_rows)} != {core.B50_ROWS}")

    corrections = load_corrections()
    seen = set()
    used = set()
    out = []
    direct = compact = 0

    for line, r in enumerate(raw_rows, 2):
        name = (r.get("file") or "").strip()
        off = core.parse_int(r.get("offset_hex") or "", f"B50 line {line} offset")
        key = (name, off)
        if key in seen:
            raise RuntimeError(f"B50 duplicate key: {name}+0x{off:X}")
        seen.add(key)

        jp = r.get("japanese") or ""
        raw_vi = r.get("vi_runtime_candidate") or ""
        if not jp or not raw_vi:
            raise RuntimeError(f"B50 line {line}: blank source/candidate")
        if name not in {"PRGPACK.BDP", "SLPS_020.75"}:
            raise RuntimeError(f"B50 line {line}: bad file {name!r}")

        field = core.parse_int(r.get("field_bytes") or "", f"B50 line {line} field")
        jp_bytes = jp.encode("cp932")
        if field != len(jp_bytes):
            raise RuntimeError(f"B50 line {line}: field {field} != CP932 {len(jp_bytes)}")

        declared = core.parse_int(
            r.get("runtime_candidate_bytes") or "", f"B50 line {line} runtime bytes"
        )
        declared_free = core.parse_int(
            r.get("free_bytes") or "", f"B50 line {line} free bytes"
        )
        if declared + declared_free != field:
            raise RuntimeError(f"B50 line {line}: declared byte/free conservation failed")

        vi = raw_vi
        if key in corrections:
            old, new = corrections[key]
            if raw_vi != old:
                raise RuntimeError(
                    f"B51R1 correction source mismatch {name}+0x{off:X}: "
                    f"B50={raw_vi!r} correction_old={old!r}"
                )
            vi = new
            used.add(key)

        if core.tokens(jp) != core.tokens(vi):
            raise RuntimeError(
                f"B51R1 token order mismatch {name}+0x{off:X}: "
                f"{core.tokens(jp)} != {core.tokens(vi)}"
            )
        enc = core.encode_runtime(vi, cmap)
        if len(enc) > field:
            raise RuntimeError(f"B51R1 overflow {name}+0x{off:X}: {len(enc)}>{field}")

        if key in corrections:
            # Correction may only preserve or reduce the already-approved B50
            # runtime budget. This prevents charset cleanup from becoming a
            # stealth field-expansion pass.
            if len(enc) > declared:
                raise RuntimeError(
                    f"B51R1 correction expands B50 budget {name}+0x{off:X}: "
                    f"{len(enc)}>{declared}"
                )
        else:
            if len(enc) != declared or field - len(enc) != declared_free:
                raise RuntimeError(
                    f"Unchanged B50 byte gate drift {name}+0x{off:X}: "
                    f"encoded={len(enc)} declared={declared} free={declared_free}"
                )

        status = (r.get("production_status") or "").strip()
        if status == "DIRECT_FIT_VI_FULL":
            direct += 1
        elif core.COMPACT_STATUS_RE.match(status):
            compact += 1
        else:
            raise RuntimeError(f"B50 line {line}: unexpected production_status {status!r}")

        out.append(core.PatchRow(line, name, off, jp, vi, field, enc, status))

    missing = sorted(set(corrections) - used)
    if missing:
        raise RuntimeError(f"B51R1 corrections not matched in B50: {missing[:8]}")
    if len(used) != EXPECTED_CORRECTIONS:
        raise RuntimeError(f"B51R1 matched corrections: {len(used)} != {EXPECTED_CORRECTIONS}")
    if direct != core.B50_DIRECT or compact != core.B50_COMPACT:
        raise RuntimeError(
            f"B50 production split drift: {direct}/{compact} != "
            f"{core.B50_DIRECT}/{core.B50_COMPACT}"
        )

    for name in ("PRGPACK.BDP", "SLPS_020.75"):
        xs = sorted((p for p in out if p.file == name), key=lambda p: p.offset)
        for a, b in zip(xs, xs[1:]):
            if b.offset < a.end:
                raise RuntimeError(
                    f"B51R1 overlap {name}: 0x{a.offset:X}..0x{a.end:X} with 0x{b.offset:X}"
                )
    return out


def dry_run_r1(clean: Path):
    clean_sha1, clean_slps, clean_prg, cmap = core.read_clean(clean)
    core.restore_b50()
    rows = load_b50_r1(cmap)
    prg_n, slps_n = core.source_identity_gate(rows, clean_slps, clean_prg)
    b40, b43, intro, eq, counts, masters = core.static_contracts(rows, cmap)
    return dict(
        clean_sha1=clean_sha1,
        clean_slps=clean_slps,
        clean_prg=clean_prg,
        cmap=cmap,
        rows=rows,
        prg_n=prg_n,
        slps_n=slps_n,
        b40=b40,
        b43=b43,
        intro=intro,
        equivalent=eq,
        counts=counts,
        masters=masters,
    )


def make_report_r1(dry, mode, base=None, out=None, changed=0, owners=0, verify=None):
    lines = core.make_report(dry, mode, base, out, changed, owners, verify)
    lines[0] = "GAIA MASTER B51R1 - GUARDED EXACT-OFFSET + FROZEN60 TEXT CORRECTIONS"
    insert_at = 7
    lines[insert_at:insert_at] = [
        f"B51R1 charset corrections            : {EXPECTED_CORRECTIONS}/{EXPECTED_CORRECTIONS}",
        "B50 canonical checkpoint mutated     : NO",
        "New font glyphs added                 : 0",
    ]
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("clean_bin", type=Path)
    ap.add_argument("--build-from", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args()

    clean = args.clean_bin.expanduser().resolve()
    if not clean.is_file():
        raise RuntimeError(f"CLEAN BIN not found: {clean}")

    dry = dry_run_r1(clean)
    report = (
        args.report.expanduser().resolve()
        if args.report
        else clean.parent / "GaiaMaster_B51R1_GUARDED_EXACT_OVERLAY_REPORT.txt"
    )

    if args.build_from is None:
        lines = make_report_r1(dry, "B51R1 GUARDED DRY-RUN PASS")
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(lines)); print("Report:", report)
        return 0

    base = args.build_from.expanduser().resolve()
    if not base.is_file():
        raise RuntimeError(f"Build base not found: {base}")
    if base.resolve() == clean.resolve():
        raise RuntimeError("B51R1 is text-only. --build-from must not be CLEAN.bin")
    if base.stat().st_size != clean.stat().st_size:
        raise RuntimeError("Build base raw-image size mismatch")

    with base.open("rb") as f:
        base_slps = core.legacy.read_iso_file(f, core.legacy.SLPS_EXTENT, core.legacy.SLPS_SIZE)
        base_prg = core.legacy.read_iso_file(f, core.legacy.PRG_EXTENT, core.legacy.PRG_SIZE)
    core.legacy.parse_bdp_entries(base_prg)
    if core.verify_codepage(base_slps, dry["cmap"]) != 60:
        raise RuntimeError("Frozen codepage gate")

    core.verify_exact_blob(base_slps, base_prg, dry["b40"], "BASE B40/Batch42")
    core.verify_exact_blob(base_slps, base_prg, dry["b43"], "BASE B43")
    core.verify_exact_blob(base_slps, base_prg, dry["intro"], "BASE Intro19")

    slps_new, prg_new, touched, atlas_before, mapping_before = core.apply_overlay(
        dry["rows"], dry["clean_slps"], dry["clean_prg"], base_slps, base_prg
    )
    out = (
        args.output.expanduser().resolve()
        if args.output
        else base.with_name(base.stem + " [B51R1 EXACT OVERLAY].bin")
    )
    if out.resolve() in {clean.resolve(), base.resolve()}:
        raise RuntimeError("Output must not overwrite CLEAN/base")
    if out.exists(): out.unlink()
    shutil.copyfile(base, out)

    changed = set()
    with out.open("r+b") as f:
        core.legacy.write_changed_iso_file(
            f, core.legacy.SLPS_EXTENT, base_slps, slps_new, changed
        )
        core.legacy.write_changed_iso_file(
            f, core.legacy.PRG_EXTENT, base_prg, prg_new, changed
        )
        for sec in sorted(changed):
            f.seek(sec * 2352)
            raw = f.read(2352)
            f.seek(sec * 2352)
            f.write(core.legacy.regen_sector(raw))

    verified = core.verify_b51_output(out, dry, atlas_before, mapping_before)
    cue = out.with_suffix(".cue")
    cue.write_text(
        f'FILE "{out.name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n',
        encoding="ascii",
    )
    lines = make_report_r1(
        dry,
        "B51R1 GUARDED BUILD + STATIC BYTE VERIFICATION PASS",
        base,
        out,
        len(changed),
        len(touched),
        verified,
    )
    lines.append(f"Output CUE                          : {cue}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines)); print("Report:", report)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("[ERROR]", repr(e))
        raise SystemExit(9)
