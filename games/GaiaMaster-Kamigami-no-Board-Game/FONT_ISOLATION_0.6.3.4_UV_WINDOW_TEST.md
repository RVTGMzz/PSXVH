# Gaia Master — Font Isolation 0.6.3.4 UV WINDOW TEST

## Why this probe exists

0.6.3.3 placed the extended target glyph at end-of-line so no following glyph could overwrite it.

Runtime result was essentially unchanged from 0.6.3.2: lower target rows still missing.

Therefore:

> following-glyph overwrite is disproven.

The unresolved loss is inside the target's own copy/upload/window/display path.

## New reverse finding

VRAM upload queue is built around:

```text
0x8003CDE8..0x8003CE24
```

and queued by:

```text
0x800406F8
```

RECT:

```text
x = state+48
y = state+40
w = 4
h = state+42 - state+40 + 1
```

RAM source pointer:

```text
state+96
```

Wide converted glyph geometry remains:

```text
6 source bytes/row -> 8 cache bytes/row
16 rows -> 128 converted bytes
```

## 0.6.3.4 design

Start from stable 0.6.3.3:

```text
ＴＥＳＴ亜
```

Keep:

- 16-row metadata/copy path;
- visible sprite height 16;
- baseline Y -4;
- target at EOL;
- native shared cache allocator/stride untouched.

Change only:

```text
target texture V += 4
```

Hook:

```text
0x8003CCF0
```

Native `subu v0,v0,v1` at `0x8003CCF4` runs in the jump delay slot. The cave then conditionally adds 4 for `0x889F`, stores texture V to descriptor byte `-10(s3)`, and resumes at `0x8003CCFC`.

## Interpretation

### If lower E rows appear

The final rows exist in VRAM. The bug is texture-window / UV / draw sampling.

Expected side effect: top accents move upward/out of the sampled window or disappear because sampling starts 4 rows lower.

### If lower E rows remain missing / blank / garbage

The last rows are already absent before texture sampling. Continue reverse in converted-cache or VRAM-upload content/rectangle, not sprite windowing.

## Safety

0.6.3.4 does **not** patch the unsafe shared cache advance block:

```text
0x8003CD94..0x8003CDB4
```

Stop immediately if unrelated Japanese corrupts or the game freezes.
