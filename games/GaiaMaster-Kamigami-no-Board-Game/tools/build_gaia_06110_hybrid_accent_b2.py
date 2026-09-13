#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaia Master 0.6.11.0
Hybrid Full-Coverage + Gameplay Accent Batch 2 wrapper.

This intentionally reuses the exact 0.6.10.0 builder so the frozen 0.6.7.2 font,
the 60-glyph codepage, BDP/checksum logic, and the exact 397/397 legacy coverage
gate stay unchanged.

What this wrapper adds:
- Front cleanup from the 0.6.10.0 runtime screenshots.
- Compact accented gameplay/card/menu/item overrides, only when they fit.
- Safe, exact dynamic-literal replacement for known Japanese %s names.
- Automatic restoration of all repository CSV sources after the build.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import zipfile

VERSION = "0.6.11.0"
CLEAN_BIN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TR = ROOT / "translation"

BASE_BUILDER = TOOLS / "build_gaia_06100_hybrid_accent_b1.py"
LIVE_FRONT = TR / "FRONT_ACCENT_OVERRIDES_0.6.10.0.csv"
NEW_FRONT = TR / "FRONT_ACCENT_OVERRIDES_0.6.11.0.csv"
GAMEPLAY_OVR = TR / "GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv"
DYNAMIC_OVR = TR / "DYNAMIC_LITERAL_OVERRIDES_0.6.11.0.csv"
MASTER_PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]

FILES = {
    "SLPS_020.75": (24, 487424),
    "PRGPACK.BDP": (2679, 1534236),
}

FROZEN_CUSTOM = set(
    "àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ"
)

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


def runtime_len_estimate(text: str) -> int:
    n = 0
    pos = 0
    for m in RAW_TOKEN_RE.finditer(text):
        n += (m.start() - pos) * 2
        n += len(m.group(0).encode("ascii"))
        pos = m.end()
    n += (len(text) - pos) * 2
    return n


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        rows = list(r)
        if not r.fieldnames:
            die(f"No CSV header: {path}")
        return r.fieldnames, rows


