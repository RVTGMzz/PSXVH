#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, string
from pathlib import Path
import gaia_nf1_new_font_art as v01

UPPER_VI = "ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ"
LOWER_VI = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
FULL_VI_NONASCII = list(UPPER_VI + LOWER_VI)

PUNCT = {
'!':["..#..","..#..","..#..","..#..","..#..",".....","..#.."],
'"':[".#.#.",".#.#.",".....",".....",".....",".....","....."],
'#':[".#.#.",".#.#.","#####",".#.#.","#####",".#.#.",".#.#."],
'$':["..#..",".####","#.#..",".###.","..#.#","####.","..#.."],
'%':["##..#","##.#.","...#.","..#..",".#...","#.##.","#..##"],
'&':[".##..","#..#.","#.#..",".##..","#.#.#","#..#.",".##.#"],
"'":["..#..","..#..",".#...",".....",".....",".....","....."],
'(':["...#.","..#..",".#...",".#...",".#...","..#..","...#."],
')':[".#...","..#..","...#.","...#.","...#.","..#..",".#..."],
'*':[".....","#.#.#",".###.","#####",".###.","#.#.#","....."],
'+':[".....","..#..","..#..","#####","..#..","..#..","....."],
',':[".....",".....",".....",".....",".....","..#..",".#..."],
'-':[".....",".....",".....","#####",".....",".....","....."],
'.':[".....",".....",".....",".....",".....",".....","..#.."],
'/':["....#","...#.","...#.","..#..",".#...",".#...","#...."],
':':[".....","..#..",".....",".....","..#..",".....","....."],
';':[".....","..#..",".....",".....","..#..",".#...","....."],
'<':["...#.","..#..",".#...","#....",".#...","..#..","...#."],
'=':[".....",".....","#####",".....","#####",".....","....."],
'>':[".#...","..#..","...#.","....#","...#.","..#..",".#..."],
'?':[".###.","#...#","....#","...#.","..#..",".....","..#.."],
'@':[".###.","#...#","#.###","#.#.#","#.###","#....",".####"],
'[':[".###.",".#...",".#...",".#...",".#...",".#...",".###."],
'\\':["#....",".#...",".#...","..#..","...#.","...#.","....#"],
']':[".###.","...#.","...#.","...#.","...#.","...#.",".###."],
'^':["..#..",".#.#.","#...#",".....",".....",".....","....."],
'_':[".....",".....",".....",".....",".....",".....","#####"],
'{':["...#.","..#..","..#..",".#...","..#..","..#..","...#."],
'|':["..#..","..#..","..#..","..#..","..#..","..#..","..#.."],
'}':[".#...","..#..","..#..","...#.","..#..","..#..",".#..."],
'~':[".....",".....",".##..","#..##",".....",".....","....."],
}
PUNCT[chr(96)] = [".#...","..#..",".....",".....",".....",".....","....."]

ASCII_PRINTABLE = [chr(i) for i in range(0x20,0x7F)]

def render(ch):
    if ch == ' ': return [[0]*12 for _ in range(12)]
    if ch in v01.P or ch in FULL_VI_NONASCII:
        return v01.render_char(ch)
    if ch in PUNCT:
        g=[[0]*12 for _ in range(12)]
        for yy,row in enumerate(PUNCT[ch]):
            for xx,c in enumerate(row):
                if c!='.':
                    g[v01.BODY_Y+yy][v01.BODY_X+xx]=1
        return g
    raise KeyError(ch)

def encode_4bpp(g,fill=1):
    out=bytearray()
    for row in g:
        for x in range(0,12,2):
            a=fill if row[x] else 0
            b=fill if row[x+1] else 0
            out.append((a&15)|((b&15)<<4))
    assert len(out)==72
    return bytes(out)

def svg(chars,out,scale=7,cols=12):
    out.parent.mkdir(parents=True,exist_ok=True)
    cellw=12*scale+24
    cellh=12*scale+34
    rows=(len(chars)+cols-1)//cols
    W=cellw*cols
    H=cellh*rows
    q=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<rect width="100%" height="100%" fill="white"/>']
    for i,ch in enumerate(chars):
        ox=(i%cols)*cellw+12
        oy=(i//cols)*cellh+8
        g=render(ch)
        q.append(f'<rect x="{ox}" y="{oy}" width="{12*scale}" height="{12*scale}" fill="#f7f7f7" stroke="#ddd"/>')
        for y,row in enumerate(g):
            for x,v in enumerate(row):
                if v:
                    q.append(f'<rect x="{ox+x*scale}" y="{oy+y*scale}" width="{scale}" height="{scale}" fill="#111"/>')
        label=('SPACE' if ch==' ' else ch)+f' U+{ord(ch):04X}'
        q.append(f'<text x="{ox}" y="{oy+12*scale+18}" font-family="monospace" font-size="12">{html.escape(label)}</text>')
    q.append('</svg>')
    out.write_text('\n'.join(q)+'\n',encoding='utf-8')

def selftest():
    assert len(UPPER_VI)==67, len(UPPER_VI)
    assert len(LOWER_VI)==67, len(LOWER_VI)
    assert len(FULL_VI_NONASCII)==134
    assert len(set(FULL_VI_NONASCII))==134
    assert len(ASCII_PRINTABLE)==95
    assert set(string.punctuation).issubset(PUNCT.keys())
    chars=ASCII_PRINTABLE+FULL_VI_NONASCII
    for ch in chars:
        g=render(ch)
        assert len(g)==12 and all(len(r)==12 for r in g)
        assert len(encode_4bpp(g))==72
    print('NF1 V0.2 FULL CHARSET SELFTEST PASS')
    print('ascii_printable=95')
    print('vietnamese_nonascii=134')
    print('total_source_glyphs=229')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--selftest',action='store_true')
    ap.add_argument('--svg',type=Path)
    a=ap.parse_args()
    if a.selftest:
        selftest()
    if a.svg:
        svg(ASCII_PRINTABLE+FULL_VI_NONASCII,a.svg)
        print('SVG:',a.svg)
    if not a.selftest and not a.svg:
        ap.print_help()

if __name__=='__main__':
    main()
