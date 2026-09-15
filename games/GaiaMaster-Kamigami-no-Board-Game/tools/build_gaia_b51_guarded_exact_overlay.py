#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gaia Master B51 guarded exact-offset text overlay.

B51 is an ADDITIVE, TEXT-ONLY layer over the canonical B50 overlay.
It never builds, edits, or regenerates font/mapping data.

Dry-run:
  python build_gaia_b51_guarded_exact_overlay.py CLEAN.bin

Build from an already-proven runtime BIN that owns the frozen 60-glyph mapping:
  python build_gaia_b51_guarded_exact_overlay.py CLEAN.bin --build-from BASE.bin

Runtime PASS is never claimed by this tool. Gameplay screenshot evidence remains
mandatory after a successful static/build verification.
"""
from __future__ import annotations

import argparse
import base64
import csv
import gzip
import hashlib
import re
import shutil
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TR = ROOT / "translation"
CHECKPOINT = TR / "source_layer" / "checkpoint_B50"
PARTS = CHECKPOINT / "parts"
RESTORED = CHECKPOINT / "GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv"
B40 = TR / "BATCH40_FINAL_EXACT_SET_0.6.50.0.csv"
B43 = TR / "BATCH43_WHOLEGAME_VISIBLE_0.6.53.0.csv"
MASTER_PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]

sys.path.insert(0, str(TOOLS))
# IMPORTANT: use the frozen historical helper directly. Never import READABLE or
# R5_PATCHED here because those views contain later font-polish source changes.
import build_gaia_06100_hybrid_accent_b1_LEGACY as legacy  # noqa: E402
import batch40_stage_06500 as b40stage  # noqa: E402

CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
B50_RAW_SHA256 = "448bc34afa675299b0de20c54d804d5765e7f9954f67c39058884b318de504b7"
B50_GZIP_SHA256 = "4b8373f53ea04b3b89420c874870b07016fd817c51e603b5644643e6cc122b60"
B50_RAW_SIZE = 162851
B50_ROWS = 1229
B50_DIRECT = 41
B50_COMPACT = 1188
B40_ROWS = 560
B43_ROWS = 102
MASTER_ROWS = 596
LEGACY_KEYS = 397
INTRO_ROWS = 19

EXPECTED_B50_HEADER = [
    "file", "offset_hex", "japanese", "vi_runtime_candidate", "field_bytes",
    "runtime_candidate_bytes", "free_bytes", "production_status", "queue_tier",
    "source_status",
]

FONT_ATLAS = (legacy.ATLAS_OFF, legacy.ATLAS_OFF + legacy.ATLAS_GLYPHS * legacy.GLYPH_BYTES)
FONT_MAPPING = (legacy.MAPPING_OFF, legacy.mapping_region_end())

INTRO = {
    0xC00B4: ("神々の戦いがはじまるのだ", "Thần chiến!"),
    0xC00D0: ("人々をコマとして、", "Người: cờ"),
    0xC00E4: ("世界というゲームボードに、", "Đời là bàn cờ"),
    0xC0100: ("あらがうことはできない", "Khuất phục"),
    0xC0118: ("座すという神々の力に", "Trước thần"),
    0xC0130: ("まぼろしの大地に", "Miền ảo"),
    0xC0144: ("どんな王も司教も、", "Vua,tu sĩ"),
    0xC0158: ("「ガイアマスター」のルールのみ", "Theo luật Gaia"),
    0xC0178: ("いまや世界をつかさどるのは", "Giờ thế giới"),
    0xC0194: ("あとかたもなくくずれさる", "Tan biến hết"),
    0xC01B0: ("今日をかぎりに", "Hôm nay"),
    0xC01C0: ("人のきずいたあらゆる法は", "Luật người"),
    0xC01DC: ("おとずれたのだ！", "Bắt đầu!"),
    0xC01F0: ("神々のゲーム「ガイアマスター」の時が", "Trò Gaia Master"),
    0xC0218: ("大陸をこんとんにたたきこむ", "Đại lục loạn"),
    0xC0234: ("１００年に一度めぐりくる宿命の時", "100 năm một lần"),
    0xC0258: ("空にうかぶまぼろしの大地", "Miền đất ảo"),
    0xC0274: ("月も太陽もおおいかくす", "Trời u tối"),
    0xC028C: ("世界はもはや人のものではなくなった", "Thế giới đổi chủ"),
}

CONTROL_RE = re.compile(
    r"%(?:[-+0-9.#]*[A-Za-z%])|/V|/v|/PF[0-9A-Fa-f]|/P[0-9A-Fa-f]{2}"
)
COMPACT_STATUS_RE = re.compile(r"^COMPACT_CANDIDATE_B(?:2[4-9]|3[0-9]|4[0-9])$")


@dataclass(frozen=True)
class PatchRow:
    line: int
    file: str
    offset: int
    japanese: str
    vi: str
    field: int
    encoded: bytes
    production_status: str

    @property
    def end(self) -> int:
        return self.offset + self.field

    @property
    def key(self) -> tuple[str, int]:
        return self.file, self.offset


def hash_file(path: Path, algo="sha1") -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            raise RuntimeError(f"No CSV header: {path}")
        return list(r.fieldnames), list(r)


def parse_int(raw: str, label: str) -> int:
    s = str(raw or "").strip()
    try:
        return int(s, 0)
    except ValueError:
        try:
            return int(s, 10)
        except ValueError as e:
            raise RuntimeError(f"Invalid integer {label}: {s!r}") from e


def restore_b50() -> Path:
    pp = sorted(PARTS.glob("GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv.gz.b64.part*"))
    if len(pp) != 4:
        raise RuntimeError(f"B50 checkpoint parts: {len(pp)} != 4")
    b64 = "".join(p.read_text(encoding="ascii").strip() for p in pp)
    gz = base64.b64decode(b64, validate=True)
    if hashlib.sha256(gz).hexdigest() != B50_GZIP_SHA256:
        raise RuntimeError("B50 gzip SHA256 mismatch")
    raw = gzip.decompress(gz)
    if len(raw) != B50_RAW_SIZE:
        raise RuntimeError(f"B50 raw size: {len(raw)} != {B50_RAW_SIZE}")
    if hashlib.sha256(raw).hexdigest() != B50_RAW_SHA256:
        raise RuntimeError("B50 raw SHA256 mismatch")
    RESTORED.write_bytes(raw)
    return RESTORED


def tokens(text: str) -> tuple[str, ...]:
    return tuple(m.group(0) for m in CONTROL_RE.finditer(text or ""))


def encode_runtime(text: str, cmap: dict[str, int]) -> bytes:
    out = bytearray(); i = 0
    while i < len(text):
        m = CONTROL_RE.match(text, i)
        if m:
            out.extend(m.group(0).encode("ascii")); i = m.end(); continue
        ch = text[i]
        if ch in cmap:
            code = cmap[ch]; out.extend(((code >> 8) & 0xFF, code & 0xFF))
        elif ch == " " or 0x21 <= ord(ch) <= 0x7E:
            code = legacy.fullwidth_code(ch); out.extend(((code >> 8) & 0xFF, code & 0xFF))
        else:
            try: out.extend(ch.encode("cp932"))
            except Exception as e:
                raise RuntimeError(f"Unsupported runtime char {ch!r} in {text!r}") from e
        i += 1
    return bytes(out)


def overlaps(a: int, b: int, x: int, y: int) -> bool:
    return max(a, x) < min(b, y)


def read_clean(clean: Path):
    got = hash_file(clean)
    if got.lower() != CLEAN_SHA1:
        raise RuntimeError(f"Need CLEAN Japan BIN SHA1 {CLEAN_SHA1}; got {got}")
    with clean.open("rb") as f:
        slps = legacy.read_iso_file(f, legacy.SLPS_EXTENT, legacy.SLPS_SIZE)
        prg = legacy.read_iso_file(f, legacy.PRG_EXTENT, legacy.PRG_SIZE)
    if legacy.sha1_bytes(slps) != legacy.EXPECTED_SLPS_SHA1:
        raise RuntimeError("CLEAN SLPS SHA1 mismatch")
    if legacy.sha1_bytes(prg) != legacy.EXPECTED_PRG_SHA1:
        raise RuntimeError("CLEAN PRGPACK SHA1 mismatch")
    cmap = dict(zip(
        legacy.CUSTOM_CHARS,
        legacy.safe_custom_codes(slps, prg, len(legacy.CUSTOM_CHARS)),
    ))
    if len(cmap) != 60:
        raise RuntimeError(f"Frozen codepage derivation: {len(cmap)} != 60")
    return got.lower(), slps, prg, cmap


def load_b50(cmap: dict[str, int]) -> list[PatchRow]:
    fields, rr = read_csv(RESTORED)
    if fields != EXPECTED_B50_HEADER:
        raise RuntimeError(f"B50 schema drift:\nwant={EXPECTED_B50_HEADER}\ngot ={fields}")
    if len(rr) != B50_ROWS:
        raise RuntimeError(f"B50 row gate: {len(rr)} != {B50_ROWS}")

    out = []; seen = set(); direct = compact = 0
    for line, r in enumerate(rr, 2):
        name = (r["file"] or "").strip()
        if name not in {"PRGPACK.BDP", "SLPS_020.75"}:
            raise RuntimeError(f"B50 line {line}: bad file {name!r}")
        off = parse_int(r["offset_hex"], f"B50 line {line} offset")
        jp = r["japanese"] or ""
        vi = r["vi_runtime_candidate"] or ""
        if not jp or not vi:
            raise RuntimeError(f"B50 line {line}: blank source/candidate")
        jp_bytes = jp.encode("cp932")
        field = parse_int(r["field_bytes"], f"B50 line {line} field")
        if field != len(jp_bytes):
            raise RuntimeError(f"B50 line {line}: field {field} != CP932 {len(jp_bytes)}")
        if tokens(jp) != tokens(vi):
            raise RuntimeError(f"B50 line {line}: token order mismatch {tokens(jp)} != {tokens(vi)}")
        enc = encode_runtime(vi, cmap)
        declared = parse_int(r["runtime_candidate_bytes"], f"B50 line {line} runtime bytes")
        free = parse_int(r["free_bytes"], f"B50 line {line} free bytes")
        if declared != len(enc) or len(enc) > field or free != field - len(enc):
            raise RuntimeError(
                f"B50 line {line}: byte gate candidate={len(enc)}/{declared} field={field} free={free}"
            )
        status = (r["production_status"] or "").strip()
        if status == "DIRECT_FIT_VI_FULL": direct += 1
        elif COMPACT_STATUS_RE.match(status): compact += 1
        else: raise RuntimeError(f"B50 line {line}: unexpected production_status {status!r}")
        key = (name, off)
        if key in seen: raise RuntimeError(f"B50 duplicate key: {name}+0x{off:X}")
        seen.add(key)
        out.append(PatchRow(line, name, off, jp, vi, field, enc, status))

    if direct != B50_DIRECT or compact != B50_COMPACT:
        raise RuntimeError(f"B50 source split: direct={direct}/{B50_DIRECT} compact={compact}/{B50_COMPACT}")
    for name in ("PRGPACK.BDP", "SLPS_020.75"):
        xs = sorted((p for p in out if p.file == name), key=lambda p: p.offset)
        for a, b in zip(xs, xs[1:]):
            if b.offset < a.end:
                raise RuntimeError(f"B50 overlap {name}: 0x{a.offset:X}..0x{a.end:X} with 0x{b.offset:X}")
    return out


def source_identity_gate(rows: list[PatchRow], clean_slps: bytes, clean_prg: bytes):
    entries = legacy.parse_bdp_entries(clean_prg); prg_n = slps_n = 0
    for p in rows:
        blob = clean_prg if p.file == "PRGPACK.BDP" else clean_slps
        if p.offset < 0 or p.end > len(blob):
            raise RuntimeError(f"CLEAN bounds: {p.file}+0x{p.offset:X}")
        if bytes(blob[p.offset:p.end]) != p.japanese.encode("cp932"):
            raise RuntimeError(f"CLEAN source mismatch: {p.file}+0x{p.offset:X} {p.japanese!r}")
        if p.file == "PRGPACK.BDP":
            owner, _s, e = legacy.owner_for_offset(entries, p.offset)
            if p.end > e: raise RuntimeError(f"BDP owner boundary: owner={owner} 0x{p.offset:X}")
            prg_n += 1
        else:
            if overlaps(p.offset, p.end, *FONT_ATLAS):
                raise RuntimeError(f"B51 forbidden font-atlas target: 0x{p.offset:X}")
            if overlaps(p.offset, p.end, *FONT_MAPPING):
                raise RuntimeError(f"B51 forbidden font-mapping target: 0x{p.offset:X}")
            slps_n += 1
    return prg_n, slps_n


def load_hist_manifest(path: Path, count: int, cmap: dict[str, int]):
    fields, rr = read_csv(path)
    need = {"file", "offset_hex", "japanese", "vi_accented", "field_bytes"}
    if not need.issubset(fields) or len(rr) != count:
        raise RuntimeError(f"Historical manifest gate failed: {path.name}")
    out = {}
    for r in rr:
        name = r["file"].strip(); off = parse_int(r["offset_hex"], path.name)
        field = parse_int(r["field_bytes"], path.name); jp = r["japanese"] or ""; vi = r["vi_accented"] or ""
        enc = encode_runtime(vi, cmap)
        if field != len(jp.encode("cp932")) or len(enc) > field:
            raise RuntimeError(f"Historical field gate {path.name} {name}+0x{off:X}")
        out[(name, off)] = (field, enc + b"\0" * (field - len(enc)), jp, vi)
    if len(out) != count: raise RuntimeError(f"Historical duplicate keys: {path.name}")
    return out


def intro_manifest(cmap: dict[str, int]):
    out = {}
    for off, (jp, vi) in INTRO.items():
        field = len(jp.encode("cp932")); enc = encode_runtime(vi, cmap)
        if len(enc) > field: raise RuntimeError(f"Intro overflow 0x{off:X}")
        out[("PRGPACK.BDP", off)] = (field, enc + b"\0" * (field-len(enc)), jp, vi)
    if len(out) != INTRO_ROWS: raise RuntimeError("Intro row gate")
    return out


def protected_overlap_gate(rows: list[PatchRow], protected: dict, label: str) -> int:
    """B50 may equal a protected field, but may never partially/conflictingly clobber it."""
    equivalent = 0
    by_file = {}
    for key, value in protected.items(): by_file.setdefault(key[0], []).append((key[1], value))
    for p in rows:
        for off, (field, want, _jp, _vi) in by_file.get(p.file, ()):
            if not overlaps(p.offset, p.end, off, off+field): continue
            got = p.encoded + b"\0"*(p.field-len(p.encoded))
            if p.offset == off and p.field == field and got == want:
                equivalent += 1; continue
            raise RuntimeError(
                f"B50 conflicts protected {label}: {p.file}+0x{p.offset:X}..0x{p.end:X} "
                f"vs 0x{off:X}..0x{off+field:X}"
            )
    return equivalent


def static_contracts(rows, cmap):
    b40 = load_hist_manifest(B40, B40_ROWS, cmap)
    b43 = load_hist_manifest(B43, B43_ROWS, cmap)
    if set(b40) & set(b43): raise RuntimeError("B40/B43 key collision")
    intro = intro_manifest(cmap)
    eq40 = protected_overlap_gate(rows, b40, "B40")
    eq43 = protected_overlap_gate(rows, b43, "B43")
    eqi = protected_overlap_gate(rows, intro, "INTRO19")

    plan = b40stage.build_plan()
    c = plan["counts"]
    if c["final_verify"] != B40_ROWS or c["legacy"] != LEGACY_KEYS:
        raise RuntimeError(f"Batch40 static contract drift: final={c['final_verify']} legacy={c['legacy']}")
    master_count = 0
    for p in MASTER_PARTS:
        _f, rr = read_csv(p); master_count += len(rr)
    if master_count != MASTER_ROWS: raise RuntimeError(f"Translation Master rows: {master_count} != {MASTER_ROWS}")
    return b40, b43, intro, (eq40, eq43, eqi), c, master_count


def verify_codepage(base_slps: bytes, cmap: dict[str, int]):
    bad = []
    for ch, slot in zip(legacy.CUSTOM_CHARS, legacy.PRODUCTION_SLOTS):
        got = legacy.mapping_value(base_slps, cmap[ch])
        if got != slot: bad.append((ch, slot, got))
    if bad: raise RuntimeError(f"Build base frozen 60-glyph mapping mismatch: {bad[:8]}")
    return len(legacy.CUSTOM_CHARS)


def verify_exact_blob(slps: bytes, prg: bytes, manifest: dict, label: str) -> int:
    bad = []
    for (name, off), (field, want, _jp, _vi) in manifest.items():
        blob = prg if name == "PRGPACK.BDP" else slps
        if bytes(blob[off:off+field]) != want: bad.append((name, off))
    if bad: raise RuntimeError(f"{label} exact byte regression: {bad[:8]} ({len(bad)} total)")
    return len(manifest)


def dry_run(clean: Path):
    clean_sha1, clean_slps, clean_prg, cmap = read_clean(clean)
    restore_b50()
    rows = load_b50(cmap)
    prg_n, slps_n = source_identity_gate(rows, clean_slps, clean_prg)
    b40, b43, intro, eq, counts, masters = static_contracts(rows, cmap)
    return dict(
        clean_sha1=clean_sha1, clean_slps=clean_slps, clean_prg=clean_prg, cmap=cmap,
        rows=rows, prg_n=prg_n, slps_n=slps_n, b40=b40, b43=b43, intro=intro,
        equivalent=eq, counts=counts, masters=masters,
    )


def apply_overlay(rows, clean_slps, clean_prg, base_slps, base_prg):
    slps = bytearray(base_slps); prg = bytearray(base_prg)
    clean_entries = legacy.parse_bdp_entries(clean_prg)
    base_entries = legacy.parse_bdp_entries(base_prg)
    touched = set()
    atlas_before = bytes(base_slps[FONT_ATLAS[0]:FONT_ATLAS[1]])
    mapping_before = bytes(base_slps[FONT_MAPPING[0]:FONT_MAPPING[1]])

    for p in rows:
        clean_blob = clean_prg if p.file == "PRGPACK.BDP" else clean_slps
        target = prg if p.file == "PRGPACK.BDP" else slps
        if bytes(clean_blob[p.offset:p.end]) != p.japanese.encode("cp932"):
            raise RuntimeError(f"Write-time CLEAN identity drift {p.file}+0x{p.offset:X}")
        if p.end > len(target): raise RuntimeError(f"Write-time bounds {p.file}+0x{p.offset:X}")
        if p.file == "PRGPACK.BDP":
            co, _cs, ce = legacy.owner_for_offset(clean_entries, p.offset)
            bo, _bs, be = legacy.owner_for_offset(base_entries, p.offset)
            if co != bo or p.end > ce or p.end > be:
                raise RuntimeError(f"Write-time BDP owner drift 0x{p.offset:X}")
            touched.add(bo)
        else:
            if overlaps(p.offset,p.end,*FONT_ATLAS) or overlaps(p.offset,p.end,*FONT_MAPPING):
                raise RuntimeError(f"Write-time font/mapping target 0x{p.offset:X}")
        target[p.offset:p.end] = p.encoded + b"\0"*(p.field-len(p.encoded))

    owners = {i:(s,e) for i,s,e in base_entries}
    for i in sorted(touched):
        s,e = owners[i]
        struct.pack_into("<I", prg, s+4, legacy.bdp_checksum(bytearray(prg[s:e])))
    struct.pack_into("<I", prg, 4, legacy.bdp_checksum(prg))
    legacy.parse_bdp_entries(bytes(prg))

    if bytes(slps[FONT_ATLAS[0]:FONT_ATLAS[1]]) != atlas_before:
        raise RuntimeError("NO-FONT guard: atlas mutated in memory")
    if bytes(slps[FONT_MAPPING[0]:FONT_MAPPING[1]]) != mapping_before:
        raise RuntimeError("NO-FONT guard: mapping mutated in memory")
    return bytes(slps), bytes(prg), touched, atlas_before, mapping_before


def verify_b51_output(out: Path, dry, atlas_before: bytes, mapping_before: bytes):
    with out.open("rb") as f:
        slps = legacy.read_iso_file(f, legacy.SLPS_EXTENT, legacy.SLPS_SIZE)
        prg = legacy.read_iso_file(f, legacy.PRG_EXTENT, legacy.PRG_SIZE)
    legacy.parse_bdp_entries(prg)
    if bytes(slps[FONT_ATLAS[0]:FONT_ATLAS[1]]) != atlas_before:
        raise RuntimeError("NO-FONT read-back: atlas changed")
    if bytes(slps[FONT_MAPPING[0]:FONT_MAPPING[1]]) != mapping_before:
        raise RuntimeError("NO-FONT read-back: mapping changed")

    bad = []
    for p in dry["rows"]:
        blob = prg if p.file == "PRGPACK.BDP" else slps
        want = p.encoded + b"\0"*(p.field-len(p.encoded))
        if bytes(blob[p.offset:p.end]) != want: bad.append((p.file,p.offset))
    if bad: raise RuntimeError(f"B51 exact output verify: {bad[:8]} ({len(bad)} total)")

    return dict(
        b51=len(dry["rows"]),
        b40=verify_exact_blob(slps, prg, dry["b40"], "B40/Batch42"),
        b43=verify_exact_blob(slps, prg, dry["b43"], "B43"),
        intro=verify_exact_blob(slps, prg, dry["intro"], "Intro19"),
    )


def make_report(dry, mode, base=None, out=None, changed=0, owners=0, verify=None):
    eq40, eq43, eqi = dry["equivalent"]
    c = dry["counts"]
    lines = [
        "GAIA MASTER B51 - GUARDED EXACT-OFFSET TEXT OVERLAY",
        "="*78,
        f"Mode                               : {mode}",
        f"CLEAN BIN SHA1                     : {dry['clean_sha1']}",
        f"B50 restored SHA256                : {B50_RAW_SHA256}",
        f"B50 exact rows                     : {len(dry['rows'])}/{B50_ROWS}",
        f"B50 direct vi_full rows            : {B50_DIRECT}/{B50_DIRECT}",
        f"B50 compact-candidate rows         : {B50_COMPACT}/{B50_COMPACT}",
        f"CLEAN source identity              : {len(dry['rows'])}/{B50_ROWS}",
        f"  PRGPACK.BDP rows                 : {dry['prg_n']}",
        f"  SLPS_020.75 text rows            : {dry['slps_n']}",
        "Duplicate exact keys               : 0",
        "Overlapping B50 write spans        : 0",
        "Byte-fit violations                : 0",
        "Token/control violations           : 0",
        "Font-atlas/mapping write overlap   : 0",
        f"B40 protected exact manifest       : {len(dry['b40'])}/{B40_ROWS}",
        f"B43 protected exact manifest       : {len(dry['b43'])}/{B43_ROWS}",
        f"Combined protected exact fields    : {len(dry['b40'])+len(dry['b43'])}/{B40_ROWS+B43_ROWS}",
        f"Equivalent B50/B40 overlaps        : {eq40}",
        f"Equivalent B50/B43 overlaps        : {eq43}",
        f"Equivalent B50/Intro19 overlaps    : {eqi}",
        f"Legacy Alpha static key contract   : {c['legacy']}/{LEGACY_KEYS}",
        f"Translation Master rows loaded     : {dry['masters']}/{MASTER_ROWS}",
        f"Intro protected exact fields       : {len(dry['intro'])}/{INTRO_ROWS}",
        "B51 font/mapping mutation           : NO",
        "Pointer/renderer architecture       : UNCHANGED",
    ]
    if base:
        lines.append(f"Build base BIN                      : {base}")
    if out:
        lines += [
            f"Output BIN                          : {out}",
            f"Output BIN SHA1                     : {hash_file(out)}",
            f"Changed raw sectors                 : {changed}",
            f"Touched nested BDP owners           : {owners}",
        ]
    if verify:
        lines += [
            f"B51 exact output byte verify        : {verify['b51']}/{B50_ROWS}",
            f"Batch42/B40 output regression       : {verify['b40']}/{B40_ROWS}",
            f"Batch43 output regression           : {verify['b43']}/{B43_ROWS}",
            f"Combined exact output regression    : {verify['b40']+verify['b43']}/{B40_ROWS+B43_ROWS}",
            f"Intro output regression             : {verify['intro']}/{INTRO_ROWS}",
            "Font atlas read-back unchanged     : PASS",
            "Font mapping read-back unchanged   : PASS",
        ]
    lines += [
        "",
        "STATUS:",
        "- Static/build PASS is allowed only when all guards above pass.",
        "- Runtime PASS claim: NO",
        "- Gameplay screenshots are still required before any Runtime PASS claim.",
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
    if not clean.is_file(): raise RuntimeError(f"CLEAN BIN not found: {clean}")
    dry = dry_run(clean)
    report = args.report.expanduser().resolve() if args.report else clean.parent/"GaiaMaster_B51_GUARDED_EXACT_OVERLAY_REPORT.txt"

    if args.build_from is None:
        lines = make_report(dry, "GUARDED DRY-RUN PASS")
        report.write_text("\n".join(lines)+"\n", encoding="utf-8")
        print("\n".join(lines)); print("Report:", report); return 0

    base = args.build_from.expanduser().resolve()
    if not base.is_file(): raise RuntimeError(f"Build base not found: {base}")
    if base.resolve() == clean.resolve():
        raise RuntimeError("B51 is text-only. --build-from must be a proven runtime BIN, not CLEAN.bin")
    if base.stat().st_size != clean.stat().st_size: raise RuntimeError("Build base raw-image size mismatch")
    with base.open("rb") as f:
        base_slps = legacy.read_iso_file(f, legacy.SLPS_EXTENT, legacy.SLPS_SIZE)
        base_prg = legacy.read_iso_file(f, legacy.PRG_EXTENT, legacy.PRG_SIZE)
    legacy.parse_bdp_entries(base_prg)
    if verify_codepage(base_slps, dry["cmap"]) != 60: raise RuntimeError("Frozen codepage gate")

    # Base must already carry the historical runtime contracts. This prevents
    # B51 from masking a bad/unknown build behind a successful new overlay.
    verify_exact_blob(base_slps, base_prg, dry["b40"], "BASE B40/Batch42")
    verify_exact_blob(base_slps, base_prg, dry["b43"], "BASE B43")
    verify_exact_blob(base_slps, base_prg, dry["intro"], "BASE Intro19")

    slps_new, prg_new, touched, atlas_before, mapping_before = apply_overlay(
        dry["rows"], dry["clean_slps"], dry["clean_prg"], base_slps, base_prg
    )
    out = args.output.expanduser().resolve() if args.output else base.with_name(base.stem+" [B51 EXACT OVERLAY].bin")
    if out.resolve() in {clean.resolve(), base.resolve()}: raise RuntimeError("Output must not overwrite CLEAN/base")
    if out.exists(): out.unlink()
    shutil.copyfile(base, out)
    changed = set()
    with out.open("r+b") as f:
        legacy.write_changed_iso_file(f, legacy.SLPS_EXTENT, base_slps, slps_new, changed)
        legacy.write_changed_iso_file(f, legacy.PRG_EXTENT, base_prg, prg_new, changed)
        for sec in sorted(changed):
            f.seek(sec*2352); raw=f.read(2352); f.seek(sec*2352); f.write(legacy.regen_sector(raw))

    verified = verify_b51_output(out, dry, atlas_before, mapping_before)
    cue = out.with_suffix(".cue")
    cue.write_text(f'FILE "{out.name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n', encoding="ascii")
    lines = make_report(dry, "GUARDED BUILD + STATIC BYTE VERIFICATION PASS", base, out, len(changed), len(touched), verified)
    lines.append(f"Output CUE                          : {cue}")
    report.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("\n".join(lines)); print("Report:", report); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except SystemExit: raise
    except Exception as e:
        print("[ERROR]", repr(e)); raise SystemExit(9)
