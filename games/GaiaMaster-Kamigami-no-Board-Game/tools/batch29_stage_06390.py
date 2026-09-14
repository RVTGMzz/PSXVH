#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import hashlib
import re
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
TARGETS = TR / "BATCH29_NEW_EXACT_OFFSET_0.6.39.0.csv"
FINAL = TR / "BATCH29_FINAL_EXACT_SET_0.6.39.0.csv"
GAMEPLAY = TR / "GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv"
EXTRA = TR / "BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv"
C13 = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv"
C140 = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.0.csv"
C141 = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
D14 = TR / "DYNAMIC_LITERAL_OVERRIDES_0.6.14.0.csv"
FRONT = TR / "FRONT_DEMO_ADDED_061.csv"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z])|/[Vv]")


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            raise RuntimeError(f"No CSV header: {path}")
        return list(r.fieldnames), list(r)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), lineterminator="\n", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


def rlen(text: str) -> int:
    n = 0; pos = 0
    for m in TOKEN.finditer(text or ""):
        n += (m.start() - pos) * 2 + len(m.group(0).encode("ascii"))
        pos = m.end()
    return n + (len(text or "") - pos) * 2


def sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def global_map(master, gameplay_rows, extra_rows):
    by_key = {key(r): r for r in master}
    out = {}; source = {}
    for r in gameplay_rows:
        src = by_key.get(key(r))
        if not src: continue
        old = (src.get("vi_game_current") or "").strip()
        val = (r.get("vi_accented") or "").strip()
        if old and val and (old not in out or rlen(val) < rlen(out[old])):
            out[old] = val; source[old] = f"gameplay:{key(r)[0]}:{key(r)[1]}"
    for r in extra_rows:
        old = (r.get("vi_game_current") or "").strip()
        val = (r.get("vi_accented") or "").strip()
        if old and val:
            out[old] = val; source[old] = "batch3-curated-or-preserve"
    return out, source


def legacy_keys(master, front_rows):
    seen = set(); out = set()
    for r in master:
        k = key(r)
        vi = (r.get("vi_game_current") or "").strip()
        if not vi or k in seen: continue
        try: field = len((r.get("japanese") or "").encode("cp932"))
        except UnicodeEncodeError: continue
        if rlen(vi) <= field:
            out.add(k); seen.add(k)
    for r in front_rows:
        k = ("PRGPACK.BDP", hex(int(r["offset_hex"], 0)).lower())
        if k in seen: continue
        jp = r.get("japanese") or ""
        vi = (r.get("vi_no_accents") or "").strip()
        field = len(jp.encode("cp932"))
        if rlen(vi) > field:
            raise RuntimeError(f"Front legacy row no longer fits: {k}")
        out.add(k); seen.add(k)
    return out


