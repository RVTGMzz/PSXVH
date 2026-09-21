#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,struct
from pathlib import Path

CLEAN="f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
BASE="0ced9982e1b00566b42ace047236378826c2aa1c"
RAW,USER=2352,2048
MAX_FILE=64*1024*1024
ANCHOR=64

def sha1(p):
    h=hashlib.sha1()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return h.hexdigest().lower()

def sector_user(f,lba):
    f.seek(lba*RAW);s=f.read(RAW)
    if len(s)!=RAW or s[15]!=2 or s[16:20]!=s[20:24]:raise RuntimeError(f"Bad MODE2 sector {lba}")
    if s[18]&0x20:return None
    return s[24:24+USER]

def read_extent(f,lba,size):
    out=bytearray();left=size;cur=lba
    while left:
        u=sector_user(f,cur)
        if u is None:return None
        n=min(USER,left);out+=u[:n];left-=n;cur+=1
    return bytes(out)

def rec_name(rec):
    n=rec[32];name=rec[33:33+n]
    if name in (b"\x00",b"\x01"):return None
    return name.decode("ascii","replace").split(";")[0]

def index_iso(binpath):
    files=[];seen=set()
    with binpath.open("rb") as f:
        pvd=sector_user(f,16)
        if pvd is None or pvd[1:6]!=b"CD001":raise RuntimeError("ISO9660 PVD not found")
        root=pvd[156:156+pvd[156]]
        root_extent=struct.unpack_from("<I",root,2)[0];root_size=struct.unpack_from("<I",root,10)[0]
        def walk(ext,size,prefix):
            key=(ext,size)
            if key in seen:return
            seen.add(key)
            data=read_extent(f,ext,size)
            if data is None:return
            i=0
            while i<len(data):
                ln=data[i]
                if ln==0:
                    i=((i//USER)+1)*USER
                    continue
                rec=data[i:i+ln]
                if len(rec)<34:break
                name=rec_name(rec);flags=rec[25];e=struct.unpack_from("<I",rec,2)[0];sz=struct.unpack_from("<I",rec,10)[0]
                i+=ln
                if name is None:continue
                path=(prefix+"/"+name) if prefix else name
                if flags&2:walk(e,sz,path)
                else:files.append((path,e,sz))
        walk(root_extent,root_size,"")
    return files

def anchor_bases(payload,data):
    if len(payload)<ANCHOR:return {}
    offs=sorted(set([0,max(0,len(payload)//2-ANCHOR//2),max(0,len(payload)-ANCHOR)]))
    bases={}
    for aid,so in enumerate(offs):
        a=payload[so:so+ANCHOR];start=0;seen=0
        while seen<64:
            p=data.find(a,start)
            if p<0:break
            bases.setdefault(p-so,set()).add(aid)
            start=p+1;seen+=1
    return bases

def classify(payload,data):
    p=data.find(payload)
    if p>=0:return ("EXACT",p,3 if len(payload)>=ANCHOR else 1)
    bases=anchor_bases(payload,data)
    if not bases:return ("NONE",-1,0)
    base,hits=max(bases.items(),key=lambda kv:len(kv[1]))
    n=len(hits)
    return (f"ALIGNED_{n}_ANCHOR" if n>1 else "SINGLE_ANCHOR",base,n)

def selftest():
    payload=bytes(range(256))*2
    data=b"xxxx"+payload+b"yyyy"
    assert classify(payload,data)[0]=="EXACT"
    mod=bytearray(payload);mod[200]^=1
    c=classify(bytes(mod),data)
    assert c[0].startswith("ALIGNED_") and c[2]>=2
    print("B52R27 DISC FINGERPRINT SELFTEST PASS")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("payload",nargs="?",type=Path)
    ap.add_argument("bin",nargs="?",type=Path)
    ap.add_argument("--selftest",action="store_true")
    a=ap.parse_args()
    if a.selftest:selftest();return 0
    if not a.payload or not a.bin:ap.error("DMA_SOURCE.bin and exact B52R14R1/CLEAN BIN required")
    b=a.bin.resolve();payload=a.payload.read_bytes();sh=sha1(b)
    if sh not in (BASE,CLEAN):raise RuntimeError(f"Unknown BIN SHA1 {sh}")
    if not payload:raise RuntimeError("Empty payload")
    entries=index_iso(b);rows=[];skipped=0
    with b.open("rb") as f:
        for path,ext,size in entries:
            if size>MAX_FILE:
                skipped+=1;continue
            data=read_extent(f,ext,size)
            if data is None:
                skipped+=1;continue
            kind,base,hits=classify(payload,data)
            if kind=="NONE":continue
            start=max(0,base)
            lba=ext+(start//USER);uoff=start%USER
            rows.append(dict(kind=kind,anchors=hits,path=path,file_size=size,file_offset=start,start_lba=lba,user_offset=uoff,extent_lba=ext))
    rank={"EXACT":4,"ALIGNED_3_ANCHOR":3,"ALIGNED_2_ANCHOR":2,"SINGLE_ANCHOR":1}
    rows.sort(key=lambda r:(-rank.get(r["kind"],0),r["path"],r["file_offset"]))
    out=a.payload.parent
    csvp=out/"GaiaMaster_B52R27_DISC_FINGERPRINT_CANDIDATES.csv"
    rpt=out/"GaiaMaster_B52R27_DISC_FINGERPRINT_REPORT.txt"
    with csvp.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["kind","anchors","path","file_size","file_offset","start_lba","user_offset","extent_lba"])
        w.writeheader();w.writerows(rows)
    exact=[r for r in rows if r["kind"]=="EXACT"];aligned=[r for r in rows if r["kind"].startswith("ALIGNED_")]
    lines=["GAIA MASTER B52R27 DISC PAYLOAD FINGERPRINT","="*78,
           f"BIN SHA1      : {sh}",f"Payload bytes : {len(payload)}",f"Payload SHA1  : {hashlib.sha1(payload).hexdigest()}",
           f"ISO files     : {len(entries)}",f"Skipped       : {skipped}",f"Candidates    : {len(rows)}",
           f"Exact hits    : {len(exact)}",f"Aligned hits  : {len(aligned)}",""]
    if exact:
        lines.append("VERDICT: EXACT_DISC_PAYLOAD_MATCH_FOUND")
        for r in exact[:20]:lines.append(f"- {r['path']} +0x{r['file_offset']:X} -> LBA {r['start_lba']} + user 0x{r['user_offset']:X}")
    elif aligned:
        lines.append("VERDICT: ALIGNED_ANCHOR_EVIDENCE_ONLY")
        for r in aligned[:20]:lines.append(f"- {r['kind']} {r['path']} base +0x{r['file_offset']:X}")
    else:lines.append("VERDICT: NO_DISC_FINGERPRINT_MATCH")
    lines += ["","INTERPRETATION:",
              "- EXACT is strong evidence that the captured payload exists verbatim inside an ISO file at the reported offset/LBA.",
              "- ALIGNED anchors are suggestive only; confirm transformation/copy/decompression before patching.",
              "- NO match suggests transformation/decompression/rasterization/composition, or a skipped/non-Form1 stream.",
              "- This tool does not repair BDP checksums and does not patch the disc.",
              "- Overall Runtime PASS remains NO.",f"CSV: {csvp.name}"]
    rpt.write_text("\n".join(lines)+"\n",encoding="utf-8");print("\n".join(lines));print("Report:",rpt);return 0
if __name__=="__main__":raise SystemExit(main())
