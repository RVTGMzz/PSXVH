#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,subprocess,sys,tempfile
from pathlib import Path

BASE='0ced9982e1b00566b42ace047236378826c2aa1c'
CLEAN='f4d5298583c90d89c4b7e51d2dde160ee07f2aec'
TOOLS=Path(__file__).resolve().parent

SCRIPTS={
 'r22':'gaia_b52r22_live_source_probe.py',
 'r23':'gaia_b52r23_gpu_upload_locator.py',
 'r24gen':'gaia_b52r24_trace_generator.py',
 'r24ana':'gaia_b52r24_trace_analyzer.py',
 'r25gen':'gaia_b52r25_writer_watch_generator.py',
 'r25resolve':'gaia_b52r25_writer_pc_resolver.py',
 'r27':'gaia_b52r27_disc_payload_fingerprint.py',
 'r28gen':'gaia_b52r28_cd_dma_provenance_generator.py',
 'r28ana':'gaia_b52r28_cd_dma_provenance_analyzer.py',
 'r29':'gaia_b52r29_overlay_fingerprint_resolver.py',
 'r30':'gaia_b52r30_ownership_patch_planner.py',
}

def sha1_file(p):
    h=hashlib.sha1()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest().lower()

def first(root,*patterns):
    for pat in patterns:
        xs=sorted(root.glob(pat),key=lambda p:p.stat().st_mtime,reverse=True)
        if xs:return xs[0]
    return None

def exact_rows(csvp):
    if not csvp or not csvp.is_file():return []
    with csvp.open('r',encoding='utf-8-sig',newline='') as f:
        rr=list(csv.DictReader(f))
    return [(i+1,r) for i,r in enumerate(rr) if (r.get('kind') or '').upper()=='EXACT']

def run_script(key,args,log):
    script=TOOLS/SCRIPTS[key]
    if not script.is_file():
        log.append(f'[BLOCK] missing tool {script.name}')
        return False
    cmd=[sys.executable,str(script),*map(str,args)]
    log.append('[RUN] '+' '.join(cmd))
    cp=subprocess.run(cmd,text=True,capture_output=True)
    if cp.stdout.strip():log.append(cp.stdout.strip())
    if cp.stderr.strip():log.append('[STDERR] '+cp.stderr.strip())
    if cp.returncode!=0:
        log.append(f'[STOP] {script.name} exit={cp.returncode}')
        return False
    return True

def scan(root):
    return {
      'r22_report':first(root,'GaiaMaster_B52R22_LIVE_SOURCE_PROBE_REPORT.txt'),
      'r23_csv':first(root,'GaiaMaster_B52R23_GPU_MMIO_HITS.csv'),
      'r24_lua':first(root,'GaiaMaster_B52R24_PCSX_DMA_SOURCE_CAPTURE.lua'),
      'r24_trace':first(root,'GaiaMaster_B52R24_TRACE.tsv','*B52R24*_TRACE.tsv'),
      'r24_analysis':first(root,'GaiaMaster_B52R24_ANALYSIS.txt','*B52R24*_ANALYSIS.txt'),
      'r24_payload':first(root,'GaiaMaster_B52R24_DMA_SOURCE.bin','*B52R24*_DMA_SOURCE.bin'),
      'r25_lua':first(root,'GaiaMaster_B52R25_PCSX_SOURCE_WRITER_WATCH.lua'),
      'r25_trace':first(root,'GaiaMaster_B52R25_WRITER_TRACE.tsv'),
      'r25_ram':first(root,'GaiaMaster_B52R25_WRITER_RAM.bin'),
      'r25_resolve':first(root,'GaiaMaster_B52R25_WRITER_RESOLVE.txt'),
      'r27_csv':first(root,'GaiaMaster_B52R27_DISC_FINGERPRINT_CANDIDATES.csv'),
      'r27_report':first(root,'GaiaMaster_B52R27_DISC_FINGERPRINT_REPORT.txt'),
      'r28_lua':first(root,'GaiaMaster_B52R28_PCSX_CD_DMA_PROVENANCE.lua'),
      'r28_trace':first(root,'GaiaMaster_B52R28_CD_DMA_TRACE.tsv'),
      'r28_analysis':first(root,'GaiaMaster_B52R28_CD_DMA_PROVENANCE_ANALYSIS.txt'),
      'r29_report':first(root,'GaiaMaster_B52R29_OVERLAY_FINGERPRINT_REPORT.txt'),
      'r30_plan':first(root,'GaiaMaster_B52R30_PATCH_PLAN.json'),
      'r31_report':first(root,'GaiaMaster_B52R31_GUARDED_BUILD_REPORT.txt'),
    }

