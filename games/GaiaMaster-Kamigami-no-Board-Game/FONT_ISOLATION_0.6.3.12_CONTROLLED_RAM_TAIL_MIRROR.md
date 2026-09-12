# Gaia Master — 0.6.3.12 CONTROLLED RAM TAIL MIRROR

Purpose: resolve the ambiguity left by 0.6.3.11 with one screenshot.

## Proven target identity

Use current glyph metadata height already proven by caller dataflow:

```text
lhu 18(sp) == 15
```

No late `s0`, no persistent flag, no source-pointer identity assumption.

## Hook point

Post-copy hook:

```text
0x8003CC4C
```

Before native allocator advance:

```text
dest = *(s1+100)
```

## Two visual signals

### CONTROL

Write converted rows6..7 as full `0x77` dark/gray bands.

These rows are inside the already-visible region and prove the hook/destination path is operating on the displayed target.

### MIRROR

Copy:

```text
converted rows12..15 dest+96..127
-> rows8..11 dest+64..95
```

The source glyph already contains full `0x11` bright rows12..15.

## Interpretation

A. Dark control + bright mirror:

> converted rows12..15 exist immediately after copy. Continue downstream to cache/VRAM placement.

B. Dark control but no bright mirror:

> hook/destination path is correct, but converted rows12..15 do not contain the expected tail immediately after `0x8003C67C`. Reverse copy loop/state/source-to-destination writes next.

C. No dark control:

> post-copy hook/destination model is still wrong. Do not infer tail loss.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.12_CONTROLLED_RAM_TAIL_MIRROR.zip
```

Launcher:

```text
00_RUN_PROBE_06312.cmd
```
