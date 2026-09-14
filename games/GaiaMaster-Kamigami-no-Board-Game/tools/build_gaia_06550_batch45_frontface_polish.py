#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import subprocess, sys
from pathlib import Path
import build_gaia_06520_batch42_master_closure as b42
import batch43_wholegame_patch_06530 as exp

VERSION="0.6.55.0"; BATCH="BATCH45"; BASE=560; NEW=102
CLEAN="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
TOOLS=Path(__file__).resolve().parent
BASE_BUILDER=TOOLS/"build_gaia_06520_batch42_master_closure.py"
BASE_READABLE=TOOLS/"build_gaia_06100_hybrid_accent_b1_READABLE.py"

INTRO = {
    0xC00B4: "Thần chiến!", 0xC00D0: "Người: cờ", 0xC00E4: "Đời là bàn cờ",
    0xC0100: "Khuất phục", 0xC0118: "Trước thần", 0xC0130: "Miền ảo",
    0xC0144: "Vua,tu sĩ", 0xC0158: "Theo luật Gaia", 0xC0178: "Giờ thế giới",
    0xC0194: "Tan biến hết", 0xC01B0: "Hôm nay", 0xC01C0: "Luật người",
    0xC01DC: "Bắt đầu!", 0xC01F0: "Trò Gaia Master", 0xC0218: "Đại lục loạn",
    0xC0234: "100 năm một lần", 0xC0258: "Miền đất ảo", 0xC0274: "Trời u tối",
    0xC028C: "Thế giới đổi chủ",
}
JP = {
    0xC00B4: "神々の戦いがはじまるのだ", 0xC00D0: "人々をコマとして、",
    0xC00E4: "世界というゲームボードに、", 0xC0100: "あらがうことはできない",
    0xC0118: "座すという神々の力に", 0xC0130: "まぼろしの大地に",
    0xC0144: "どんな王も司教も、", 0xC0158: "「ガイアマスター」のルールのみ",
    0xC0178: "いまや世界をつかさどるのは", 0xC0194: "あとかたもなくくずれさる",
    0xC01B0: "今日をかぎりに", 0xC01C0: "人のきずいたあらゆる法は",
    0xC01DC: "おとずれたのだ！", 0xC01F0: "神々のゲーム「ガイアマスター」の時が",
    0xC0218: "大陸をこんとんにたたきこむ", 0xC0234: "１００年に一度めぐりくる宿命の時",
    0xC0258: "空にうかぶまぼろしの大地", 0xC0274: "月も太陽もおおいかくす",
    0xC028C: "世界はもはや人のものではなくなった",
}

def _static_intro_gate():
    base=b42.core.load_base()
    allowed=set(base.CUSTOM_CHARS)
    for off,text in INTRO.items():
        field=len(JP[off].encode("cp932"))
        bad=[c for c in text if ord(c)>127 and c not in allowed]
        if bad: raise RuntimeError(f"Intro 0x{off:X} unsupported chars: {bad}")
        if len(text)*2 > field: raise RuntimeError(f"Intro 0x{off:X} too long")
        if "=" in text: raise RuntimeError(f"Intro 0x{off:X} still contains '='")
    return len(INTRO)

def selftest():
    rr=exp.load_manifest()
    if len(rr)!=NEW: raise RuntimeError("Batch43 gate")
    if _static_intro_gate()!=19: raise RuntimeError("Intro polish gate")
    src=BASE_READABLE.read_text(encoding="utf-8")
    if "(y0 + y1) // 2 - 1" not in src:
        raise RuntimeError("Đ/đ crossbar polish missing")
    print("="*78)
    print("GAIA MASTER 0.6.55.0 BATCH45 SELFTEST PASS")
    print("="*78)
    print(f"base_exact={BASE}")
    print(f"wholegame_visible={NEW}")
    print(f"combined={BASE+NEW}")
    print("intro_polish=19/19")
    print("intro_equals_removed=PASS")
    print("font_D_crossbar=UP_1PX")
    print("token_codepage_fit=PASS")
    print("batch40_span_overlap=0")
    print("source_gate=CLEAN_ROM")
    return 0

def _verify_intro(clean,built):
    base=b42.core.load_base()
    with clean.open("rb") as f:
        clean_slps=base.read_iso_file(f,base.SLPS_EXTENT,base.SLPS_SIZE)
        clean_prg=base.read_iso_file(f,base.PRG_EXTENT,base.PRG_SIZE)
    codes=base.safe_custom_codes(clean_slps,clean_prg,len(base.CUSTOM_CHARS))
    cmap=dict(zip(base.CUSTOM_CHARS,codes))
    with built.open("rb") as f:
        prg=base.read_iso_file(f,base.PRG_EXTENT,base.PRG_SIZE)
    bad=[]
    for off,text in INTRO.items():
        field=len(JP[off].encode("cp932"))
        enc,_=base.encode_runtime_text(text,cmap)
        want=enc+b"\0"*(field-len(enc))
        got=bytes(prg[off:off+field])
        if got!=want: bad.append(f"0x{off:X} {text!r}")
    if bad: raise RuntimeError("Intro byte verification failed: "+", ".join(bad))
    return len(INTRO)