def build_plan():
    original = []; part_data = []
    for p in PARTS:
        fields, rr = read_csv(p)
        original.extend(rr); part_data.append((p, fields, rr))
    by_key = {key(r): r for r in original}

    _, target_rows = read_csv(TARGETS)
    targets = {}
    for r in target_rows:
        k = key(r)
        text = (r.get("vi_accented") or "").strip()
        if k in targets and targets[k] != text:
            raise RuntimeError(f"Conflicting Batch29 target: {k}")
        targets[k] = text
    if not targets:
        raise RuntimeError("Batch29 target manifest is empty")
    missing = sorted(set(targets) - set(by_key))
    if missing:
        raise RuntimeError(f"Batch29 keys missing Translation Master: {missing[:8]}")

    _, final_rows = read_csv(FINAL)
    final_map = {key(r): (r.get("vi_accented") or "").strip() for r in final_rows}
    if not final_map or not set(targets).issubset(final_map):
        raise RuntimeError("Batch29 final verification set missing new target keys")

    gp_fields, gameplay_all = read_csv(GAMEPLAY)
    ex_fields, extra_all = read_csv(EXTRA)
    c13_fields, c13_all = read_csv(C13)
    c140_fields, _ = read_csv(C140)
    c141_fields, c141_all = read_csv(C141)
    _, dyn = read_csv(D14)
    _, front = read_csv(FRONT)
    if c140_fields != c141_fields:
        raise RuntimeError("0.6.14.0/.1 compact headers differ")

    gameplay_filtered = [r for r in gameplay_all if key(r) not in targets]
    c13_filtered = [r for r in c13_all if key(r) not in targets]
    c14_filtered = [r for r in c141_all if key(r) not in targets]

    dynamic_hits = []
    for k, want in targets.items():
        jp = by_key[k].get("japanese") or ""
        for d in dyn:
            scope = (d.get("file_scope") or "AUTO").strip()
            if (d.get("japanese") or "") == jp and (scope.upper() == "AUTO" or scope == k[0]):
                dynamic_hits.append((k, jp, want, (d.get("vi_accented") or "").strip()))
    dynamic_same = [x for x in dynamic_hits if x[2] == x[3]]
    dynamic_diff = [x for x in dynamic_hits if x[2] != x[3]]
    sink_keys = {x[0] for x in dynamic_diff}

    gm_before, gm_source = global_map(original, gameplay_all, extra_all)
    gm_after, _ = global_map(original, gameplay_filtered, extra_all)
    preserve = {old: val for old, val in gm_before.items() if gm_after.get(old) != val}
    extra_staged = [dict(r) for r in extra_all]
    for old, val in sorted(preserve.items()):
        extra_staged.append({
            "vi_game_current": old,
            "vi_accented": val,
            "category": "batch29-preserve",
            "note": "Temporary wrapper row preserving original 0.6.12 global-map semantics after exact-key masking",
        })
    gm_check, _ = global_map(original, gameplay_filtered, extra_staged)
    if gm_check != gm_before:
        raise RuntimeError("Temporary EXTRA rows fail to preserve original global map")

    staged_parts = []; shadows = 0; sinks = 0
    for p, fields, rr in part_data:
        out = []
        for src in rr:
            k = key(src)
            if k not in targets:
                out.append(dict(src)); continue
            if k in sink_keys:
                sink = dict(src)
                sink["japanese"] = ""
                sink["vi_full"] = ""
                sink["vi_game_current"] = ""
                sink["status"] = "BATCH29_DYNAMIC_SINK"
                sink["note"] = "Batch29 per-key dynamic sink; zero-byte source field forces base builder skip"
                out.append(sink); sinks += 1
            primary = dict(src)
            fallback = primary.get("vi_game_current") or ""
            primary["vi_full"] = targets[k]
            primary["vi_game_current"] = ""
            primary["note"] = ((primary.get("note") or "") + " | Batch29 final exact primary").strip()
            out.append(primary)
            if fallback.strip():
                shadow = dict(src)
                shadow["vi_full"] = ""
                shadow["note"] = ((shadow.get("note") or "") + " | Batch29 legacy shadow").strip()
                out.append(shadow); shadows += 1
        staged_parts.append((p, fields, out))

    original_legacy = legacy_keys(original, front)
    staged_master = [r for _, _, rr in staged_parts for r in rr]
    staged_legacy = legacy_keys(staged_master, front)
    if len(original_legacy) != 397:
        raise RuntimeError(f"Baseline legacy gate drift: {len(original_legacy)}/397")
    if staged_legacy != original_legacy:
        raise RuntimeError(f"Batch29 staging changes legacy key set: {len(staged_legacy)} vs 397")

    counts = {
        "targets": len(targets),
        "final_verify": len(final_map),
        "shadows": shadows,
        "sinks": sinks,
        "gameplay_mask": len(gameplay_all) - len(gameplay_filtered),
        "compact13_mask": len(c13_all) - len(c13_filtered),
        "compact14_mask": len(c141_all) - len(c14_filtered),
        "preserve": len(preserve),
        "dynamic_hits": len(dynamic_hits),
        "dynamic_same": len(dynamic_same),
        "dynamic_diff": len(dynamic_diff),
        "legacy": len(staged_legacy),
    }
    return {
        "targets": targets,
        "final_map": final_map,
        "original": original,
        "staged_parts": staged_parts,
        "gameplay_fields": gp_fields,
        "gameplay_rows": gameplay_filtered,
        "extra_fields": ex_fields,
        "extra_rows": extra_staged,
        "c13_fields": c13_fields,
        "c13_rows": c13_filtered,
        "c140_fields": c140_fields,
        "c140_rows": c14_filtered,
        "sink_keys": sink_keys,
        "global_before": gm_before,
        "global_source": gm_source,
        "preserve": preserve,
        "dynamic_hits": dynamic_hits,
        "counts": counts,
    }


