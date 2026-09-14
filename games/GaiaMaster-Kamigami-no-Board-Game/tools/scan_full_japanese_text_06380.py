#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
from pathlib import Path

VERSION = "0.6.38.0"
TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TR = ROOT / "translation"
BASE = TOOLS / "build_gaia_06100_hybrid_accent_b1_READABLE.py"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"

ANCHORS = (
    "メモリーカード",
    "ようし",
    "同じエリア",
    "バトルカード",
    "終了ターン",
)


def sha1_file(path: Path):
    h = hashlib.sha1()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def find_clean_bin(requested: Path):
    requested = requested.expanduser().resolve()
    seen = set()

    def candidates_in(root: Path):
        if not root.exists() or not root.is_dir():
            return []
        items = []
        items.extend(root.glob("*.bin"))
        items.extend(root.glob("*/*.bin"))
        return items

    ordered = []
    if requested.is_file() and requested.suffix.lower() == ".bin":
        ordered.append(requested)

    base_dir = requested.parent if requested.suffix else requested
    roots = [base_dir]
    if base_dir.parent != base_dir:
        roots.append(base_dir.parent)

    for root in roots:
        ordered.extend(candidates_in(root))

    for p in ordered:
        try:
            rp = p.resolve()
        except Exception:
            continue
        if rp in seen or not rp.is_file():
            continue
        seen.add(rp)
        try:
            got = sha1_file(rp).lower()
        except OSError:
            continue
        print(f"[CHECK] {rp.name}")
        print(f"        SHA1 {got}")
        if got == CLEAN_SHA1:
            print("[OK] Tim thay CLEAN Japan BIN dung SHA1:")
            print("     ", rp)
            return rp
    return None


