#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, string, unicodedata
from pathlib import Path

CUSTOM_CHARS = list("àáâãéêìíòóÔôùúÝăĐđĩũƠơưạảấầẩẫậắặẻẽếềểệỉịọỏốồổỗộớờởợụủứừửữựỵỹ")

P = {
'A':[".###.","#...#","#...#","#####","#...#","#...#","#...#"],
'B':["####.","#...#","#...#","####.","#...#","#...#","####."],
'C':[".###.","#...#","#....","#....","#....","#...#",".###."],
'D':["####.","#...#","#...#","#...#","#...#","#...#","####."],
'E':["#####","#....","#....","####.","#....","#....","#####"],
'F':["#####","#....","#....","####.","#....","#....","#...."],
'G':[".###.","#...#","#....","#.###","#...#","#...#",".###."],
'H':["#...#","#...#","#...#","#####","#...#","#...#","#...#"],
'I':["#####","..#..","..#..","..#..","..#..","..#..","#####"],
'J':["..###","...#.","...#.","...#.","#..#.","#..#.",".##.."],
'K':["#...#","#..#.","#.#..","##...","#.#..","#..#.","#...#"],
'L':["#....","#....","#....","#....","#....","#....","#####"],
'M':["#...#","##.##","#.#.#","#.#.#","#...#","#...#","#...#"],
'N':["#...#","##..#","#.#.#","#..##","#...#","#...#","#...#"],
'O':[".###.","#...#","#...#","#...#","#...#","#...#",".###."],
'P':["####.","#...#","#...#","####.","#....","#....","#...."],
'Q':[".###.","#...#","#...#","#...#","#.#.#","#..#.",".##.#"],
'R':["####.","#...#","#...#","####.","#.#..","#..#.","#...#"],
'S':[".####","#....","#....",".###.","....#","....#","####."],
'T':["#####","..#..","..#..","..#..","..#..","..#..","..#.."],
'U':["#...#","#...#","#...#","#...#","#...#","#...#",".###."],
'V':["#...#","#...#","#...#","#...#","#...#",".#.#.","..#.."],
'W':["#...#","#...#","#...#","#.#.#","#.#.#","##.##","#...#"],
'X':["#...#","#...#",".#.#.","..#..",".#.#.","#...#","#...#"],
'Y':["#...#","#...#",".#.#.","..#..","..#..","..#..","..#.."],
'Z':["#####","....#","...#.","..#..",".#...","#....","#####"],
'a':[".....",".....",".###.","....#",".####","#...#",".####"],
'b':["#....","#....","#.##.","##..#","#...#","#...#","####."],
'c':[".....",".....",".###.","#...#","#....","#...#",".###."],
'd':["....#","....#",".##.#","#..##","#...#","#...#",".####"],
'e':[".....",".....",".###.","#...#","#####","#....",".####"],
'f':["..##.",".#..#",".#...","###..",".#...",".#...",".#..."],
'g':[".....",".####","#...#","#...#",".####","....#",".###."],
'h':["#....","#....","#.##.","##..#","#...#","#...#","#...#"],
'i':["..#..",".....",".##..","..#..","..#..","..#..",".###."],
'j':["...#.",".....","..##.","...#.","...#.","#..#.",".##.."],
'k':["#....","#....","#..#.","#.#..","##...","#.#..","#..#."],
'l':[".##..","..#..","..#..","..#..","..#..","..#..",".###."],
'm':[".....",".....","##.#.","#.#.#","#.#.#","#...#","#...#"],
'n':[".....",".....","#.##.","##..#","#...#","#...#","#...#"],
'o':[".....",".....",".###.","#...#","#...#","#...#",".###."],
'p':[".....","####.","#...#","#...#","####.","#....","#...."],
'q':[".....",".####","#...#","#...#",".####","....#","....#"],
'r':[".....",".....","#.##.","##..#","#....","#....","#...."],
's':[".....",".....",".####","#....",".###.","....#","####."],
't':[".#...",".#...","###..",".#...",".#...",".#..#","..##."],
'u':[".....",".....","#...#","#...#","#...#","#..##",".##.#"],
'v':[".....",".....","#...#","#...#","#...#",".#.#.","..#.."],
'w':[".....",".....","#...#","#...#","#.#.#","#.#.#",".#.#."],
'x':[".....",".....","#...#",".#.#.","..#..",".#.#.","#...#"],
'y':[".....",".....","#...#","#...#",".####","....#",".###."],
'z':[".....",".....","#####","...#.","..#..",".#...","#####"],
'0':[".###.","#...#","#..##","#.#.#","##..#","#...#",".###."],
'1':["..#..",".##..","..#..","..#..","..#..","..#..",".###."],
'2':[".###.","#...#","....#","...#.","..#..",".#...","#####"],
'3':["####.","....#","....#",".###.","....#","....#","####."],
'4':["...#.","..##.",".#.#.","#..#.","#####","...#.","...#."],
'5':["#####","#....","#....","####.","....#","....#","####."],
'6':[".###.","#....","#....","####.","#...#","#...#",".###."],
'7':["#####","....#","...#.","..#..",".#...",".#...",".#..."],
'8':[".###.","#...#","#...#",".###.","#...#","#...#",".###."],
'9':[".###.","#...#","#...#",".####","....#","....#",".###."],
}

BODY_Y=4
BODY_X=3

