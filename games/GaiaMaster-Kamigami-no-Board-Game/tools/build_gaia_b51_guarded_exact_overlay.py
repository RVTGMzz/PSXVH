#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gaia Master B51 guarded exact-offset runtime overlay layer.

B51 is deliberately TEXT-ONLY.

Safety contract:
- exact CLEAN Japan BIN SHA1 is mandatory for source identity;
- canonical B50 overlay is restored from checkpoint and hash-verified;
- every source file+offset is verified against CLEAN bytes before any write;
- token/control order is preserved;
- duplicate/overlapping writes are rejected;
- font atlas and mapping ranges are forbidden write targets;
- build mode patches an existing runtime base BIN that already owns the frozen
  60-glyph codepage; B51 never regenerates or edits font/mapping data;
- BDP and raw-sector checksums are rebuilt after text writes;
- historical B40/B43 exact-field regression gates are verified after build;
- Runtime PASS is NEVER claimed here. Gameplay screenshot evidence is required.

Usage:
  python build_gaia_b51_guarded_exact_overlay.py CLEAN.bin
      -> restore B50 + guarded dry-run only

  python build_gaia_b51_guarded_exact_overlay.py CLEAN.bin --build-from BASE.bin
      -> guarded dry-run, then text-only B51 build from BASE.bin

Optional:
  --output OUT.bin
  --report REPORT.txt
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
FRONT = TR / "FRONT_DEMO_ADDED_061.csv"
MASTER_PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]

# Import the frozen historical helper implementation directly. Do NOT import
# READABLE/R5_PATCHED here because those views contain later font-polish logic.
sys.path.insert(0, str(TOOLS))
import build_gaia_06100_hybrid_accent_b1_LEGACY as legacy  # noqa: E402

CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
B50_RAW_SHA256 = "448bc34afa675299b0de20c54d804d5765e7f9954f67c39058884b318de504b7"
B50_GZIP_SHA256 = "4b8373f53ea04b3b89420c874870b07016fd817c51e603b5644643e6cc122b60"
B50_RAW_SIZE = 162851
B50_ROWS = 1229
B40_ROWS = 560
B43_ROWS = 102
MASTER_ROWS = 596
LEGACY_KEYS = 397
INTRO_ROWS = 19

FONT_ATLAS_A = legacy.ATLAS_OFF
FONT_ATLAS_B = legacy.ATLAS_OFF + legacy.ATLAS_GLYPHS * legacy.GLYPH_BYTES
MAPPING_A = legacy.MAPPING_OFF
MAPPING_B = legacy.mapping_region_end()

# B45 wording is a historical exact-field runtime contract. B51 does not touch
# the B45 font code; only these 19 text fields are regression-checked.
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

# Raw runtime controls. Order is part of source identity.
CONTROL_RE = re.compile(
    r"%(?:[-+0-9.#]*[A-Za-z%])|/V|/v|/PF[0-9A-Fa-f]|/P[0-9A-Fa-f]{2}"
)

EXPLICIT_CANDIDATE_COLUMNS = (
    "runtime_candidate",
    "vi_runtime_candidate",
    "selected_candidate",
    "selected_vi",
    "vi_selected",
    "vi_candidate",
    "candidate_text",
    "candidate",
)
FIELD_COLUMNS = ("field_bytes", "byte_len", "source_bytes", "jp_bytes", "orig_bytes")
BYTE_COUNT_COLUMNS = ("candidate_bytes", "runtime_bytes", "encoded_bytes", "vi_bytes")
FREE_COLUMNS = ("free_bytes", "remaining_bytes")
SOURCE_COLUMNS = ("candidate_source", "selected_source", "runtime_source", "source_kind")