def next_action(s):
    if not s['r22_report']: return ('STATIC','Run B52R22 static live-source probe.')
    if not s['r23_csv']: return ('STATIC','Run B52R23 GPU/DMA locator.')
    if not s['r24_lua']: return ('STATIC','Generate B52R24 PCSX capture Lua from B52R23 MMIO CSV.')
    if not s['r24_trace']: return ('RUNTIME',"PCSX-Redux: load GaiaMaster_B52R24_PCSX_DMA_SOURCE_CAPTURE.lua, call gaia_arm24() immediately before the green main menu, enter it, then when paused call gaia_save24().")
    if not s['r24_analysis']: return ('STATIC','Analyze the B52R24 runtime capture.')
    if s['r24_payload'] and not s['r27_report']: return ('STATIC','Run B52R27 disc fingerprint on the captured linear DMA payload.')
    if s['r24_payload'] and not s['r25_lua']: return ('STATIC','Generate B52R25 source-buffer writer watch.')
    if s['r25_lua'] and not s['r25_trace']: return ('RUNTIME',"PCSX-Redux: load B52R25 writer-watch Lua, arm before the same transition with gaia_arm25(), reproduce the target transition, pause on writer hit, then call gaia_save25().")
    if s['r25_trace'] and not s['r25_resolve']: return ('STATIC','Resolve B52R25 writer PC against the exact BIN.')
    if s['r25_trace'] and s['r25_ram'] and not s['r29_report']: return ('STATIC','Run B52R29 overlay fingerprint resolver.')
    if s['r24_trace'] and not s['r28_lua']: return ('STATIC','Generate B52R28 CD Setloc/LBA provenance Lua.')
    if s['r28_lua'] and not s['r28_trace']: return ('RUNTIME',"If direct CD provenance is still needed: load B52R28 Lua, call gaia_arm26() before the target transition, then call gaia_save26() when an overlap pauses.")
    if s['r28_trace'] and not s['r28_analysis']: return ('STATIC','Analyze B52R28 CD DMA provenance against the exact BIN.')
    ex=exact_rows(s['r27_csv'])
    if len(ex)==1 and s['r24_payload'] and not s['r30_plan']: return ('STATIC',f'Run B52R30 structural ownership planner on the single B52R27 EXACT candidate (row {ex[0][0]}).')
    if len(ex)>1 and not s['r30_plan']: return ('HUMAN',f'B52R27 has {len(ex)} EXACT rows. Correlate runtime/provenance before selecting a B52R30 candidate.')
    if s['r30_plan'] and not s['r31_report']: return ('GATE','B52R30 plan exists. Prepare the exact same-length intended replacement, rerun B52R30 with --replacement, then run B52R31 DRY-RUN only. Do not build until target ownership is proven.')
    return ('GATE','No safe automatic step remains. Review runtime correlation and ownership evidence. B52R31 BUILD must remain manual and gated.')

