#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION = "0.6.42.0"
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
B29 = TR / "BATCH29_FINAL_EXACT_SET_0.6.39.0.csv"
HIST = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
B19 = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv"
OUT = TR / "BATCH32_CURATED_COMPACT_0.6.42.0.csv"
REPORT = ROOT / "checkpoints" / VERSION / "BATCH32_CURATED_COMPACT_REPORT.txt"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN = set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")

# Japanese-keyed manual compact translations. These are curated from the
# Batch31 residual report. No fallback-only inference is allowed here.
CURATED = {
    "武器カードを": "Thẻ VK",
    "武器カードは": "Thẻ VK",
    "やるね": "Hay",
    "終了ターン": "Hết",
    "%sのラッキー！！": "%s hên!",
    "病院": "BV",
    "なにか捨ててね": "Bỏ bớt",
    "騎士団": "Kỵ",
    "お店破壊": "Phá!",
    "武器屋": "VK",
    "%dゼニーはらってね": "Trả %dZ",
    "修道会": "Đạo",
    "攻撃力を２倍にアップさせる": "Công x2",
    "いやしのうた": "Hồi HP",
    "指定武器カード１枚を盗む": "Cướp thẻ VK",
    "盗賊のオーブ": "Trộm",
    "クリティカルがでやすい": "Hay CM",
    "防御　速度７　使い捨て": "Thủ SPD7 1L",
    "使い捨てアイテム": "Đồ 1L",
    "みがわり": "Thế",
    "あいての命中率を落とす": "Giảm CX",
    "ブラッドスピア": "G.Máu",
    "ＨＰを６０回復する": "Hồi 60HP",
    "死亡するとＨＰ１００で復活": "Hồi sinh100HP",
    "復活の霊薬": "Sống",
}


def rows(path: Path):
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r):
    return r["file"].strip(), hex(int(r["offset_hex"], 0)).lower()


def tokens(text):
    return tuple(m.group(0) for m in TOKEN.finditer(text or ""))


def rlen(text: str) -> int:
    total = 0; pos = 0
    for m in TOKEN.finditer(text or ""):
        total += (m.start() - pos) * 2 + len(m.group(0).encode("ascii")); pos = m.end()
    return total + (len(text or "") - pos) * 2


def bad_chars(text: str):
    out = []
    for ch in text or "":
        if ord(ch) < 128:
            continue
        try:
            ch.encode("cp932"); continue
        except UnicodeEncodeError:
            pass
        if ch not in FROZEN:
            out.append(ch)
    return sorted(set(out))


def master_rows():
    out=[]; seen=set()
    for p in PARTS:
        for r in rows(p):
            k=key(r)
            if k in seen: raise RuntimeError(f"duplicate Translation Master key: {k}")
            seen.add(k); out.append(r)
    if len(out) != 596: raise RuntimeError(f"Translation Master row gate {len(out)} != 596")
    return out


def historical_fit(master):
    by={key(r):r for r in master}; out=set()
    for r in rows(HIST):
        k=key(r); src=by.get(k); text=(r.get("vi_accented") or "").strip()
        if not src or not text: continue
        jp=src.get("japanese") or ""
        try: field=len(jp.encode("cp932"))
        except UnicodeEncodeError: continue
        if rlen(text)<=field and tokens(jp)==tokens(text) and not bad_chars(text): out.add(k)
    return out


def main():
    master=master_rows()
    protected={key(r) for r in rows(B29)} | {key(r) for r in rows(B19)} | historical_fit(master)
    out=[]; errors=[]; jp_hits={jp:0 for jp in CURATED}; skipped_protected=0
    for r in master:
        k=key(r); jp=(r.get("japanese") or "").strip(); fallback=(r.get("vi_game_current") or "").strip()
        if jp not in CURATED or not fallback: continue
        jp_hits[jp]+=1
        if k in protected:
            skipped_protected+=1; continue
        text=CURATED[jp]
        try: field=len(jp.encode("cp932"))
        except UnicodeEncodeError:
            errors.append(f"Japanese not CP932: {k} {jp!r}"); continue
        used=rlen(text)
        if used>field: errors.append(f"too long {used}>{field}: {k} {jp!r} -> {text!r}")
        if tokens(jp)!=tokens(text): errors.append(f"token mismatch: {k} {jp!r} -> {text!r}")
        bad=bad_chars(text)
        if bad: errors.append(f"unsupported chars {bad!r}: {k} {text!r}")
        out.append({
            "file":k[0],"offset_hex":k[1],"japanese":jp,"vi_accented":text,
            "field_bytes":field,"vi_bytes":used,"free_bytes":field-used,
            "old_fallback":fallback,"vi_full":(r.get("vi_full") or "").strip(),
            "source":"batch32-curated-japanese-key",
        })

    missing=[jp for jp,n in jp_hits.items() if n==0]
    if missing: errors.append(f"curated Japanese keys missing master: {missing!r}")
    out.sort(key=lambda r:(r["file"],int(r["offset_hex"],16)))
    fields=["file","offset_hex","japanese","vi_accented","field_bytes","vi_bytes","free_bytes","old_fallback","vi_full","source"]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n"); w.writeheader(); w.writerows(out)

    REPORT.parent.mkdir(parents=True,exist_ok=True)
    distinct=len({r["japanese"] for r in out})
    exact_full=sum(1 for r in out if r["free_bytes"]==0)
    lines=[
        f"GAIA MASTER {VERSION} BATCH 32 CURATED COMPACT",
        "="*76,
        f"Curated Japanese keys        : {len(CURATED)}",
        f"Curated keys producing rows  : {distinct}",
        f"Protected hits skipped       : {skipped_protected}",
        f"New exact rows exported      : {len(out)}",
        f"Exact-full-field rows        : {exact_full}",
        f"Errors                       : {len(errors)}",
        "",
        "RULES:",
        "- Japanese-keyed manual curation only",
        "- B29/Batch19/runtime-fit historical exact keys are protected",
        "- runtime tokens preserve identity and order",
        "- every compact candidate must fit the original CP932 field",
        "- every non-CP932 glyph must belong to the frozen Vietnamese codepage",
        "- no ROM/font/pointer modification",
    ]
    if errors: lines += ["","ERRORS:"]+[f"- {e}" for e in errors]
    else: lines += ["","RESULT: STATIC CURATED PASS"]
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
