# Gaia Master — Font Isolation 0.6.3.10 HEIGHT FROM STACK METADATA

Prepared: **2026-09-12**
Status: **BUILT / awaiting runtime result**

## Why 0.6.3.9 failed

0.6.3.9 assumed `s3` at `0x8003CCC0` still pointed to the glyph metadata struct and used:

```text
lhu v0,2(s3)
```

Runtime produced vertical `TEST` layout and texture garbage.

Full caller reverse later proved:

```text
s5 = current 16-byte output/cache record base
s3 = s5 + 15
```

Therefore `s3+2` is outside the current record and is not metadata height.

## Proven metadata lifetime

Caller flow:

```text
0x8003CAC0  a2 = sp+16
0x8003C210  builds current glyph metadata into sp+16
```

Later in the same caller frame:

```text
0x8003CC3C  a1 = sp+16
0x8003C67C  copy/unpack routine
```

The copy routine reads:

```text
lhu 2(a1)
```

as `height_minus_1` for the source-row loop.

So at the sprite-geometry stage the dataflow-proven current glyph height is:

```text
lhu v0,18(sp)
```

because:

```text
sp+16 = metadata base
+2    = height_minus_1
```

## 0.6.3.10 design

Start from 0.6.3.7 SOURCE ROW SENTINEL.

Replace the native load at `0x8003CCC0` with a jump to a tiny cave that executes:

```text
lhu v0,18(sp)
j 0x8003CCC8
nop
```

Then native:

```text
0x8003CCC8 addiu v0,v0,1
```

produces:

```text
native metadata 11 -> visible dimension 12
target metadata 15 -> visible dimension 16
```

No late `s0` target check is needed.

## Source sentinel remains

Target source rows:

```text
rows10..11 = dark/gray full band
rows12..15 = bright white full band
```

## Runtime question

Does normal TEST/native layout remain horizontal and stable while the target finally shows the full thick 4-row bright lower block?

### If yes

The remaining blocker was the late-stage dimension source. The renderer can use current glyph metadata safely when read from the proven stack buffer.

### If no but layout is stable

The lower rows are already lost before final sprite geometry. Continue reverse into converted-cache / VRAM contents.

## Safety

0.6.3.10 does not use:

- global height force;
- persistent/global flag;
- post-copy sentinel hook;
- late `s0` target identity;
- UV diagnostic;
- shared `0x8003CD94..0x8003CDB4` allocator rewrite.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.10_HEIGHT_FROM_STACK_METADATA.zip
```

Launcher:

```text
00_RUN_PROBE_06310.cmd
```
