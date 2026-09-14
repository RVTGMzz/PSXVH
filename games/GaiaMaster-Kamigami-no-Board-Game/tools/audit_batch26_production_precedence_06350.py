#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

VERSION = "0.6.35.0"
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
B25 = TR / "BATCH25_NEW_EXACT_OFFSET_0.6.34.0.csv"
GAMEPLAY = TR / "GAMEPLAY_ACCENT_OVERRIDES_0.6.11.0.csv"
EXTRA = TR / "BATCH3_FALLBACK_ACCENT_MAP_0.6.12.0.csv"
C13 = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.13.0.csv"
C141 = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
D14 = TR / "DYNAMIC_LITERAL_OVERRIDES_0.6.14.0.csv"
FRONT = TR / "FRONT_DEMO_ADDED_061.csv"
OUT = ROOT / "checkpoints" / VERSION / "BATCH26_PRECEDENCE_AUDIT.txt"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z])|/[Vv]")
EXPECTED = 209


def rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


def rlen(text: str) -> int:
    n = 0
    pos = 0
    for m in TOKEN.finditer(text or ""):
        n += (m.start() - pos) * 2 + len(m.group(0).encode("ascii"))
        pos = m.end()
    return n + (len(text or "") - pos) * 2


def global_map(master, gameplay_rows, extra_rows):
    by_key = {key(r): r for r in master}
    out = {}
    source = {}
    for r in gameplay_rows:
        src = by_key.get(key(r))
        if not src:
            continue
        old = (src.get("vi_game_current") or "").strip()
        val = (r.get("vi_accented") or "").strip()
        if old and val and (old not in out or rlen(val) < rlen(out[old])):
            out[old] = val
            source[old] = f"gameplay:{key(r)[0]}:{key(r)[1]}"
    for r in extra_rows:
        old = (r.get("vi_game_current") or "").strip()
        val = (r.get("vi_accented") or "").strip()
        if old and val:
            out[old] = val
            source[old] = "batch3-curated"
    return out, source


def legacy_keys(master, front):
    seen = set()
    legacy = set()
    for r in master:
        k = key(r)
        vi = (r.get("vi_game_current") or "").strip()
        if not vi or k in seen:
            continue
        try:
            field = len((r.get("japanese") or "").encode("cp932"))
        except UnicodeEncodeError:
            continue
        if rlen(vi) <= field:
            legacy.add(k)
            seen.add(k)
    for r in front:
        k = ("PRGPACK.BDP", hex(int(r["offset_hex"], 0)).lower())
        if k in seen:
            continue
        field = len((r.get("japanese") or "").encode("cp932"))
        vi = (r.get("vi_no_accents") or "").strip()
        if rlen(vi) > field:
            raise RuntimeError(f"front fallback stopped fitting: {k}")
        legacy.add(k)
        seen.add(k)
    return legacy


