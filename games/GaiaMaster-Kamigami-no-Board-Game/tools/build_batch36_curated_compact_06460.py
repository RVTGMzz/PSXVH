#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION = "0.6.46.0"
ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "translation"
PARTS = [TR / f"TRANSLATION_MASTER_0.6_part{i:02d}.csv" for i in range(1, 7)]
PROTECTED_FINAL = TR / "BATCH33_FINAL_EXACT_SET_0.6.43.0.csv"
HIST = TR / "COMPACT_TRANSLATION_OVERRIDES_0.6.14.1.csv"
B19 = ROOT / "checkpoints" / "0.6.28.0" / "reports" / "GaiaMaster_0.6.28.0_EXACT_OFFSET_LOCKS.csv"
OUT = TR / "BATCH36_CURATED_COMPACT_0.6.46.0.csv"
REPORT = ROOT / "checkpoints" / VERSION / "BATCH36_CURATED_COMPACT_REPORT.txt"
TOKEN = re.compile(r"%(?:[-+0-9.#]*[A-Za-z%])|/[Vv]")
FROZEN = set("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")

# Large Japanese-keyed manual compact sweep after Batch34.
# Every candidate is intentionally bounded by the original CP932 field.
CURATED = {
    "れん金術": "Giả", "最強の弓": "Cung", "アースクエイク": "Đ.đất", "エクスカリバー": "Excal",
    "フェザーレイ": "Feath", "ダメージの１／２を奪う": "Hút 1/2 DMG", "アイテムを使えなくする": "Khóa đồ",
    "伝説の聖剣": "Kiếm", "ストームソード": "K.bão", "ほのおの弓": "C.lửa", "最強の魔剣": "Ma",
    "ダークメテオ": "Meteor", "メテオフォール": "Meteor", "魔剣ムラマサ": "Murama", "まどわしの玉": "Ngọc",
    "力の指輪": "Lực", "ＧＯマス": "Ô GO", "最強の魔法": "Phép+", "封いんされた魔法": "Phong ấn",
    "%dゼニー": "%d Z", "(速い者順)": "(Tốc)", "１ターンのあいだ自分の番だけ、": "1 lượt của bạn",
    "トカードが１枚": "1 thẻ", "の２０％を税金": "Thuế20%", "ダイス３つ": "3 xúc", "ダイス４つ": "4 xúc",
    "どの物件を売るの？": "Bán đâu?", "どの物件を売る？": "Bán đâu?", "スノーストーム": "B.tuyết",
    "飛ばすぜ ！！": "Bay!!", "シンボル": "Biểu", "この シンボルは": "Biểu:", "どれを捨てる？": "Bỏ gì?",
    "金斗雲": "Mây", "あーあ": "Ôi", "お店破壊なんてガードしちゃえ！！": "Chặn phá shop!!",
    "早く決めてってばぁ～": "Nhanh!", "早く決めてよね！！": "Nhanh!!", "物件を決めたら、": "Chọn TS,",
    "どこを戻すの？": "Chuộc?", "メイス": "Búa", "何がおこるのかな": "Có gì?", "できます": "Được",
    "を切りかえられ": "Đổi", "しかけることが": "Mở", "戦いをしかけることができるよ": "Thách đấu được",
    "戦闘をしかけることができるよ！": "Thách đấu được!", "氷の弓": "Ice", "ルートを切りかえたよ": "Đã đổi",
    "大幸運": "May", "大不幸": "Xui", "我に 近付くとは": "Dám gần", "呪いの沼": "Đầm",
    "どの土地をせめる？": "Đánh đất?", "盗賊の援助": "Trộm+", "いっちょう やってみっか": "Đấu nhé?",
    "あいてに戦闘を": "Đấu", "ＧＯマスおくり": "Tới GO", "ダメージ": "Sát", "カスが": "Rác",
    "大不幸、不幸で": "Do xui", "全ての分岐マスを切りかえて、": "Đổi mọi rẽ", "を入れかえちゃう": "Đổi chỗ",
    "土地の持ち主が変わったよ": "Đổi chủ đất", "ルートが切りか": "Đổi", "本当にやめるの？": "Dừng?",
    "このカードを使えば、ライバルに": "Dùng thẻ địch", "このカードを使うと、": "Dùng thẻ:", "止まると土地代": "Đất",
    "止まるとミニゲ": "Mini", "止まるとイベン": "Sự kiện", "止まると所持金": "Tiền có", "止まると好きな": "Tùy",
    "価値    %4d": "Giá%4d", "ダメージを１／２にへらす": "Giảm 1/2 DMG", "魔王しょうかん": "Gọi ma",
    "聖地に 預けておいたから": "Gửi Thánh", "もう持ち切れないよ": "Hết chỗ", "あっなんか": "Ơ...",
    "回復系": "Hồi", "大国の混乱": "Loạn", "あいての体力": "HPđịch", "体力が０になったから、ちりょうひ": "HP0 trả viện phí",
    "自分が止まると": "Dừng", "関係なかったみたい": "Không sao", "なんか 気がのらん": "Chán", "買えません": "Không",
    "このエリアはあなたたちのものよ！！": "Khu của các bạn!!", "このエリアはあなたのものよ！！": "Khu của bạn!!",
    "せつなの剣": "Kiếm", "します": "Làm", "も～何やってるの？": "Làm gì?", "魔王の気まぐれ": "Ma quậy",
    "魔王のこうりん": "Ma tới", "領地購入": "Mua", "この土地を買うよ": "Mua đất", "はかば": "Mộ", "墓地": "Mộ",
    "孫悟空": "Ngộ", "%dゼニーもらっちゃった": "Nhận %d Z", "土地を１つもらえるよ！！": "Nhận 1 đất!!",
    "多くもらっちゃった": "Nhận thêm", "プール金取得": "Quỹ", "２００ゼニーをもらうわよ！": "Nhận 200Z!",
    "如意棒": "Gậy", "野太刀": "Đao", "女神像": "Nữ", "シンボルを一つ壊せるよ": "Phá 1 biểu",
    "どれを壊すの？": "Phá gì?", "ランダム武器破壊": "Phá VK", "武器破壊": "Phá",
    "通行税 %+3d％": "Phí%+3d%", "通行税  %4d": "Phí%4d", "通行税 %4d": "Phí%4d",
    "１０％、まわりの通行税ダウン！": "Phí giảm10%", "まわりの通行税が３０％下がるよ！": "Phí giảm30%",
    "まわりの通行税が５０％下がるよ！": "Phí giảm50%", "まわりの通行税が７０％下がるよ！": "Phí giảm70%",
    "まわりの通行税が９０％下がるよ！": "Phí giảm90%", "通行税": "Phí", "なにぃ～い 通行税だと？": "Phí à?",
    "まわりの通行税が３０％上がるよ！": "Phí tăng30%", "まわりの通行税が５０％上がるよ！": "Phí tăng50%",
    "まわりの通行税が７０％上がるよ！": "Phí tăng70%", "まわりの通行税が２倍になるよ！": "Phí x2",
    "まわりの通行税が３倍になるよ！": "Phí x3", "ダーツ": "Phi", "通過するとお金": "Qua +$", "軍資金": "Quỹ",
    "聖地で 引き落としてね": "Rút Thánh", "もらえます": "Nhận", "俺さまが遊んでやるぜ！": "Ta chơi!",
    "邪神像": "Tà", "物件": "TS", "投射": "Xa", "土地名": "Tên", "エリア名": "Khu",
    "して戦闘をしかける": "Thách đấu", "戦いをしかけるよ？": "Đấu nhé?", "時の神のいたず": "Thời",
    "いたずら好きの時の神がみんなの場所": "Thần TG đổi chỗ", "運の神の休息": "May", "大聖堂": "Đền",
    "悪魔の塔": "Ma", "かいしめ": "Thâu", "バトルカード": "Thẻ", "レベル５裏武器カード": "VK ẩn LV5",
    "レベル５表武器カード": "VK LV5", "抵当": "TC", "抵当額": "TC$", "もう１回行動できるよ！！": "Thêm lượt!!",
    "お金が足りないけど": "Thiếu $", "お金たりないじゃない！": "Thiếu tiền!", "不足金額： %dゼニー": "Thiếu:%dZ",
    "土地税": "TĐ", "所得税": "TN", "所得税、土地税": "TN/TĐ", "我が けんぞくよ": "Hạ ta",
    "もらえるお金が倍になるよ！！": "Tiền nhận x2!!", "お金が 持ち切れないみたい": "Tiền đầy", "不足金額": "Nợ",
    "小領主の協力": "L.chúa", "速度が速い": "Nhanh", "最大 99999までよ": "TĐ99999", "合計金額": "Tổng",
    "戦いをさけられる": "Tránh", "もうっ！": "Ôi!", "はんぶん盗めるよ！！": "Trộm 1/2!!",
    "ほかの人と同じマスに止まったよ": "Trùng ô người", "死神像": "Tử", "修道会が戦いを止めてくれたよ": "Tu viện ngăn",
    "やったー！！": "Hay!!", "大国の援助": "Viện+", "所有者なし": "Trống", "土地マスを無効にできるよ": "Vô hiệu đất",
    "特殊マスが効かなくなっちゃう": "Vô hiệu ô ĐB", "無属性": "Vô", "どこに建てる？": "Xây?", "悪いな%s": "Xin%s",
    "ダイスの数が３つになるよ": "Xúc xắc x3", "ダイスの数が４つになるよ": "Xúc xắc x4",
    "「ルート変更」": "「Đổi」", "「お店破壊」": "「Phá」", "「バトルカード」": "「Thẻ」",
}


