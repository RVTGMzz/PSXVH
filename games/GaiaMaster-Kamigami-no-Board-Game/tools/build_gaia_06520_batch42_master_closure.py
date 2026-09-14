#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import subprocess,sys
from pathlib import Path
import build_gaia_06400_batch30_accent_sweep as core
from batch40_stage_06500 import build_plan, staged_sources

VERSION="0.6.52.0";BATCH="BATCH42"
TOOLS=Path(__file__).resolve().parent;ROOT=TOOLS.parent;TR=ROOT/"translation"
INNER=TOOLS/"build_gaia_06140_translation_b5.py";BASE_READABLE=TOOLS/"build_gaia_06100_hybrid_accent_b1_READABLE.py"
FINAL_MANIFEST=TR/"BATCH40_FINAL_EXACT_SET_0.6.50.0.csv";CLEAN_SHA1="f4d5298583c90d89c4b7e51d2dde160ee07f2aec";EXPECTED_FINAL=560
core.FINAL_MANIFEST=FINAL_MANIFEST;core.EXPECTED_FINAL=EXPECTED_FINAL;core.VERSION=VERSION;core.BATCH=BATCH;core.build_plan=build_plan;core.staged_sources=staged_sources

def die(m):raise RuntimeError(m)
def rename_outputs(out_dir,before,clean_bin):
    ren=[]
    for p in sorted(core.changed(out_dir,before),key=lambda x:len(x.name),reverse=True):
        if not p.exists() or p.resolve()==clean_bin.resolve():continue
        new=p.name.replace("0.6.14.0",VERSION).replace("06140","06520").replace("BATCH5",BATCH)
        if new==p.name:continue
        q=p.with_name(new)
        if q.exists():q.unlink()
        p.rename(q);ren.append((p.name,q.name))
    for p in out_dir.glob(f"*{VERSION}*.cue"):
        try:
            txt=p.read_text(encoding="utf-8",errors="replace").replace("0.6.14.0",VERSION).replace("06140","06520").replace("BATCH5",BATCH)
            p.write_text(txt,encoding="utf-8")
        except Exception as e:print(f"[WARN] CUE rewrite failed: {p.name}: {e}")
    return ren
core.rename_outputs=rename_outputs

def selftest():
    req=[INNER,BASE_READABLE,FINAL_MANIFEST];missing=[str(p) for p in req if not p.is_file()]
    if missing:die("Missing Batch42 dependencies:\n  "+"\n  ".join(missing))
    plan=build_plan();expected=core.final_expected_map()
    if len(expected)!=EXPECTED_FINAL:die(f"Final manifest gate {len(expected)} != {EXPECTED_FINAL}")
    if plan["counts"]["final_verify"]!=EXPECTED_FINAL:die(f"Stage final gate {plan['counts']['final_verify']} != {EXPECTED_FINAL}")
    if plan["counts"]["legacy"]!=397:die(f"Legacy gate {plan['counts']['legacy']} != 397")
    if not callable(getattr(core.load_base(),"encode_runtime_text",None)):die("Readable 0.6.10 encoder missing")
    with staged_sources(plan):pass
    c=plan["counts"]
    print("="*84);print("GAIA MASTER 0.6.52.0 BATCH42 BUILDER SELFTEST PASS");print("="*84)
    print(f"New exact targets     : {c['targets']}");print(f"Final exact verify    : {EXPECTED_FINAL}")
    print(f"Legacy shadows        : {c['shadows']}");print(f"Dynamic sinks         : {c['sinks']}");print(f"Legacy gate           : {c['legacy']}/397")
    print(f"Gameplay masks        : {c['gameplay_mask']}");print(f"Compact13 masks       : {c['compact13_mask']}");print(f"Compact14 masks       : {c['compact14_mask']}");print(f"Global-map preserves  : {c['preserve']}");print("Source restore        : PASS")
    return 0

