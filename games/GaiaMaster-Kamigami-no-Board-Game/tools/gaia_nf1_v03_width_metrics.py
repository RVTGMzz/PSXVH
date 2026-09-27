#!/usr/bin/env python3
from __future__ import annotations
import argparse, html
from pathlib import Path
import gaia_nf1_full_font_art_v02 as v02

REFERENCE_LINES = [
    "Hoàng tử ơi!",
    "Người lại ra phố",
    "chơi bài nữa sao!?",
    "Your duellist code has",
    "been recorded.",
]

def bbox(g):
    pts=[(x,y) for y,row in enumerate(g) for x,v in enumerate(row) if v]
    if not pts:return None
    return min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)

def advance_width(ch):
    if ch==" ":
        return 4
    g=v02.render(ch)
    b=bbox(g)
    if b is None:
        return 4
    x0,y0,x1,y1=b
    ink=x1-x0+1
    # One blank column after most glyphs. Narrow punctuation stays compact.
    if ch in "ilI.,:;'!|":
        return max(3,ink+1)
    if ch in "mwMW@%":
        return min(9,ink+2)
    return min(8,max(4,ink+1))

def source_width(ch):
    g=v02.render(ch);b=bbox(g)
    return 0 if b is None else b[2]-b[0]+1

def draw_line_svg(text,scale=4):
    x=0
    pieces=[]
    for ch in text:
        g=v02.render(ch)
        b=bbox(g)
        if b:
            x0,y0,x1,y1=b
            for yy,row in enumerate(g):
                for xx,val in enumerate(row):
                    if val:
                        pieces.append((x+(xx-x0),yy))
        x+=advance_width(ch)
    w=max(1,x)
    h=12
    return pieces,w,h

def write_preview(out:Path):
    out.parent.mkdir(parents=True,exist_ok=True)
    scale=5
    line_gap=18
    rendered=[]
    maxw=0
    for t in REFERENCE_LINES:
        pts,w,h=draw_line_svg(t,scale)
        rendered.append((t,pts,w,h))
        maxw=max(maxw,w)
    W=maxw*scale+80
    H=len(rendered)*(12*scale+line_gap)+80
    q=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<rect width="100%" height="100%" fill="#151525"/>',
       '<text x="20" y="24" font-family="monospace" font-size="14" fill="#bbb">NF1 V0.3 proportional-metrics preview</text>']
    oy=42
    for text,pts,w,h in rendered:
        for x,y in pts:
            q.append(f'<rect x="{20+x*scale}" y="{oy+y*scale}" width="{scale}" height="{scale}" fill="#f4f4f4"/>')
        q.append(f'<text x="{30+w*scale}" y="{oy+42}" font-family="monospace" font-size="12" fill="#999">{html.escape(text)} / width={w}</text>')
        oy+=12*scale+line_gap
    q.append('</svg>')
    out.write_text("\n".join(q)+"\n",encoding="utf-8")

def write_metrics(out:Path):
    chars=v02.ASCII_PRINTABLE+v02.FULL_VI_NONASCII
    lines=["char,codepoint,ink_width,advance"]
    for ch in chars:
        label=ch.replace('"','""')
        lines.append(f'"{label}",U+{ord(ch):04X},{source_width(ch)},{advance_width(ch)}')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(lines)+"\n",encoding="utf-8-sig")

def selftest():
    chars=v02.ASCII_PRINTABLE+v02.FULL_VI_NONASCII
    assert len(chars)==229
    for ch in chars:
        a=advance_width(ch)
        assert 3<=a<=9, (ch,a)
    assert advance_width("i") < advance_width("W")
    assert advance_width(".") < advance_width("M")
    assert advance_width(" ") == 4
    for line in REFERENCE_LINES:
        for ch in line:
            if ch!=" ":
                v02.render(ch)
    print("NF1 V0.3 WIDTH METRICS SELFTEST PASS")
    print("glyphs=229")
    print("reference_lines=%d"%len(REFERENCE_LINES))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--selftest",action="store_true")
    ap.add_argument("--svg",type=Path)
    ap.add_argument("--csv",type=Path)
    a=ap.parse_args()
    if a.selftest:selftest()
    if a.svg:
        write_preview(a.svg);print("SVG:",a.svg)
    if a.csv:
        write_metrics(a.csv);print("CSV:",a.csv)
    if not (a.selftest or a.svg or a.csv):ap.print_help()

if __name__=="__main__":
    main()