def advance(binpath,root,log):
    for _ in range(12):
        s=scan(root); changed=False
        if not s['r22_report']:
            if not run_script('r22',[binpath],log):break
            changed=True
        elif not s['r23_csv']:
            if not run_script('r23',[binpath],log):break
            changed=True
        elif not s['r24_lua']:
            if not run_script('r24gen',[s['r23_csv']],log):break
            changed=True
        elif s['r24_trace'] and not s['r24_analysis']:
            if not run_script('r24ana',[s['r24_trace']],log):break
            changed=True
        elif s['r24_payload'] and not s['r27_report']:
            if not run_script('r27',[s['r24_payload'],binpath],log):break
            changed=True
        elif s['r24_payload'] and not s['r25_lua']:
            if run_script('r25gen',[s['r24_trace']],log):changed=True
            else:break
        elif s['r25_trace'] and not s['r25_resolve']:
            if not run_script('r25resolve',[s['r25_trace'],binpath],log):break
            changed=True
        elif s['r25_trace'] and s['r25_ram'] and not s['r29_report']:
            if not run_script('r29',[s['r25_trace'],s['r25_ram'],binpath],log):break
            changed=True
        elif s['r24_trace'] and not s['r28_lua']:
            if not run_script('r28gen',[s['r24_trace']],log):break
            changed=True
        elif s['r28_trace'] and not s['r28_analysis']:
            if not run_script('r28ana',[s['r28_trace'],binpath],log):break
            changed=True
        else:
            ex=exact_rows(s['r27_csv'])
            if len(ex)==1 and s['r24_payload'] and not s['r30_plan']:
                row=ex[0][0]
                if not run_script('r30',[binpath,'--candidate-csv',s['r27_csv'],'--row',row,'--payload',s['r24_payload']],log):break
                changed=True
        if not changed:break

def write_report(root,binpath,sh,log):
    s=scan(root); mode,action=next_action(s)
    lines=['GAIA MASTER B52R32 CAPTURE SESSION MANAGER','='*78,
           f'BIN: {binpath}',f'SHA1: {sh}',f'Workspace: {root}','',
           'EVIDENCE FILE STATUS:']
    for k,v in s.items(): lines.append(f"- {k:14s}: {v.name if v else 'MISSING'}")
    lines += ['','NEXT ACTION:',f'[{mode}] {action}','','AUTOMATION LOG:']
    lines += log or ['- no automatic step was requested/performed']
    lines += ['','SAFETY GATES:',
              '- B52R32 never invokes B52R31 build mode.',
              '- It only auto-runs read-only/static tooling.',
              '- PCSX runtime actions are always manual.',
              '- A B52R27 exact payload match is ownership evidence, not visible-target proof by itself.',
              '- Overall Runtime PASS remains NO.']
    rp=root/'GaiaMaster_B52R32_SESSION_STATUS.txt'
    jp=root/'GaiaMaster_B52R32_SESSION_STATUS.json'
    rp.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    jp.write_text(json.dumps({'bin':str(binpath),'sha1':sh,'files':{k:(str(v) if v else None) for k,v in s.items()},'next_mode':mode,'next_action':action},indent=2),encoding='utf-8')
    print('\n'.join(lines)); print('Report:',rp)
    return mode,action

def selftest():
    with tempfile.TemporaryDirectory() as d:
        r=Path(d)
        s=scan(r); assert next_action(s)[1].startswith('Run B52R22')
        (r/'GaiaMaster_B52R22_LIVE_SOURCE_PROBE_REPORT.txt').write_text('x')
        (r/'GaiaMaster_B52R23_GPU_MMIO_HITS.csv').write_text('x')
        (r/'GaiaMaster_B52R24_PCSX_DMA_SOURCE_CAPTURE.lua').write_text('x')
        assert next_action(scan(r))[0]=='RUNTIME'
        c=r/'GaiaMaster_B52R27_DISC_FINGERPRINT_CANDIDATES.csv'
        c.write_text('kind,path,file_offset\nEXACT,PRGPACK.BDP,16\n',encoding='utf-8')
        assert len(exact_rows(c))==1
    print('B52R32 CAPTURE SESSION MANAGER SELFTEST PASS')

def main():
    ap=argparse.ArgumentParser(description='Gaia Master B52R32 evidence workflow/session manager')
    ap.add_argument('bin',nargs='?',type=Path)
    ap.add_argument('--advance-readonly',action='store_true')
    ap.add_argument('--selftest',action='store_true')
    a=ap.parse_args()
    if a.selftest:selftest();return 0
    if not a.bin:ap.error('exact B52R14R1/CLEAN BIN required')
    b=a.bin.expanduser().resolve()
    if not b.is_file():raise RuntimeError(f'BIN not found: {b}')
    sh=sha1_file(b)
    if sh not in(BASE,CLEAN):raise RuntimeError(f'Unknown BIN SHA1 {sh}')
    root=b.parent; log=[]
    if a.advance_readonly:advance(b,root,log)
    write_report(root,b,sh,log)
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except SystemExit:raise
    except Exception as e:print('[ERROR]',repr(e));raise SystemExit(9)