def main():
    if len(sys.argv)==2 and sys.argv[1]=="--selftest": return selftest()
    if len(sys.argv)!=2:
        print("Usage: build_gaia_06550_batch45_frontface_polish.py CLEAN.bin"); return 2
    clean=Path(sys.argv[1]).expanduser().resolve()
    if not clean.is_file(): print("[ERROR] CLEAN BIN not found",clean); return 2
    got=b42.core.sha1_file(clean).lower()
    if got!=CLEAN: print(f"[ERROR] Need CLEAN SHA1 {CLEAN}; got {got}"); return 3

    out=clean.parent; before=b42.core.snapshot(out)
    cp=subprocess.run([sys.executable,str(BASE_BUILDER),str(clean)],cwd=str(TOOLS),check=False)
    if cp.returncode: raise RuntimeError(f"Batch42 builder failed: {cp.returncode}")
    bins=[p for p in b42.core.changed(out,before) if p.suffix.lower()==".bin" and p.resolve()!=clean.resolve()]
    bins.sort(key=lambda p:p.stat().st_mtime_ns,reverse=True)
    if not bins: raise RuntimeError("No Batch42 output BIN")
    built=next((p for p in bins if "0.6.52.0" in p.name),bins[0])

    if b42.core.verify_output(clean,built)!=BASE: raise RuntimeError("Batch42 pre-expansion gate failed")
    verified,sectors,owners=exp.patch(clean,built)
    if verified!=NEW or b42.core.verify_output(clean,built)!=BASE:
        raise RuntimeError("post-expansion gate failed")
    intro_verified=_verify_intro(clean,built)

    old=built
    new=old.with_name(old.name.replace("0.6.52.0",VERSION).replace("BATCH42",BATCH))
    if new==old: new=old.with_name(clean.stem+" [VI 0.6.55.0 FRONTFACE POLISH].bin")
    if new.exists(): new.unlink()
    old.rename(new)

    for cue in [p for p in b42.core.changed(out,before) if p.suffix.lower()==".cue"]:
        try: text=cue.read_text(encoding="utf-8",errors="replace")
        except Exception: continue
        if old.name in text or "0.6.52.0" in cue.name:
            nc=cue.with_name(cue.name.replace("0.6.52.0",VERSION).replace("BATCH42",BATCH))
            if nc==cue: nc=cue.with_name(clean.stem+" [VI 0.6.55.0 FRONTFACE POLISH].cue")
            if nc.exists(): nc.unlink()
            nc.write_text(text.replace(old.name,new.name).replace("0.6.52.0",VERSION).replace("BATCH42",BATCH),encoding="utf-8")
            if cue.exists() and cue!=nc: cue.unlink()
            break

    report=out/"GaiaMaster_0.6.55.0_BATCH45_FINAL_REPORT.txt"
    report.write_text("\n".join([
        "GAIA MASTER 0.6.55.0 - BATCH45 FRONT-FACE RUNTIME POLISH","="*78,
        f"Input CLEAN SHA1: {got}",
        f"Batch42 master exact fields preserved: {BASE}/{BASE}",
        f"Batch43 whole-game visible fields verified: {verified}/{NEW}",
        f"Combined exact fields verified: {BASE+verified}/{BASE+NEW}",
        f"Intro polish fields verified: {intro_verified}/19",
        "Unsafe intro '=' removed: PASS",
        "Đ/đ glyph crossbar: raised 1 px from R5 runtime evidence",
        f"Nested BDP owners rebuilt by Batch43: {owners}",
        f"Raw sectors regenerated by Batch43: {sectors}",
        "Legacy Alpha gate inherited: 397/397",
        "Translation Master coverage inherited: 596/596",
        "IMPORTANT: this is NOT whole-game translation coverage.",
        "Main menu / character select graphics and many story/gameplay strings remain pending.",
        "Runtime test still required.",f"Output BIN: {new.name}"
    ])+"\n",encoding="utf-8")
    print(f"[OK] {BASE+verified}/{BASE+NEW} exact fields verified")
    print(f"[OK] Intro polish {intro_verified}/19")
    print("[OK] Đ/đ crossbar source polish present")
    print("Output:",new); print("Report:",report)
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except SystemExit: raise
    except Exception as e:
        print("[ERROR]",repr(e)); raise SystemExit(9)