def write_csv(path: Path, fieldnames, rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
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
        out.extend(bin_bytes[user:user + need])
    return bytes(out)


def find_all(haystack: bytes, needle: bytes):
    start = 0
    while True:
        p = haystack.find(needle, start)
        if p < 0:
            return
        yield p
        start = p + 1


def standalone_string_boundary(data: bytes, off: int, n: int) -> bool:
    before_ok = off == 0 or data[off - 1] == 0
    after = off + n
    after_ok = after >= len(data) or data[after] == 0
    return before_ok and after_ok


def snapshot_dir(d: Path):
    snap = {}
    for p in d.iterdir():
        if p.is_file():
            try:
                st = p.stat()
                snap[p.name] = (st.st_mtime_ns, st.st_size)
            except OSError:
                pass
    return snap


def changed_files(d: Path, before):
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


def versioned_name(name: str) -> str:
    return (
        name.replace("0.6.10.0", "0.6.11.0")
            .replace("06100", "06110")
            .replace("HYBRID_FRONT_ACCENT_BATCH1", "HYBRID_GAMEPLAY_ACCENT_BATCH2")
            .replace("HYBRID_ACCENT_B1", "HYBRID_ACCENT_B2")
            .replace("FRONT_ACCENT_BATCH1", "GAMEPLAY_ACCENT_BATCH2")
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: drag CLEAN Gaia Master BIN onto 00_BUILD_0.6.11.0_HYBRID_ACCENT_B2.cmd")
        return 2

    clean_bin = Path(sys.argv[1]).expanduser().resolve()
    if not clean_bin.is_file():
        die(f"Input does not exist: {clean_bin}")

    got_sha = sha1_file(clean_bin)
    if got_sha.lower() != CLEAN_BIN_SHA1:
        die(f"Need CLEAN Japan BIN SHA1 {CLEAN_BIN_SHA1}; got {got_sha}")

    required = [BASE_BUILDER, LIVE_FRONT, NEW_FRONT, GAMEPLAY_OVR, DYNAMIC_OVR, *MASTER_PARTS]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        die("Missing source files:\n  " + "\n  ".join(missing))

    _, ovr_rows = read_csv(GAMEPLAY_OVR)
    gameplay = {}
    for r in ovr_rows:
        key = (r["file"].strip(), norm_off(r["offset_hex"]))
        if key in gameplay:
            die(f"Duplicate gameplay override {key}")
        text = r["vi_accented"].strip()
        validate_text(text, f"{GAMEPLAY_OVR.name}:{key}")
        gameplay[key] = (text, r.get("category", ""), r.get("note", ""))

    _, front_rows = read_csv(NEW_FRONT)
    if len(front_rows) != 31:
        die(f"Front Batch 2 cleanup must still contain exactly 31 rows; got {len(front_rows)}")
    for r in front_rows:
        validate_text(r["vi_accented"], f"{NEW_FRONT.name}:{r['offset_hex']}")

    part_data = {}
    seen_keys = set()
    applied = []
    too_long = []
    for path in MASTER_PARTS:
        fields, rows = read_csv(path)
        for r in rows:
            key = (r["file"].strip(), norm_off(r["offset_hex"]))
            seen_keys.add(key)
            if key not in gameplay:
                continue
            text, cat, note = gameplay[key]
            jp = r["japanese"]
            old_len = len(jp.encode("cp932"))
            new_len = runtime_len_estimate(text)
            if new_len <= old_len:
                r["vi_full"] = text
                applied.append((key, text, new_len, old_len, cat))
            else:
                too_long.append((key, text, new_len, old_len, cat))
        part_data[path] = (fields, rows)

    missing_keys = sorted(set(gameplay) - seen_keys)

    clean_bytes = clean_bin.read_bytes()
    extracted = {name: extract_extent(clean_bytes, ext, size)
                 for name, (ext, size) in FILES.items()}

    _, dyn_rows = read_csv(DYNAMIC_OVR)
    dynamic_injected = []
    dynamic_ignored = []
    append_path = MASTER_PARTS[-1]
    append_fields, append_rows = part_data[append_path]
    existing = {(r["file"].strip(), norm_off(r["offset_hex"])) for r in append_rows}

    for r in dyn_rows:
        jp = r["japanese"]
        vi = r["vi_accented"].strip()
        scope = (r.get("file_scope") or "AUTO").strip()
        validate_text(vi, f"{DYNAMIC_OVR.name}:{jp}")
        jp_b = jp.encode("cp932")
        new_len = runtime_len_estimate(vi)
        if new_len > len(jp_b):
            dynamic_ignored.append((jp, vi, "replacement-too-long"))
            continue
        names = list(FILES) if scope.upper() == "AUTO" else [scope]
        for name in names:
            if name not in extracted:
                die(f"Unknown dynamic file scope {name!r}")
            data = extracted[name]
            for off in find_all(data, jp_b):
                if new_len != len(jp_b) and not standalone_string_boundary(data, off, len(jp_b)):
                    dynamic_ignored.append((jp, vi, f"{name}+{hex(off)} non-standalone"))
                    continue
                key = (name, hex(off))
                if key in existing or key in seen_keys:
                    found = False
                    for path, (fields, rows) in part_data.items():
                        for rr in rows:
                            if (rr["file"].strip(), norm_off(rr["offset_hex"])) == key:
                                rr["vi_full"] = vi
                                dynamic_injected.append((key, jp, vi, "existing-row"))
                                found = True
                                break
                        if found:
                            break
                    continue
                append_rows.append({
                    "file": name,
                    "offset_hex": hex(off),
                    "japanese": jp,
                    "vi_full": vi,
                    "vi_game_current": "",
                    "status": "BATCH2_DYNAMIC",
                    "note": r.get("note", ""),
                })
                existing.add(key)
                dynamic_injected.append((key, jp, vi, "new-row"))

    backups = {p: p.read_bytes() for p in [LIVE_FRONT, *MASTER_PARTS]}
    out_dir = clean_bin.parent
    before = snapshot_dir(out_dir)

    try:
        LIVE_FRONT.write_bytes(NEW_FRONT.read_bytes())
        for path, (fields, rows) in part_data.items():
            write_csv(path, fields, rows)

        print("=" * 78)
        print("GAIA MASTER 0.6.11.0 - HYBRID GAMEPLAY ACCENT BATCH 2")
        print("=" * 78)
        print("Font: 0.6.7.2 FROZEN (unchanged)")
        print(f"Gameplay override candidates : {len(gameplay)}")
        print(f"Static compact-fit promoted  : {len(applied)}")
        print(f"Static too-long kept fallback: {len(too_long)}")
        print(f"Missing override keys        : {len(missing_keys)}")
        print(f"Dynamic literals injected    : {len(dynamic_injected)}")
        print()
        if missing_keys:
            print("[WARN] Override keys absent from current Translation Master:")
            for k in missing_keys:
                print("  ", k)
            print()
        if too_long:
            print("[INFO] Too-long compact candidates were NOT forced; old fallback stays.")
            print("       This preserves coverage instead of trading coverage for accents.")
            print()

        cp = subprocess.run(
            [sys.executable, str(BASE_BUILDER), str(clean_bin)],
            cwd=str(TOOLS),
            check=False,
        )
        if cp.returncode != 0:
            die(f"Inner 0.6.10.0 exact builder failed with exit code {cp.returncode}")
    finally:
        for p, data in backups.items():
            try:
                p.write_bytes(data)
            except Exception as e:
                print(f"[CRITICAL] Failed to restore {p}: {e}", file=sys.stderr)

    changed = changed_files(out_dir, before)
    renamed = []
    for p in list(changed):
        if p.resolve() == clean_bin:
            continue
        new_name = versioned_name(p.name)
        if new_name != p.name:
            q = p.with_name(new_name)
            if q.exists():
                q.unlink()
            p.rename(q)
            renamed.append((p.name, q.name))

    final_changed = changed_files(out_dir, before)
    for p in final_changed:
        if p.suffix.lower() == ".cue":
            try:
                s = p.read_text(encoding="utf-8", errors="replace")
                s2 = versioned_name(s)
                if s2 != s:
                    p.write_text(s2, encoding="utf-8")
            except Exception as e:
                print(f"[WARN] Could not rewrite CUE {p.name}: {e}")

    report = out_dir / "GaiaMaster_0.6.11.0_B2_WRAPPER_REPORT.txt"
    lines = [
        "GAIA MASTER 0.6.11.0 - HYBRID GAMEPLAY ACCENT BATCH 2",
        "=" * 78,
        f"Input CLEAN BIN SHA1: {got_sha}",
        "Font baseline: 0.6.7.2 FROZEN / unchanged",
        "Inner builder: exact 0.6.10.0 snapshot (keeps exact 397/397 legacy gate)",
        "",
        f"Gameplay override candidates: {len(gameplay)}",
        f"Static compact-fit promoted: {len(applied)}",
        f"Static too-long kept fallback: {len(too_long)}",
        f"Missing override keys: {len(missing_keys)}",
        f"Dynamic literals injected: {len(dynamic_injected)}",
        f"Dynamic ignored: {len(dynamic_ignored)}",
        "",
        "Runtime fixes targeted:",
        "- remove unsafe '=' from intro lines",
        "- replace 'Tải dữ liệu VK?' with 'Tải KN vũ khí?'",
        "- upgrade DUNG %s -> Dừng %s",
        "- replace トロル通り -> Troll when found safely",
        "- accent-upgrade compact card/menu/item/gameplay fallback rows that fit",
        "",
        "IMPORTANT: candidates that do not fit are intentionally NOT forced.",
        "The old fallback remains so 397/397 coverage is never sacrificed for accents.",
        "",
        "RENAMED OUTPUTS:",
    ]
    lines += [f"- {a} -> {b}" for a, b in renamed] or ["- none detected"]
    if missing_keys:
        lines += ["", "MISSING OVERRIDE KEYS:"] + [f"- {k[0]} {k[1]}" for k in missing_keys]
    if dynamic_injected:
        lines += ["", "DYNAMIC INJECTED:"] + [
            f"- {k[0]} {k[1]}: {jp} -> {vi} ({mode})"
            for k, jp, vi, mode in dynamic_injected
        ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    candidates = []
    for p in changed_files(out_dir, before):
        if p.resolve() == clean_bin:
            continue
        if p.suffix.lower() in {".bin", ".cue", ".txt"}:
            candidates.append(p)
    package = out_dir / "GaiaMaster_0.6.11.0_HYBRID_GAMEPLAY_ACCENT_BATCH2.zip"
    if candidates:
        with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for p in sorted(set(candidates)):
                z.write(p, arcname=p.name)
        print(f"[PACKAGE] {package}")
    else:
        print("[WARN] No BIN/CUE/TXT build outputs detected for automatic packaging.")

    print()
    print("[PASS] Inner exact builder completed. Repository CSV sources restored.")
    print("[NEXT RUNTIME] intro cleanup -> setup wording -> Dừng Troll -> card/menu/item.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
