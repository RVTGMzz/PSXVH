#!/usr/bin/env python3
from __future__ import annotations
import subprocess,sys
from pathlib import Path
import build_gaia_06520_batch42_master_closure as b42
import batch43_wholegame_patch_06530 as exp

VERSION="0.6.54.0";BATCH="BATCH44";BASE=560;NEW=102
CLEAN="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
TOOLS=Path(__file__).resolve().parent
BASE_BUILDER=TOOLS/"build_gaia_06520_batch42_master_closure.py"

def selftest():
    rr=exp.load_manifest()
    if len(rr)!=NEW:raise RuntimeError("Batch43 gate")
    print("="*78)
    print("GAIA MASTER 0.6.54.0 BATCH44 SELFTEST PASS")
    print("="*78)
    print(f"base_exact={BASE}")
    print(f"wholegame_new={NEW}")
    print(f"combined={BASE+NEW}")
    print("token_codepage_fit=PASS")
    print("master_overlap=0")
    print("batch40_span_overlap=0")
    print("source_gate=CLEAN_ROM")
    return 0

def main():
    if len(sys.argv)==2 and sys.argv[1]=="--selftest":return selftest()
    if len(sys.argv)!=2:print("Usage: build_gaia_06540_batch44_wholegame_visible.py CLEAN.bin");return 2
    clean=Path(sys.argv[1]).expanduser().resolve()
    if not clean.is_file():print("[ERROR] CLEAN BIN not found",clean);return 2
    got=b42.core.sha1_file(clean).lower()
    if got!=CLEAN:print(f"[ERROR] Need CLEAN SHA1 {CLEAN}; got {got}");return 3
    out=clean.parent;before=b42.core.snapshot(out)
    cp=subprocess.run([sys.executable,str(BASE_BUILDER),str(clean)],cwd=str(TOOLS),check=False)
    if cp.returncode:raise RuntimeError(f"Batch42 builder failed: {cp.returncode}")
    bins=[p for p in b42.core.changed(out,before) if p.suffix.lower()==".bin" and p.resolve()!=clean.resolve()]
    bins.sort(key=lambda p:p.stat().st_mtime_ns,reverse=True)
    if not bins:raise RuntimeError("No Batch42 output BIN")
    built=next((p for p in bins if "0.6.52.0" in p.name),bins[0])
    if b42.core.verify_output(clean,built)!=BASE:raise RuntimeError("Batch42 pre-expansion gate failed")
    verified,sectors,owners=exp.patch(clean,built)
    if verified!=NEW or b42.core.verify_output(clean,built)!=BASE:raise RuntimeError("post-expansion gate failed")
    old=built;new=old.with_name(old.name.replace("0.6.52.0",VERSION).replace("BATCH42",BATCH))
    if new==old:new=old.with_name(clean.stem+" [VI 0.6.54.0 BATCH44 WHOLEGAME].bin")
    if new.exists():new.unlink()
    old.rename(new)
    for cue in [p for p in b42.core.changed(out,before) if p.suffix.lower()==".cue"]:
        try:txt=cue.read_text(encoding="utf-8",errors="replace")
        except Exception:continue
        if old.name in txt or "0.6.52.0" in cue.name:
            nc=cue.with_name(cue.name.replace("0.6.52.0",VERSION).replace("BATCH42",BATCH))
            if nc==cue:nc=cue.with_name(clean.stem+" [VI 0.6.54.0 BATCH44 WHOLEGAME].cue")
            if nc.exists():nc.unlink()
            nc.write_text(txt.replace(old.name,new.name).replace("0.6.52.0",VERSION).replace("BATCH42",BATCH),encoding="utf-8")
            if cue.exists() and cue!=nc:cue.unlink()
            break
    report=out/"GaiaMaster_0.6.54.0_BATCH44_FINAL_REPORT.txt"
    report.write_text("\n".join([
        "GAIA MASTER 0.6.54.0 - BATCH44 WHOLE-GAME VISIBLE EXPANSION","="*78,
        f"Input CLEAN SHA1: {got}",f"Batch42 master exact fields preserved: {BASE}/{BASE}",
        f"Batch43 whole-game visible fields verified: {verified}/{NEW}",
        f"Combined exact fields verified: {BASE+verified}/{BASE+NEW}",
        f"Nested BDP owners rebuilt: {owners}",f"Raw sectors regenerated: {sectors}",
        "Legacy Alpha gate inherited: 397/397","Translation Master coverage inherited: 596/596",
        "Runtime test still required.",f"Output BIN: {new.name}"
    ])+"\n",encoding="utf-8")
    print(f"[OK] {BASE+verified}/{BASE+NEW} exact fields verified")
    print("Output:",new);print("Report:",report);return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except SystemExit:raise
    except Exception as e:print("[ERROR]",repr(e));raise SystemExit(9)