def main():
    original = []
    part_rows = []
    for p in PARTS:
        rr = rows(p)
        original.extend(rr)
        part_rows.append((p, rr))
    by_key = {key(r): r for r in original}
    targets = {key(r): (r.get("vi_accented") or "").strip() for r in rows(B25)}
    errors = []
    if len(targets) != EXPECTED:
        errors.append(f"Batch25 target count {len(targets)} != {EXPECTED}")
    missing = sorted(set(targets) - set(by_key))
    if missing:
        errors.append(f"Batch25 keys missing Translation Master: {len(missing)}")

    gameplay_all = rows(GAMEPLAY)
    c13_all = rows(C13)
    c141_all = rows(C141)
    dyn = rows(D14)
    extra = rows(EXTRA)

    gameplay_hits = [r for r in gameplay_all if key(r) in targets]
    c13_hits = [r for r in c13_all if key(r) in targets]
    c141_hits = [r for r in c141_all if key(r) in targets]

    dynamic_hits = []
    for k, want in targets.items():
        src = by_key.get(k)
        if not src:
            continue
        jp = src.get("japanese") or ""
        for d in dyn:
            scope = (d.get("file_scope") or "AUTO").strip()
            if (d.get("japanese") or "") == jp and (scope.upper() == "AUTO" or scope == k[0]):
                dynamic_hits.append((k, jp, want, (d.get("vi_accented") or "").strip()))

    # Filtering gameplay exact rows changes the Batch-2 exemplar input to the
    # 0.6.12 global map. Compute the exact fallback entries a wrapper must add
    # temporarily to EXTRA so global behavior for every non-target row stays identical.
    gm_before, src_before = global_map(original, gameplay_all, extra)
    gameplay_filtered = [r for r in gameplay_all if key(r) not in targets]
    gm_after, _ = global_map(original, gameplay_filtered, extra)
    preserve = {old: val for old, val in gm_before.items() if gm_after.get(old) != val}

    # Simulate wrapper Translation Master layout. Primary target rows keep exact
    # wording but hide vi_game_current from global promotion. A shadow duplicate
    # placed immediately after preserves the legacy-fallback reconstruction.
    sim = []
    shadow_count = 0
    for r in original:
        rr = dict(r)
        k = key(rr)
        if k not in targets:
            sim.append(rr)
            continue
        fallback = (rr.get("vi_game_current") or "")
        rr["vi_full"] = targets[k]
        rr["vi_game_current"] = ""
        sim.append(rr)
        if fallback.strip():
            sh = dict(r)
            sh["vi_full"] = ""
            sh["note"] = ((sh.get("note") or "") + " | Batch26 legacy shadow").strip()
            sim.append(sh)
            shadow_count += 1

    # 0.6.14 exact layer, using codepage-safe .1 and filtering Batch25 targets.
    sim_by_key_first = {}
    for r in sim:
        sim_by_key_first.setdefault(key(r), r)
    for o in c141_all:
        k = key(o)
        if k in targets:
            continue
        if k in sim_by_key_first:
            sim_by_key_first[k]["vi_full"] = (o.get("vi_accented") or "").strip()

    # 0.6.13 exact layer, also filtered on Batch25 targets.
    for o in c13_all:
        k = key(o)
        if k in targets:
            continue
        if k in sim_by_key_first:
            sim_by_key_first[k]["vi_full"] = (o.get("vi_accented") or "").strip()

    # 0.6.12 global promotion. Temporary preservation entries make its global
    # map byte-for-byte equivalent to the unfiltered production behavior.
    gm_sim = dict(gm_after)
    gm_sim.update(preserve)
    if gm_sim != gm_before:
        errors.append("preserved global fallback map does not equal original map")
    for r in sim:
        old = (r.get("vi_game_current") or "").strip()
        if not old or old not in gm_sim:
            continue
        target = gm_sim[old]
        try:
            field = len((r.get("japanese") or "").encode("cp932"))
        except UnicodeEncodeError:
            continue
        if rlen(target) <= field:
            cur = (r.get("vi_full") or "").strip()
            if not cur or rlen(target) <= rlen(cur):
                r["vi_full"] = target

    # 0.6.11 static exact layer is filtered for target keys. Its dynamic layer
    # is NOT safe to filter globally unless proven collision-free, so any hit is
    # a hard blocker for this wrapper design.
    for o in gameplay_filtered:
        k = key(o)
        if k in sim_by_key_first:
            sim_by_key_first[k]["vi_full"] = (o.get("vi_accented") or "").strip()

    final_wrong = []
    for k, want in targets.items():
        got = (sim_by_key_first.get(k, {}).get("vi_full") or "").strip()
        if got != want:
            final_wrong.append((k, want, got))

    legacy_original = legacy_keys(original, rows(FRONT))
    legacy_sim = legacy_keys(sim, rows(FRONT))
    if len(legacy_original) != 397:
        errors.append(f"original legacy gate is {len(legacy_original)}, expected 397")
    if legacy_sim != legacy_original:
        errors.append(f"shadow strategy changes legacy key set: {len(legacy_sim)} vs {len(legacy_original)}")
    if final_wrong:
        errors.append(f"final exact precedence mismatches: {len(final_wrong)}")
    if dynamic_hits:
        errors.append(f"effective 0.6.14 dynamic collisions need guard: {len(dynamic_hits)}")

    lines = [
        f"GAIA MASTER {VERSION} BATCH 26 PRODUCTION PRECEDENCE AUDIT",
        "=" * 76,
        f"Batch25 new exact targets          : {len(targets)}",
        f"Legacy shadow rows required        : {shadow_count}",
        f"0.6.11 exact collisions to mask    : {len(gameplay_hits)}",
        f"0.6.13 exact collisions to mask    : {len(c13_hits)}",
        f"0.6.14.1 exact collisions to mask  : {len(c141_hits)}",
        f"Global-map preservation entries    : {len(preserve)}",
        f"Effective 0.6.14 dynamic collisions: {len(dynamic_hits)}",
        f"Legacy gate before                 : {len(legacy_original)}",
        f"Legacy gate with shadows           : {len(legacy_sim)}",
        f"Final exact mismatches (static)     : {len(final_wrong)}",
        f"Errors                              : {len(errors)}",
        "",
        "Planned wrapper contract:",
        "- inject Batch25 exact vi_full into primary rows",
        "- blank primary vi_game_current and append legacy shadow duplicates",
        "- temporarily use 0.6.14.1 compact table in the 0.6.14 slot",
        "- mask Batch25 exact keys from 0.6.11/0.6.13/0.6.14 exact tables",
        "- preserve the original 0.6.12 global fallback map through temporary EXTRA entries",
        "- do not filter dynamic literals unless the audit proves a safe per-key guard",
        "- restore every mutable repo source after build",
    ]
    if preserve:
        lines += ["", "GLOBAL MAP ENTRIES TO PRESERVE:"]
        for old, val in sorted(preserve.items()):
            lines.append(f"- {old!r} -> {val!r} ({src_before.get(old, '')})")
    if dynamic_hits:
        lines += ["", "DYNAMIC COLLISION BLOCKERS:"]
        for k, jp, want, dynval in dynamic_hits:
            lines.append(f"- {k[0]} {k[1]} JP={jp!r}: exact={want!r} dynamic={dynval!r}")
    if final_wrong:
        lines += ["", "FINAL EXACT MISMATCHES:"]
        for k, want, got in final_wrong[:50]:
            lines.append(f"- {k[0]} {k[1]}: want={want!r} got={got!r}")
    if errors:
        lines += ["", "ERRORS:"] + [f"- {e}" for e in errors]
    else:
        lines += ["", "RESULT: STATIC PRECEDENCE PASS"]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