def blank(): return [[0]*12 for _ in range(12)]
def setp(g,x,y):
    if 0<=x<12 and 0<=y<12:g[y][x]=1

def bbox(g):
    pts=[(x,y) for y,row in enumerate(g) for x,v in enumerate(row) if v]
    if not pts:return None
    return min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)

def draw_pattern(base):
    if base not in P: raise KeyError(base)
    g=blank()
    for yy,row in enumerate(P[base]):
        for xx,ch in enumerate(row):
            if ch!='.':setp(g,BODY_X+xx,BODY_Y+yy)
    return g

def decompose(ch):
    if ch=='Đ': return 'D',['stroke-upper']
    if ch=='đ': return 'd',['stroke-lower']
    d=unicodedata.normalize('NFD',ch)
    if not d:return ch,[]
    return d[0],list(d[1:])

def draw_tone(g,mark,cx,structural=False):
    if structural:
        if mark=='\u0301': pts=[(cx+3,0),(cx+2,1)]
        elif mark=='\u0300': pts=[(cx-3,0),(cx-2,1)]
        elif mark=='\u0309': pts=[(cx+2,0),(cx+3,0),(cx+3,1)]
        elif mark=='\u0303': pts=[(cx+1,0),(cx+2,1),(cx+3,0)]
        else:return
    else:
        if mark=='\u0301': pts=[(cx+1,1),(cx,2)]
        elif mark=='\u0300': pts=[(cx-1,1),(cx,2)]
        elif mark=='\u0309': pts=[(cx,1),(cx+1,1),(cx+1,2)]
        elif mark=='\u0303': pts=[(cx-2,2),(cx-1,1),(cx,2),(cx+1,2),(cx+2,1)]
        else:return
    for p in pts:setp(g,*p)

def render_char(ch):
    base,marks=decompose(ch)
    if base not in P: raise KeyError('No NF1 base pattern for %r -> %r'%(ch,base))
    g=draw_pattern(base)
    b=bbox(g); assert b
    x0,y0,x1,y1=b; cx=(x0+x1)//2
    structural=('\u0302' in marks or '\u0306' in marks)
    if '\u0302' in marks:
        for p in [(cx-1,3),(cx,2),(cx+1,3)]:setp(g,*p)
    if '\u0306' in marks:
        for p in [(cx-2,2),(cx-1,3),(cx,3),(cx+1,3),(cx+2,2)]:setp(g,*p)
    if '\u031B' in marks:
        for p in [(min(10,x1+1),y0+1),(min(10,x1+2),y0)]:setp(g,*p)
    if 'stroke-upper' in marks:
        yy=BODY_Y+3
        for x in range(BODY_X-1,BODY_X+4):setp(g,x,yy)
    if 'stroke-lower' in marks:
        yy=BODY_Y+1
        for x in range(BODY_X+2,BODY_X+6):setp(g,x,yy)
    for m in ('\u0301','\u0300','\u0309','\u0303'):
        if m in marks:draw_tone(g,m,cx,structural)
    if '\u0323' in marks:
        setp(g,cx,11)
    return g

def encode_4bpp(g,fill=1):
    out=bytearray()
    for row in g:
        for x in range(0,12,2):
            a=fill if row[x] else 0; b=fill if row[x+1] else 0
            out.append((a&15)|((b&15)<<4))
    assert len(out)==72
    return bytes(out)

def svg(chars,out,scale=7,cols=12):
    out.parent.mkdir(parents=True,exist_ok=True)
    cellw=12*scale+24; cellh=12*scale+34
    rows=(len(chars)+cols-1)//cols
    W=cellw*cols; H=cellh*rows
    q=['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'%(W,H,W,H),'<rect width="100%" height="100%" fill="white"/>']
    for i,ch in enumerate(chars):
        ox=(i%cols)*cellw+12; oy=(i//cols)*cellh+8
        g=render_char(ch)
        q.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#f7f7f7" stroke="#ddd"/>'%(ox,oy,12*scale,12*scale))
        for y,row in enumerate(g):
            for x,v in enumerate(row):
                if v:q.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#111"/>'%(ox+x*scale,oy+y*scale,scale,scale))
        label='%s  U+%04X'%(ch,ord(ch))
        q.append('<text x="%d" y="%d" font-family="monospace" font-size="12">%s</text>'%(ox,oy+12*scale+18,html.escape(label)))
    q.append('</svg>')
    out.write_text('\n'.join(q)+'\n',encoding='utf-8')

def selftest():
    need=list(string.ascii_letters+string.digits)+CUSTOM_CHARS
    for ch in need:
        g=render_char(ch)
        assert len(g)==12 and all(len(r)==12 for r in g)
        assert bbox(g) is not None
        assert len(encode_4bpp(g))==72
    assert render_char('A')!=render_char('Â')
    assert render_char('D')!=render_char('Đ')
    assert render_char('d')!=render_char('đ')
    assert render_char('o')!=render_char('ơ')
    print('NF1 NEW FONT ART SELFTEST PASS glyphs=%d'%len(need))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--selftest',action='store_true');ap.add_argument('--svg',type=Path);a=ap.parse_args()
    if a.selftest:selftest()
    if a.svg:
        chars=list(string.ascii_uppercase+string.ascii_lowercase+string.digits)+CUSTOM_CHARS
        svg(chars,a.svg);print('SVG:',a.svg)
    if not a.selftest and not a.svg:ap.print_help()

if __name__=='__main__':main()