def verify_staged(plan):
    master = []
    for p in PARTS:
        _, rr = read_csv(p); master.extend(rr)
    _, gp = read_csv(GAMEPLAY)
    _, ex = read_csv(EXTRA)
    _, c13 = read_csv(C13)
    _, c140 = read_csv(C140)
    _, front = read_csv(FRONT)
    targets = plan["targets"]

    if any(key(r) in targets for r in gp):
        raise RuntimeError("Staged 0.6.11 gameplay file still contains Batch29 exact key")
    if any(key(r) in targets for r in c13):
        raise RuntimeError("Staged 0.6.13 compact file still contains Batch29 exact key")
    if any(key(r) in targets for r in c140):
        raise RuntimeError("Staged 0.6.14 compact file still contains Batch29 exact key")
    gm, _ = global_map(plan["original"], gp, ex)
    if gm != plan["global_before"]:
        raise RuntimeError("Staged global fallback map differs from production baseline")
    if legacy_keys(master, front) != legacy_keys(plan["original"], front):
        raise RuntimeError("Staged master fails exact legacy-key preservation")

    for k, want in targets.items():
        matches = [r for r in master if key(r) == k]
        primary = [r for r in matches if (r.get("japanese") or "") and (r.get("vi_full") or "").strip() == want and not (r.get("vi_game_current") or "").strip()]
        if len(primary) != 1:
            raise RuntimeError(f"Staged primary exact row count != 1 for {k}: {len(primary)}")
        if k in plan["sink_keys"]:
            sinks = [r for r in matches if (r.get("status") or "") == "BATCH29_DYNAMIC_SINK" and not (r.get("japanese") or "")]
            if len(sinks) != 1:
                raise RuntimeError(f"Staged dynamic sink count != 1 for {k}")


def mutable_files():
    return [*PARTS, GAMEPLAY, EXTRA, C13, C140]


@contextmanager
def staged_sources(plan=None):
    plan = plan or build_plan()
    files = mutable_files()
    backups = {p: p.read_bytes() for p in files}
    hashes = {p: sha1_bytes(data) for p, data in backups.items()}
    try:
        for p, fields, rr in plan["staged_parts"]:
            write_csv(p, fields, rr)
        write_csv(GAMEPLAY, plan["gameplay_fields"], plan["gameplay_rows"])
        write_csv(EXTRA, plan["extra_fields"], plan["extra_rows"])
        write_csv(C13, plan["c13_fields"], plan["c13_rows"])
        write_csv(C140, plan["c140_fields"], plan["c140_rows"])
        verify_staged(plan)
        yield plan
    finally:
        errors = []
        for p, data in backups.items():
            try: p.write_bytes(data)
            except Exception as e: errors.append(f"{p}: {e}")
        for p in files:
            try:
                if sha1_bytes(p.read_bytes()) != hashes[p]:
                    errors.append(f"hash mismatch after restore: {p}")
            except Exception as e:
                errors.append(f"restore verify failed {p}: {e}")
        if errors:
            raise RuntimeError("Batch29 source restoration failed: " + " | ".join(errors))


if __name__ == "__main__":
    plan = build_plan()
    with staged_sources(plan):
        pass
    print("BATCH29 STAGING SELFTEST PASS")
    print(plan["counts"])