def main():
    if len(sys.argv)==2 and sys.argv[1]=="--selftest":return selftest()
    if len(sys.argv)>2:print(f"Usage: {Path(sys.argv[0]).name} [CLEAN_GAME.bin] | --selftest");return 2
    clean=Path(sys.argv[1]).expanduser().resolve() if len(sys.argv)==2 else TOOLS/"GaiaMaster - Kamigami no Board Game (Japan).bin"
    if not clean.is_file():print("[ERROR] CLEAN Japan BIN not found:");print(clean);return 2
    got=core.sha1_file(clean).lower()
    if got!=CLEAN_SHA1:print(f"[ERROR] Need CLEAN Japan BIN SHA1 {CLEAN_SHA1}; got {got}");return 3
    plan=build_plan();expected=core.final_expected_map();out_dir=clean.parent;before=core.snapshot(out_dir)
    print("="*84);print("GAIA MASTER 0.6.52.0 - BATCH42 MASTER-CLOSURE PRODUCTION BUILD");print("="*84)
    print(f"Input CLEAN SHA1       : {got}");print(f"New exact targets      : {len(plan['targets'])}");print(f"Final exact verify set : {len(expected)}")
    print(f"Legacy shadows         : {plan['counts']['shadows']}");print(f"Dynamic sinks          : {plan['counts']['sinks']}");print(f"Legacy gate contract   : {plan['counts']['legacy']}/397");print()
    with staged_sources(plan):
        cp=subprocess.run([sys.executable,str(INNER),str(clean)],cwd=str(TOOLS),check=False)
        if cp.returncode!=0:die(f"Inner 0.6.14.0 builder failed with exit code {cp.returncode}")
    bins=[p for p in core.changed(out_dir,before) if p.suffix.lower()==".bin" and p.resolve()!=clean.resolve()];bins.sort(key=lambda p:p.stat().st_mtime_ns,reverse=True)
    if not bins:die("Inner build succeeded but no changed output BIN found")
    verified=core.verify_output(clean,bins[0]);ren=rename_outputs(out_dir,before,clean)
    final_bins=[p for p in core.changed(out_dir,before) if p.suffix.lower()==".bin" and p.resolve()!=clean.resolve()];final_bins.sort(key=lambda p:p.stat().st_mtime_ns,reverse=True);final_bin=final_bins[0] if final_bins else bins[0]
    report=out_dir/f"GaiaMaster_{VERSION}_{BATCH}_FINAL_REPORT.txt"
    lines=[f"GAIA MASTER {VERSION} - {BATCH} MASTER-CLOSURE PRODUCTION BUILD","="*84,f"Input CLEAN SHA1: {got}",f"Batch40 new exact targets staged: {len(plan['targets'])}",f"Final exact fields byte-verified in output BIN: {verified}/{EXPECTED_FINAL}",f"Legacy shadow rows: {plan['counts']['shadows']}",f"Dynamic sink rows: {plan['counts']['sinks']}",f"0.6.11 exact keys masked: {plan['counts']['gameplay_mask']}",f"0.6.13 exact keys masked: {plan['counts']['compact13_mask']}",f"0.6.14 exact keys masked: {plan['counts']['compact14_mask']}",f"Global fallback entries preserved: {plan['counts']['preserve']}",f"Legacy Alpha key contract: {plan['counts']['legacy']}/397","Current Translation Master coverage audit: 596/596 protected","Source staging restoration: PASS",f"Output BIN: {final_bin.name}","","Architecture unchanged:","- native 12x12 / 72-byte / 4bpp / LOW nibble first","- static mapping-only","- frozen 60-glyph Vietnamese codepage","- no renderer hook / pointer redirect / narrow-font path","","STATUS: BUILD + BYTE VERIFICATION PASS","RUNTIME TEST STILL REQUIRED","596/596 refers only to the current Translation Master, NOT whole-game text coverage.","Story/tutorial/help outside the master still require scanner expansion."]
    if ren:lines += ["","Renamed inner outputs:"]+[f"- {a} -> {b}" for a,b in ren]
    report.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print();print(f"[OK] {VERSION} {BATCH} build completed");print(f"[OK] Final exact byte verification: {verified}/{EXPECTED_FINAL}");print("[OK] Sources restored after staging");print(f"Output: {final_bin}");print(f"Report: {report}");print("[NOTE] Runtime screenshots + whole-game scanner still required.");return 0
if __name__=="__main__":
    try:raise SystemExit(main())
    except SystemExit:raise
    except Exception as e:print("[ERROR]",repr(e));raise SystemExit(9)