@dataclass(frozen=True)
class PatchRow:
    line_no: int
    file: str
    offset: int
    japanese: str
    candidate: str
    candidate_source: str
    field_bytes: int
    encoded: bytes
    controls: tuple[str, ...]

    @property
    def end(self) -> int:
        return self.offset + self.field_bytes

    @property
    def key(self) -> tuple[str, int]:
        return self.file, self.offset


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            b = f.read(8 * 1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            raise RuntimeError(f"No CSV header: {path}")
        return list(r.fieldnames), list(r)


def restore_b50() -> Path:
    part_paths = sorted(PARTS.glob("GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv.gz.b64.part*"))
    if len(part_paths) != 4:
        raise RuntimeError(f"B50 checkpoint part gate failed: {len(part_paths)} != 4")
    b64 = "".join(p.read_text(encoding="ascii").strip() for p in part_paths)
    gz = base64.b64decode(b64, validate=True)
    if sha256_bytes(gz) != B50_GZIP_SHA256:
        raise RuntimeError("B50 compressed SHA256 mismatch")
    raw = gzip.decompress(gz)
    if len(raw) != B50_RAW_SIZE:
        raise RuntimeError(f"B50 raw size mismatch: {len(raw)} != {B50_RAW_SIZE}")
    if sha256_bytes(raw) != B50_RAW_SHA256:
        raise RuntimeError("B50 raw SHA256 mismatch")
    RESTORED.write_bytes(raw)
    return RESTORED


def controls(text: str) -> tuple[str, ...]:
    return tuple(m.group(0) for m in CONTROL_RE.finditer(text or ""))


def encode_runtime_text(text: str, cmap: dict[str, int]) -> bytes:
    """Historical full-width encoder plus B50's /Pxx and /PFx raw controls."""
    out = bytearray()
    i = 0
    while i < len(text):
        m = CONTROL_RE.match(text, i)
        if m:
            token = m.group(0)
            out.extend(token.encode("ascii"))
            i = m.end()
            continue
        ch = text[i]
        if ch in cmap:
            code = cmap[ch]
            out.extend(((code >> 8) & 0xFF, code & 0xFF))
        elif ch == " " or 0x21 <= ord(ch) <= 0x7E:
            code = legacy.fullwidth_code(ch)
            out.extend(((code >> 8) & 0xFF, code & 0xFF))
        else:
            try:
                out.extend(ch.encode("cp932"))
            except Exception as e:
                raise RuntimeError(
                    f"Unsupported runtime char {ch!r} U+{ord(ch):04X} in {text!r}"
                ) from e
        i += 1
    return bytes(out)


def first_present(fields: list[str], names: tuple[str, ...]) -> str | None:
    for n in names:
        if n in fields:
            return n
    return None


def resolve_candidate(fields: list[str], row: dict[str, str], line_no: int) -> tuple[str, str]:
    # Prefer an explicit B50 selected/runtime candidate column when present.
    for col in EXPLICIT_CANDIDATE_COLUMNS:
        if col in fields and (row.get(col) or "").strip():
            source_col = first_present(fields, SOURCE_COLUMNS)
            source = (row.get(source_col) or "").strip() if source_col else col
            return (row.get(col) or "").strip(), (source or col)

    # Source-layer fallback used by B24-B49: compact wins only when present,
    # otherwise the meaning-first vi_full is the selected runtime text.
    if "vi_compact" in fields and (row.get("vi_compact") or "").strip():
        return (row.get("vi_compact") or "").strip(), "vi_compact"
    if "vi_full" in fields and (row.get("vi_full") or "").strip():
        return (row.get("vi_full") or "").strip(), "vi_full"
    if "vi_accented" in fields and (row.get("vi_accented") or "").strip():
        return (row.get("vi_accented") or "").strip(), "vi_accented"
    if "vi_game_current" in fields and (row.get("vi_game_current") or "").strip():
        return (row.get("vi_game_current") or "").strip(), "vi_game_current"
    raise RuntimeError(f"B50 line {line_no}: no runtime candidate column/value")


def parse_int(raw: str, label: str) -> int:
    s = str(raw or "").strip()
    if not s:
        raise RuntimeError(f"Blank integer: {label}")
    try:
        return int(s, 0)
    except ValueError:
        try:
            return int(s, 10)
        except ValueError as e:
            raise RuntimeError(f"Invalid integer {label}: {s!r}") from e


def load_overlay(cmap: dict[str, int]) -> tuple[list[PatchRow], list[str]]:
    fields, raw_rows = read_csv(RESTORED)
    for req in ("file", "offset_hex", "japanese"):
        if req not in fields:
            raise RuntimeError(f"B50 overlay missing required column {req!r}; fields={fields}")
    if len(raw_rows) != B50_ROWS:
        raise RuntimeError(f"B50 row gate failed: {len(raw_rows)} != {B50_ROWS}")

    field_col = first_present(fields, FIELD_COLUMNS)
    byte_col = first_present(fields, BYTE_COUNT_COLUMNS)
    free_col = first_present(fields, FREE_COLUMNS)
    out: list[PatchRow] = []
    seen: set[tuple[str, int]] = set()

    for idx, r in enumerate(raw_rows, start=2):
        name = (r.get("file") or "").strip()
        if name not in {"PRGPACK.BDP", "SLPS_020.75"}:
            raise RuntimeError(f"B50 line {idx}: unsupported target file {name!r}")
        off = parse_int(r.get("offset_hex") or "", f"B50 line {idx} offset_hex")
        jp = r.get("japanese") or ""
        if not jp:
            raise RuntimeError(f"B50 line {idx}: blank Japanese source")
        try:
            jp_bytes = jp.encode("cp932")
        except Exception as e:
            raise RuntimeError(f"B50 line {idx}: Japanese is not CP932 encodable: {jp!r}") from e

        field = parse_int(r.get(field_col) or "", f"B50 line {idx} {field_col}") if field_col else len(jp_bytes)
        if field != len(jp_bytes):
            raise RuntimeError(
                f"B50 line {idx}: source field-size identity mismatch: "
                f"CSV={field} CP932={len(jp_bytes)} {name}+0x{off:X} {jp!r}"
            )

        vi, source = resolve_candidate(fields, r, idx)
        if controls(jp) != controls(vi):
            raise RuntimeError(
                f"B50 line {idx}: token/control mismatch {name}+0x{off:X}: "
                f"{controls(jp)} != {controls(vi)}"
            )
        enc = encode_runtime_text(vi, cmap)
        if len(enc) > field:
            raise RuntimeError(
                f"B50 line {idx}: byte overflow {name}+0x{off:X}: {len(enc)}>{field}"
            )
        if byte_col and (r.get(byte_col) or "").strip():
            declared = parse_int(r.get(byte_col) or "", f"B50 line {idx} {byte_col}")
            if declared != len(enc):
                raise RuntimeError(
                    f"B50 line {idx}: encoded-byte gate mismatch: {declared}!={len(enc)}"
                )
        if free_col and (r.get(free_col) or "").strip():
            declared_free = parse_int(r.get(free_col) or "", f"B50 line {idx} {free_col}")
            if declared_free != field - len(enc):
                raise RuntimeError(
                    f"B50 line {idx}: free-byte gate mismatch: "
                    f"{declared_free}!={field-len(enc)}"
                )

        key = (name, off)
        if key in seen:
            raise RuntimeError(f"B50 duplicate exact key: {name}+0x{off:X}")
        seen.add(key)
        out.append(PatchRow(idx, name, off, jp, vi, source, field, enc, controls(jp)))

    by_file: dict[str, list[PatchRow]] = {}
    for p in out:
        by_file.setdefault(p.file, []).append(p)
    for name, rr in by_file.items():
        rr.sort(key=lambda p: p.offset)
        for prev, cur in zip(rr, rr[1:]):
            if cur.offset < prev.end:
                raise RuntimeError(
                    f"B50 overlapping writes in {name}: "
                    f"0x{prev.offset:X}..0x{prev.end:X} overlaps "
                    f"0x{cur.offset:X}..0x{cur.end:X}"
                )
    return out, fields


def overlaps(a: int, b: int, x: int, y: int) -> bool:
    return max(a, x) < min(b, y)


def clean_source_gate(rows: list[PatchRow], clean_slps: bytes, clean_prg: bytes) -> tuple[int, int]:
    entries = legacy.parse_bdp_entries(clean_prg)
    prg_ok = 0
    slps_ok = 0
    for p in rows:
        blob = clean_prg if p.file == "PRGPACK.BDP" else clean_slps
        if p.offset < 0 or p.end > len(blob):
            raise RuntimeError(f"CLEAN bounds gate failed: {p.file}+0x{p.offset:X}")
        jp_bytes = p.japanese.encode("cp932")
        got = bytes(blob[p.offset:p.end])
        if got != jp_bytes:
            raise RuntimeError(
                f"CLEAN source identity mismatch {p.file}+0x{p.offset:X}:\n"
                f"expected={jp_bytes.hex().upper()} {p.japanese!r}\n"
                f"actual  ={got.hex().upper()}"
            )

        if p.file == "PRGPACK.BDP":
            owner, start, end = legacy.owner_for_offset(entries, p.offset)
            if p.end > end:
                raise RuntimeError(
                    f"CLEAN BDP owner boundary gate failed: owner={owner} "
                    f"0x{p.offset:X}..0x{p.end:X} > 0x{end:X}"
                )
            prg_ok += 1
        else:
            if overlaps(p.offset, p.end, FONT_ATLAS_A, FONT_ATLAS_B):
                raise RuntimeError(f"B51 forbidden font-atlas write: SLPS+0x{p.offset:X}")
            if overlaps(p.offset, p.end, MAPPING_A, MAPPING_B):
                raise RuntimeError(f"B51 forbidden font-mapping write: SLPS+0x{p.offset:X}")
            slps_ok += 1
    return prg_ok, slps_ok


def derive_cmap(clean_slps: bytes, clean_prg: bytes) -> dict[str, int]:
    codes = legacy.safe_custom_codes(clean_slps, clean_prg, len(legacy.CUSTOM_CHARS))
    if len(codes) != 60:
        raise RuntimeError(f"Frozen codepage derivation gate: {len(codes)} != 60")
    return dict(zip(legacy.CUSTOM_CHARS, codes))


def verify_base_codepage(base_slps: bytes, cmap: dict[str, int]) -> None:
    if len(legacy.CUSTOM_CHARS) != 60 or len(legacy.PRODUCTION_SLOTS) != 60:
        raise RuntimeError("Frozen codepage constants changed")
    bad = []
    for ch, slot in zip(legacy.CUSTOM_CHARS, legacy.PRODUCTION_SLOTS):
        code = cmap[ch]
        got = legacy.mapping_value(base_slps, code)
        if got != slot:
            bad.append((ch, code, slot, got))
    if bad:
        preview = ", ".join(f"{ch}:{code:04X}->{got} want {slot}" for ch, code, slot, got in bad[:8])
        raise RuntimeError(
            "Build base does not own the frozen 60-glyph mapping contract. "
            f"First mismatches: {preview}"
        )


def manifest_expected(path: Path, cmap: dict[str, int], expected_count: int) -> dict[tuple[str, int], tuple[bytes, int, str]]:
    fields, rr = read_csv(path)
    required = {"file", "offset_hex", "japanese", "vi_accented", "field_bytes"}
    missing = sorted(required - set(fields))
    if missing:
        raise RuntimeError(f"Historical manifest {path.name} missing columns: {missing}")
    if len(rr) != expected_count:
        raise RuntimeError(f"Historical manifest row gate {path.name}: {len(rr)} != {expected_count}")
    out = {}
    for r in rr:
        name = (r.get("file") or "").strip()
        off = parse_int(r.get("offset_hex") or "", f"{path.name} offset")
        field = parse_int(r.get("field_bytes") or "", f"{path.name} field")
        vi = r.get("vi_accented") or ""
        enc = encode_runtime_text(vi, cmap)
        if len(enc) > field:
            raise RuntimeError(f"Historical manifest overflow {path.name} {name}+0x{off:X}")
        key = (name, off)
        if key in out:
            raise RuntimeError(f"Historical manifest duplicate {path.name} {key}")
        out[key] = (enc + b"\0" * (field - len(enc)), field, vi)
    return out


def load_master_rows() -> list[dict[str, str]]:
    out = []
    for p in MASTER_PARTS:
        _fields, rr = read_csv(p)
        out.extend(rr)
    if len(out) != MASTER_ROWS:
        raise RuntimeError(f"Translation Master row gate: {len(out)} != {MASTER_ROWS}")
    return out


def legacy_key_gate(cmap: dict[str, int], overlay_map: dict[tuple[str, int], PatchRow]) -> int:
    masters = load_master_rows()
    _ff, front_rows = read_csv(FRONT)
    keys = legacy.compute_alpha061_legacy_keys(masters, front_rows, cmap)
    if len(keys) != LEGACY_KEYS:
        raise RuntimeError(f"Legacy Alpha key reconstruction: {len(keys)} != {LEGACY_KEYS}")
    missing = sorted(k for k in keys if k not in overlay_map)
    if missing:
        raise RuntimeError(f"B50 lost {len(missing)} legacy Alpha exact keys: {missing[:8]}")
    return len(keys)


def master_coverage_gate(overlay_map: dict[tuple[str, int], PatchRow]) -> int:
    masters = load_master_rows()
    missing = []
    for r in masters:
        name = (r.get("file") or "").strip()
        off = parse_int(r.get("offset_hex") or "", "Translation Master offset")
        jp = r.get("japanese") or ""
        p = overlay_map.get((name, off))
        if p is None or p.japanese != jp:
            missing.append((name, off, jp))
    if missing:
        raise RuntimeError(f"B50 Translation Master identity gate lost {len(missing)} rows: {missing[:8]}")
    return len(masters)


def intro_overlay_gate(overlay_map: dict[tuple[str, int], PatchRow], cmap: dict[str, int]) -> int:
    bad = []
    for off, (jp, vi) in INTRO.items():
        p = overlay_map.get(("PRGPACK.BDP", off))
        if p is None:
            bad.append((off, "missing"))
            continue
        if p.japanese != jp:
            bad.append((off, f"jp {p.japanese!r} != {jp!r}"))
            continue
        if p.encoded != encode_runtime_text(vi, cmap):
            bad.append((off, f"vi {p.candidate!r} != {vi!r}"))
    if bad:
        raise RuntimeError(f"B50 intro 19/19 regression gate failed: {bad[:8]}")
    return len(INTRO)


def exact_manifest_overlay_gate(
    overlay_map: dict[tuple[str, int], PatchRow],
    expected: dict[tuple[str, int], tuple[bytes, int, str]],
    label: str,
) -> int:
    bad = []
    for key, (want, field, vi) in expected.items():
        p = overlay_map.get(key)
        if p is None:
            bad.append((key, "missing"))
            continue
        got = p.encoded + b"\0" * (p.field_bytes - len(p.encoded))
        if p.field_bytes != field or got != want:
            bad.append((key, f"B50={p.candidate!r} historical={vi!r}"))
    if bad:
        raise RuntimeError(f"{label} B50 overlay regression gate failed ({len(bad)}): {bad[:8]}")
    return len(expected)


def dry_run(clean: Path):
    got = sha1_file(clean).lower()
    if got != CLEAN_SHA1:
        raise RuntimeError(f"Need exact CLEAN Japan BIN SHA1 {CLEAN_SHA1}; got {got}")

    restored = restore_b50()
    if sha256_bytes(restored.read_bytes()) != B50_RAW_SHA256:
        raise RuntimeError("Restored B50 SHA256 changed after write")

    with clean.open("rb") as f:
        clean_slps = legacy.read_iso_file(f, legacy.SLPS_EXTENT, legacy.SLPS_SIZE)
        clean_prg = legacy.read_iso_file(f, legacy.PRG_EXTENT, legacy.PRG_SIZE)
    if legacy.sha1_bytes(clean_slps) != legacy.EXPECTED_SLPS_SHA1:
        raise RuntimeError("CLEAN SLPS SHA1 mismatch")
    if legacy.sha1_bytes(clean_prg) != legacy.EXPECTED_PRG_SHA1:
        raise RuntimeError("CLEAN PRGPACK SHA1 mismatch")

    cmap = derive_cmap(clean_slps, clean_prg)
    rows, fields = load_overlay(cmap)
    prg_ok, slps_ok = clean_source_gate(rows, clean_slps, clean_prg)
    overlay_map = {p.key: p for p in rows}

    b40 = manifest_expected(B40, cmap, B40_ROWS)
    b43 = manifest_expected(B43, cmap, B43_ROWS)
    if set(b40) & set(b43):
        raise RuntimeError("Historical B40/B43 exact-key collision")
    b40_ok = exact_manifest_overlay_gate(overlay_map, b40, "B40/Batch42")
    b43_ok = exact_manifest_overlay_gate(overlay_map, b43, "B43")
    legacy_ok = legacy_key_gate(cmap, overlay_map)
    master_ok = master_coverage_gate(overlay_map)
    intro_ok = intro_overlay_gate(overlay_map, cmap)

    direct = sum(1 for p in rows if "full" in p.candidate_source.lower())
    compact = len(rows) - direct
    return {
        "clean_sha1": got,
        "clean_slps": clean_slps,
        "clean_prg": clean_prg,
        "cmap": cmap,
        "rows": rows,
        "fields": fields,
        "overlay_map": overlay_map,
        "prg_rows": prg_ok,
        "slps_rows": slps_ok,
        "b40": b40_ok,
        "b43": b43_ok,
        "combined": b40_ok + b43_ok,
        "legacy": legacy_ok,
        "master": master_ok,
        "intro": intro_ok,
        "direct_inferred": direct,
        "compact_inferred": compact,
    }


def apply_rows(rows: list[PatchRow], clean_slps: bytes, clean_prg: bytes, base_slps: bytes, base_prg: bytes):
    slps_new = bytearray(base_slps)
    prg_new = bytearray(base_prg)
    base_entries = legacy.parse_bdp_entries(base_prg)
    clean_entries = legacy.parse_bdp_entries(clean_prg)
    touched_owners: set[int] = set()

    atlas_before = bytes(base_slps[FONT_ATLAS_A:FONT_ATLAS_B])
    mapping_before = bytes(base_slps[MAPPING_A:MAPPING_B])

    for p in rows:
        clean_blob = clean_prg if p.file == "PRGPACK.BDP" else clean_slps
        target = prg_new if p.file == "PRGPACK.BDP" else slps_new
        jp_bytes = p.japanese.encode("cp932")
        if bytes(clean_blob[p.offset:p.end]) != jp_bytes:
            raise RuntimeError(f"Write-time CLEAN identity drift: {p.file}+0x{p.offset:X}")
        if p.end > len(target):
            raise RuntimeError(f"Write-time base bounds gate: {p.file}+0x{p.offset:X}")
        new_field = p.encoded + b"\0" * (p.field_bytes - len(p.encoded))
        if len(new_field) != p.field_bytes:
            raise AssertionError((p.file, p.offset, len(new_field), p.field_bytes))

        if p.file == "PRGPACK.BDP":
            clean_owner, _cs, ce = legacy.owner_for_offset(clean_entries, p.offset)
            base_owner, _bs, be = legacy.owner_for_offset(base_entries, p.offset)
            if p.end > ce or p.end > be:
                raise RuntimeError(f"Write-time BDP owner boundary gate: 0x{p.offset:X}")
            if clean_owner != base_owner:
                raise RuntimeError(
                    f"BDP owner index drift at 0x{p.offset:X}: CLEAN={clean_owner} BASE={base_owner}"
                )
            touched_owners.add(base_owner)
        else:
            if overlaps(p.offset, p.end, FONT_ATLAS_A, FONT_ATLAS_B) or overlaps(
                p.offset, p.end, MAPPING_A, MAPPING_B
            ):
                raise RuntimeError(f"Write-time forbidden font/mapping write: 0x{p.offset:X}")

        target[p.offset:p.end] = new_field

    by = {i: (s, e) for i, s, e in base_entries}
    for owner in sorted(touched_owners):
        s, e = by[owner]
        block = bytearray(prg_new[s:e])
        struct.pack_into("<I", prg_new, s + 4, legacy.bdp_checksum(block))
    struct.pack_into("<I", prg_new, 4, legacy.bdp_checksum(prg_new))
    legacy.parse_bdp_entries(bytes(prg_new))

    if bytes(slps_new[FONT_ATLAS_A:FONT_ATLAS_B]) != atlas_before:
        raise RuntimeError("B51 NO-FONT guard failed: atlas bytes changed in memory")
    if bytes(slps_new[MAPPING_A:MAPPING_B]) != mapping_before:
        raise RuntimeError("B51 NO-FONT guard failed: mapping bytes changed in memory")

    return bytes(slps_new), bytes(prg_new), touched_owners, atlas_before, mapping_before


def verify_output(
    out_bin: Path,
    rows: list[PatchRow],
    cmap: dict[str, int],
    atlas_before: bytes,
    mapping_before: bytes,
) -> dict[str, int]:
    with out_bin.open("rb") as f:
        slps = legacy.read_iso_file(f, legacy.SLPS_EXTENT, legacy.SLPS_SIZE)
        prg = legacy.read_iso_file(f, legacy.PRg_EXTENT if False else legacy.PRG_EXTENT, legacy.PRG_SIZE)
    legacy.parse_bdp_entries(prg)

    if bytes(slps[FONT_ATLAS_A:FONT_ATLAS_B]) != atlas_before:
        raise RuntimeError("B51 NO-FONT read-back guard failed: atlas changed")
    if bytes(slps[MAPPING_A:MAPPING_B]) != mapping_before:
        raise RuntimeError("B51 NO-FONT read-back guard failed: mapping changed")

    bad = []
    for p in rows:
        blob = prg if p.file == "PRGPACK.BDP" else slps
        want = p.encoded + b"\0" * (p.field_bytes - len(p.encoded))
        got = bytes(blob[p.offset:p.end])
        if got != want:
            bad.append((p.file, p.offset))
    if bad:
        raise RuntimeError(f"B51 exact output byte verification failed: {bad[:8]}")

    b40 = manifest_expected(B40, cmap, B40_ROWS)
    b43 = manifest_expected(B43, cmap, B43_ROWS)
    hist_bad = []
    for label, manifest in (("B40", b40), ("B43", b43)):
        for (name, off), (want, field, _vi) in manifest.items():
            blob = prg if name == "PRGPACK.BDP" else slps
            if bytes(blob[off:off+field]) != want:
                hist_bad.append((label, name, off))
    if hist_bad:
        raise RuntimeError(f"Historical exact-field output regression: {hist_bad[:8]}")

    intro_bad = []
    for off, (jp, vi) in INTRO.items():
        field = len(jp.encode("cp932"))
        enc = encode_runtime_text(vi, cmap)
        want = enc + b"\0" * (field - len(enc))
        if bytes(prg[off:off+field]) != want:
            intro_bad.append(off)
    if intro_bad:
        raise RuntimeError(f"Intro 19/19 output regression failed: {intro_bad[:8]}")

    return {
        "b51": len(rows),
        "b40": len(b40),
        "b43": len(b43),
        "combined": len(b40) + len(b43),
        "intro": len(INTRO),
    }


def report_lines(dry, mode: str, base: Path | None = None, out: Path | None = None, changed=0, owners=0, verify=None):
    lines = [
        "GAIA MASTER B51 - GUARDED EXACT-OFFSET TEXT OVERLAY",
        "=" * 78,
        f"Mode                              : {mode}",
        f"CLEAN BIN SHA1                    : {dry['clean_sha1']}",
        f"B50 restored raw SHA256           : {B50_RAW_SHA256}",
        f"B50 exact rows                    : {len(dry['rows'])}/{B50_ROWS}",
        f"CLEAN source identity verified    : {len(dry['rows'])}/{B50_ROWS}",
        f"  PRGPACK rows                    : {dry['prg_rows']}",
        f"  SLPS text rows                  : {dry['slps_rows']}",
        "Duplicate file+offset collisions  : 0",
        "Overlapping write spans           : 0",
        "Byte-fit violations                : 0",
        "Token/control order violations     : 0",
        "Font-atlas overlap                 : 0",
        "Font-mapping overlap               : 0",
        f"Batch42/B40 exact regression       : {dry['b40']}/{B40_ROWS}",
        f"Batch43 exact regression           : {dry['b43']}/{B43_ROWS}",
        f"Combined historical exact          : {dry['combined']}/{B40_ROWS+B43_ROWS}",
        f"Legacy Alpha key contract          : {dry['legacy']}/{LEGACY_KEYS}",
        f"Translation Master identity        : {dry['master']}/{MASTER_ROWS}",
        f"Intro exact text contract          : {dry['intro']}/{INTRO_ROWS}",
        "B51 font/mapping mutation          : NO",
        "Pointer/renderer architecture      : UNCHANGED",
    ]
    if base is not None:
        lines.append(f"Build base BIN                     : {base}")
    if out is not None:
        lines += [
            f"Output BIN                         : {out}",
            f"Output BIN SHA1                    : {sha1_file(out)}",
            f"Changed raw sectors                : {changed}",
            f"Touched nested BDP owners          : {owners}",
        ]
    if verify:
        lines += [
            f"B51 exact output byte verify       : {verify['b51']}/{B50_ROWS}",
            f"Batch42/B40 output regression      : {verify['b40']}/{B40_ROWS}",
            f"Batch43 output regression          : {verify['b43']}/{B43_ROWS}",
            f"Combined exact output regression   : {verify['combined']}/{B40_ROWS+B43_ROWS}",
            f"Intro output regression            : {verify['intro']}/{INTRO_ROWS}",
            "Font atlas read-back unchanged    : PASS",
            "Font mapping read-back unchanged  : PASS",
        ]
    lines += [
        "",
        "STATIC/BUILD STATUS:",
        "- Guarded source/byte regression gates may be called PASS when this report says so.",
        "- Runtime PASS claim: NO",
        "- Gameplay screenshots are still required before any Runtime PASS claim.",
    ]
    return lines


def write_cue(out_bin: Path) -> Path:
    cue = out_bin.with_suffix(".cue")
    cue.write_text(
        f'FILE "{out_bin.name}" BINARY\n'
        "  TRACK 01 MODE2/2352\n"
        "    INDEX 01 00:00:00\n",
        encoding="ascii",
    )
    return cue


def main() -> int:
    ap = argparse.ArgumentParser(description="Gaia Master B51 guarded B50 exact-offset text layer")
    ap.add_argument("clean_bin", type=Path, help="exact CLEAN Japan BIN")
    ap.add_argument("--build-from", type=Path, default=None, help="existing runtime base BIN with frozen 60-glyph codepage")
    ap.add_argument("--output", type=Path, default=None, help="B51 output BIN path")
    ap.add_argument("--report", type=Path, default=None, help="report path")
    args = ap.parse_args()

    clean = args.clean_bin.expanduser().resolve()
    if not clean.is_file():
        raise RuntimeError(f"CLEAN BIN not found: {clean}")

    dry = dry_run(clean)
    default_report = clean.parent / "GaiaMaster_B51_GUARDED_EXACT_OVERLAY_REPORT.txt"
    report = args.report.expanduser().resolve() if args.report else default_report

    if args.build_from is None:
        lines = report_lines(dry, "GUARDED DRY-RUN ONLY")
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(lines))
        print(f"Report: {report}")
        return 0

    base = args.build_from.expanduser().resolve()
    if not base.is_file():
        raise RuntimeError(f"Build base BIN not found: {base}")
    if base.resolve() == clean.resolve():
        raise RuntimeError(
            "B51 build refuses CLEAN.bin as --build-from because B51 is text-only and "
            "does not install the frozen Vietnamese font. Use a known-good runtime base BIN."
        )
    if base.stat().st_size != clean.stat().st_size:
        raise RuntimeError(
            f"Build base raw-image size mismatch: {base.stat().st_size} != {clean.stat().st_size}"
        )

    with base.open("rb") as f:
        base_slps = legacy.read_iso_file(f, legacy.SLPS_EXTENT, legacy.SLPS_SIZE)
        base_prg = legacy.read_iso_file(f, legacy.PRG_EXTENT, legacy.PRG_SIZE)
    legacy.parse_bdp_entries(base_prg)
    verify_base_codepage(base_slps, dry["cmap"])

    slps_new, prg_new, touched, atlas_before, mapping_before = apply_rows(
        dry["rows"], dry["clean_slps"], dry["clean_prg"], base_slps, base_prg
    )

    out = (
        args.output.expanduser().resolve()
        if args.output
        else base.with_name(base.stem + " [B51 EXACT OVERLAY].bin")
    )
    if out.resolve() in {base.resolve(), clean.resolve()}:
        raise RuntimeError("Output path must not overwrite CLEAN or build base BIN")
    if out.exists():
        out.unlink()
    shutil.copyfile(base, out)
    changed: set[int] = set()
    with out.open("r+b") as f:
        legacy.write_changed_iso_file(f, legacy.SLPS_EXTENT, base_slps, slps_new, changed)
        legacy.write_changed_iso_file(f, legacy.PRG_EXTENT, base_prg, prg_new, changed)
        for sec in sorted(changed):
            f.seek(sec * 2352)
            raw = f.read(2352)
            f.seek(sec * 2352)
            f.write(legacy.regen_sector(raw))

    verified = verify_output(out, dry["rows"], dry["cmap"], atlas_before, mapping_before)
    cue = write_cue(out)
    lines = report_lines(
        dry,
        "GUARDED BUILD + STATIC BYTE VERIFICATION PASS",
        base=base,
        out=out,
        changed=len(changed),
        owners=len(touched),
        verify=verified,
    )
    lines.append(f"Output CUE                         : {cue}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"Report: {report}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("[ERROR]", repr(e))
        raise SystemExit(9)
