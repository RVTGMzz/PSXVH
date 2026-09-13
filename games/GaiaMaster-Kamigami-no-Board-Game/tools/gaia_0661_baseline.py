#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import build_gaia_0654_native_base as n
import build_gaia_0655_accent_safe as a
import build_gaia_0660_production_encoder as p

def fit_body_native(g, marks):
    src=n.bbox(g)
    if src is None: raise RuntimeError("empty native glyph")
    x0,sy0,x1,sy1=src
    top=any(x in marks for x in ("\u0306","\u0302","\u031B","\u0301","\u0300","\u0309","\u0303"))
    bottom="\u0323" in marks
    top_need=2 if top else 0
    bottom_limit=10 if bottom else 11
    if sy0>=top_need and sy1<=bottom_limit:
        return [r[:] for r in g],src,src,"native-preserved"
    sh=sy1-sy0+1; dy1=min(sy1,bottom_limit); dy0=max(top_need,dy1-sh+1)
    if dy0>dy1: dy0,dy1=top_need,bottom_limit
    dh=dy1-dy0+1; out=[[0]*12 for _ in range(12)]
    for dy in range(dh):
        sy=sy0 if dh==1 else sy0+int(round(dy*(sh-1)/float(dh-1)))
        out[dy0+dy]=g[sy][:]
    return out,src,n.bbox(out),"minimal-fit"

def make_vi_glyph(slps,ch,cache):
    base,marks=p.decompose(ch)
    if base not in cache: cache[base]=p.native_base(slps,base)
    code,slot,raw,bg=cache[base]
    fill,shadow,hist=a.choose_layers(bg)
    g,src,body,mode=fit_body_native(bg,marks)
    x0,y0,x1,y1=body; cx=(x0+x1)//2; t1=max(0,y0-1); t2=max(0,y0-2)
    def dual(pts): a.draw_dual(g,pts,fill,shadow)
    if "\u0306" in marks: dual([(cx-2,t1),(cx-1,t2),(cx,t2),(cx+1,t2),(cx+2,t1)])
    if "\u0302" in marks: dual([(cx-1,t1),(cx,t2),(cx+1,t1)])
    if "\u031B" in marks:
        hx=min(10,x1+1); dual([(hx,y0),(min(10,hx+1),max(0,y0-1))])
    if "stroke" in marks:
        yy=max(y0,min(y1,(y0+y1)//2)); dual([(max(0,x0-1),yy),(x0,yy),(min(11,x0+1),yy),(min(11,x0+2),yy)])
    if "\u0301" in marks: dual([(cx+1,t2),(cx,t1)])
    if "\u0300" in marks: dual([(cx-1,t2),(cx,t1)])
    if "\u0309" in marks: dual([(cx,t2),(cx+1,t2),(cx+1,t1),(cx,t1)])
    if "\u0303" in marks: dual([(cx-2,t1),(cx-1,t2),(cx,t1),(cx+1,t1),(cx+2,t2)])
    if "\u0323" in marks: dual([(cx,min(11,y1+1))])
    return n.encode_glyph(g),{
        "base":base,"native_code":code,"native_slot":slot,"fit":mode,
        "src_bbox":src,"body_bbox":body,"final_bbox":n.bbox(g),
        "fill":fill,"shadow":shadow,
        "marks":["stroke" if x=="stroke" else "U+%04X"%ord(x) for x in marks],
    }