def load_base():
    spec = importlib.util.spec_from_file_location("gaia06100_readable", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load readable production helper")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def csv_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def master_indexes():
    by_key = {}
    by_jp = set()
    for p in PARTS:
        for r in csv_rows(p):
            fn = (r.get("file") or "").strip()
            off = int((r.get("offset_hex") or "0"), 0)
            jp = (r.get("japanese") or "")
            by_key[(fn, off)] = jp
            if jp:
                by_jp.add(jp)
    return by_key, by_jp


def is_sjis_lead(b: int) -> bool:
    return 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC


def is_sjis_trail(b: int) -> bool:
    return 0x40 <= b <= 0xFC and b != 0x7F


def next_unit(blob: bytes, pos: int):
    if pos >= len(blob):
        return None
    b = blob[pos]
    if 0x20 <= b <= 0x7E:
        return bytes([b]), 1
    if 0xA1 <= b <= 0xDF:
        return bytes([b]), 1
    if is_sjis_lead(b) and pos + 1 < len(blob) and is_sjis_trail(blob[pos + 1]):
        raw = blob[pos:pos+2]
        try:
            raw.decode("cp932")
        except Exception:
            return None
        return raw, 2
    return None


def is_kana(ch: str) -> bool:
    o = ord(ch)
    return 0x3040 <= o <= 0x30FF or 0xFF66 <= o <= 0xFF9D


def is_kanji(ch: str) -> bool:
    o = ord(ch)
    return 0x3400 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF


def is_jp_punct(ch: str) -> bool:
    o = ord(ch)
    return 0x3000 <= o <= 0x303F or 0xFF01 <= o <= 0xFF65


def score_text(text: str):
    kana = sum(is_kana(ch) for ch in text)
    kanji = sum(is_kanji(ch) for ch in text)
    punct = sum(is_jp_punct(ch) for ch in text)
    jp = kana + kanji
    visible = sum(not ch.isspace() for ch in text)
    ratio = jp / max(1, visible)
    return kana, kanji, punct, jp, ratio


def excluded_slps_ranges(base):
    atlas_a = base.ATLAS_OFF
    atlas_b = base.ATLAS_OFF + base.ATLAS_GLYPHS * base.GLYPH_BYTES
    try:
        map_b = base.mapping_region_end()
    except Exception:
        map_b = base.MAPPING_OFF + 0x40000
    return [(atlas_a, atlas_b), (base.MAPPING_OFF, map_b)]


def in_ranges(pos: int, ranges):
    return any(a <= pos < b for a, b in ranges)


def scan_blob(file_name: str, blob: bytes, excluded=()):
    out = []
    i = 0
    n = len(blob)
    while i < n:
        if in_ranges(i, excluded):
            ends = [b for a, b in excluded if a <= i < b]
            i = min(ends) if ends else i + 1
            continue
        first = next_unit(blob, i)
        if first is None:
            i += 1
            continue
        start = i
        raw = bytearray()
        units = 0
        while i < n and not in_ranges(i, excluded):
            u = next_unit(blob, i)
            if u is None:
                break
            b, size = u
            raw.extend(b)
            i += size
            units += 1
            if units >= 160:
                break
        if len(raw) < 4:
            i = max(i, start + 1)
            continue
        try:
            text = bytes(raw).decode("cp932")
        except Exception:
            i = max(i, start + 1)
            continue
        text = text.strip(" \u3000")
        if not text:
            continue
        kana, kanji, punct, jp, ratio = score_text(text)
        if jp < 2:
            continue
        if kana == 0 and kanji < 3:
            continue
        if ratio < 0.32:
            continue
        if len(text) > 120:
            continue
        end = start + len(raw)
        term = blob[end] if end < n else None
        term_kind = "NUL" if term == 0 else ("CTRL" if term is not None and term < 0x20 else "OTHER")
        confidence = "HIGH" if term_kind in ("NUL", "CTRL") and ratio >= 0.5 else "MEDIUM"
        out.append({
            "file": file_name,
            "offset": start,
            "japanese": text,
            "byte_len": len(raw),
            "chars": len(text),
            "kana": kana,
            "kanji": kanji,
            "jp_ratio": ratio,
            "terminator": term_kind,
            "confidence": confidence,
        })
        if i == start:
            i += 1
    return out


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} CLEAN_GAME.bin")
        return 2
    requested = Path(sys.argv[1]).expanduser().resolve()
    clean = find_clean_bin(requested)
    if clean is None:
        print("[ERROR] Khong tim thay CLEAN Japan BIN dung SHA1.")
        print("Expected:", CLEAN_SHA1)
        print()
        print("Hay keo-tha file CLEAN Japan .BIN truc tiep len 01_QUET_TOAN_BO_GAME.cmd")
        return 3
    got = sha1_file(clean).lower()

    base = load_base()
    with clean.open("rb") as f:
        slps = base.read_iso_file(f, base.SLPS_EXTENT, base.SLPS_SIZE)
        prg = base.read_iso_file(f, base.PRG_EXTENT, base.PRG_SIZE)

    known_key, known_jp = master_indexes()
    found = []
    found.extend(scan_blob("PRGPACK.BDP", prg))
    found.extend(scan_blob("SLPS_020.75", slps, excluded_slps_ranges(base)))

    unique = {}
    for r in found:
        unique[(r["file"], r["offset"])] = r
    found = sorted(unique.values(), key=lambda r: (r["file"], r["offset"]))

    unseen = 0
    same_offset = 0
    same_text_elsewhere = 0
    anchors = []
    for r in found:
        k = (r["file"], r["offset"])
        jp = r["japanese"]
        exact = known_key.get(k)
        r["known_same_offset"] = "YES" if exact == jp else "NO"
        r["known_text_elsewhere"] = "YES" if jp in known_jp else "NO"
        r["master_offset_text"] = exact or ""
        hit = [a for a in ANCHORS if a in jp]
        r["anchor"] = ";".join(hit)
        if exact == jp:
            same_offset += 1
            r["priority"] = "KNOWN"
        elif jp in known_jp:
            same_text_elsewhere += 1
            r["priority"] = "REPEATED-UNMAPPED"
        else:
            unseen += 1
            r["priority"] = "UNSEEN-JAPANESE"
        if hit:
            anchors.append(r)

    out_dir = requested.parent if requested.parent.exists() else clean.parent
    csv_path = out_dir / "GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv"
    report = out_dir / "GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt"
    fields = [
        "file","offset_hex","japanese","byte_len","chars","kana","kanji","jp_ratio",
        "terminator","confidence","known_same_offset","known_text_elsewhere",
        "master_offset_text","priority","anchor",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in found:
            row = dict(r)
            row["offset_hex"] = hex(row.pop("offset"))
            row["jp_ratio"] = f"{row['jp_ratio']:.3f}"
            w.writerow({k: row.get(k, "") for k in fields})

    unique_unseen = len({r["japanese"] for r in found if r["priority"] == "UNSEEN-JAPANESE"})
    lines = [
        f"GAIA MASTER {VERSION} FULL JAPANESE TEXT SCAN",
        "=" * 78,
        f"CLEAN BIN SHA1             : {got}",
        f"Translation Master keys    : {len(known_key)}",
        f"Scanner candidates         : {len(found)}",
        f"Known same offset          : {same_offset}",
        f"Known text at other offset : {same_text_elsewhere}",
        f"Unseen Japanese candidates : {unseen}",
        f"Unique unseen Japanese     : {unique_unseen}",
        f"Screenshot-anchor hits     : {len(anchors)}",
        "",
        "ANCHOR HITS:",
    ]
    if anchors:
        for r in anchors[:80]:
            lines.append(f"- {r['file']}+{hex(r['offset'])} [{r['priority']}] {r['japanese']}")
    else:
        lines.append("- none found by broad scanner")
    lines += [
        "",
        "NOTES:",
        "- READ ONLY: scanner never patches the BIN.",
        "- UNSEEN-JAPANESE means absent from the current 596-row Translation Master.",
        "- MEDIUM candidates may include false positives and need review before patching.",
        "- HIGH candidates are null/control-terminated and preferred for next translation batches.",
        "",
        f"CSV: {csv_path.name}",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:9]))
    print("Report:", report)
    print("CSV   :", csv_path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("[ERROR]", repr(e))
        raise SystemExit(9)