def rows(path: Path):
    if not path.is_file(): return []
    with path.open("r", encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

def key(r): return r["file"].strip(), hex(int(r["offset_hex"],0)).lower()
def tokens(text): return tuple(m.group(0) for m in TOKEN.finditer(text or ""))

def rlen(text: str) -> int:
    n=0; pos=0
    for m in TOKEN.finditer(text or ""):
        n += (m.start()-pos)*2 + len(m.group(0).encode("ascii")); pos=m.end()
    return n + (len(text or "")-pos)*2

def bad_chars(text: str):
    out=[]
    for ch in text or "":
        if ord(ch)<128: continue
        try: ch.encode("cp932"); continue
        except UnicodeEncodeError: pass
        if ch not in FROZEN: out.append(ch)
    return sorted(set(out))

def master_rows():
    out=[]; seen=set()
    for p in PARTS:
        for r in rows(p):
            k=key(r)
            if k in seen: raise RuntimeError(f"duplicate master key: {k}")
            seen.add(k); out.append(r)
    if len(out)!=596: raise RuntimeError(f"master gate {len(out)} != 596")
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
    protected={key(r) for r in rows(PROTECTED_FINAL)} | {key(r) for r in rows(B19)} | historical_fit(master)
    out=[]; errors=[]; hits={jp:0 for jp in CURATED}; skipped=0
    for r in master:
        k=key(r); jp=(r.get("japanese") or "").strip(); fallback=(r.get("vi_game_current") or "").strip()
        if jp not in CURATED or not fallback: continue
        hits[jp]+=1
        if k in protected: skipped+=1; continue
        text=CURATED[jp]
        try: field=len(jp.encode("cp932"))
        except UnicodeEncodeError:
            errors.append(f"CP932 source failure {k}: {jp!r}"); continue
        used=rlen(text)
        if used>field:
            errors.append(f"too long {used}>{field}: {k} {text!r}"); continue
        if tokens(jp)!=tokens(text):
            errors.append(f"token mismatch {k}: {tokens(jp)} != {tokens(text)}"); continue
        bad=bad_chars(text)
        if bad:
            errors.append(f"unsupported chars {bad!r}: {k} {text!r}"); continue
        out.append({"file":k[0],"offset_hex":k[1],"japanese":jp,"vi_accented":text,
                    "field_bytes":field,"vi_bytes":used,"free_bytes":field-used,
                    "source":"BATCH36_CURATED_COMPACT_0.6.46.0","category":"batch36-curated-compact"})
    missing=[jp for jp,n in hits.items() if n==0]
    if missing: errors.append(f"curated Japanese keys missing from master: {missing[:12]!r}")
    if not out: errors.append("no rows exported")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=["file","offset_hex","japanese","vi_accented","field_bytes","vi_bytes","free_bytes","source","category"]
    with OUT.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n"); w.writeheader()
        w.writerows(sorted(out,key=lambda r:(r["file"],int(r["offset_hex"],16))))
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    full=sum(1 for r in out if int(r["free_bytes"])==0)
    lines=[f"GAIA MASTER {VERSION} BATCH 36 LARGE CURATED COMPACT","="*80,
           f"Curated Japanese keys        : {len(CURATED)}",f"Curated keys producing rows  : {sum(1 for n in hits.values() if n)}",
           f"Protected hits skipped       : {skipped}",f"New exact rows exported      : {len(out)}",
           f"Exact-full-field rows        : {full}",f"Errors                       : {len(errors)}","",
           "RULES:","- Japanese-keyed manual curation only","- B33/Batch19/runtime-fit historical exact keys are protected",
           "- runtime tokens preserve identity and order","- every candidate must fit the original CP932 field",
           "- every non-CP932 glyph must belong to the frozen Vietnamese codepage","- no ROM/font/pointer modification"]
    if errors: lines += ["","ERRORS:"]+[f"- {e}" for e in errors]
    else: lines += ["","RESULT: STATIC CURATED PASS"]
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))
    return 1 if errors else 0

if __name__ == "__main__": raise SystemExit(main())
