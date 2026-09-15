#!/usr/bin/env python3
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import build_gaia_b51_guarded_exact_overlay as core
import build_gaia_b51r1_guarded_exact_overlay as r1

clean = Path(sys.argv[1])
sha1, slps, prg, cmap = core.read_clean(clean)
core.restore_b50()
rows = r1.load_b50_r1(cmap)

bad = []
for p in rows:
    blob = prg if p.file == "PRGPACK.BDP" else slps
    want = p.japanese.encode("cp932")
    got = bytes(blob[p.offset:p.end])
    if got != want:
        bad.append((p, blob, want, got))

print("=" * 72)
print("B51R1 CLEAN SOURCE MISMATCH DIAGNOSTIC")
print("=" * 72)
print("CLEAN SHA1:", sha1)
print("rows checked:", len(rows))
print("exact rows:", len(rows) - len(bad))
print("mismatch rows:", len(bad))
print("BIN modified: NO")
print("Font modified: NO")
print("Runtime PASS: NO")
print()

for n, (p, blob, want, got) in enumerate(bad, 1):
    print(f"[{n}] {p.file}+0x{p.offset:X} field={p.field}")
    print(" expected:", repr(p.japanese))
    print(" expected hex:", want.hex(" "))
    print(" actual hex  :", got.hex(" "))
    print(" actual text :", repr(got.decode("cp932", errors="replace")))
    hits = []
    pos = blob.find(want)
    while pos >= 0 and len(hits) < 8:
        hits.append(pos)
        pos = blob.find(want, pos + 1)
    if hits:
        hits.sort(key=lambda x: abs(x - p.offset))
        print(" exact hits  :", ", ".join(f"0x{x:X} delta={x-p.offset:+#x}" for x in hits[:8]))
    else:
        print(" exact hits  : NONE")
    print()

if bad:
    print("RESULT: FAIL - keep build blocked; fix source-layer identity first.")
    raise SystemExit(9)
print("RESULT: PASS 1229/1229")
