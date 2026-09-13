# Gaia Master — 0.6.5.3 MAPPING-ONLY NATIVE-CELL PROOF

## Gate opened by scanner 0.2

`GaiaMaster_FontMappingInitializerScanner_02.txt` proved:

- runtime GP = `0x80085F28`;
- `gp+0x518` = atlas pointer slot;
- `gp+0x51C` = mapping pointer slot;
- initializer at `0x8003DD48..0x8003DD5C` writes:
  - atlas `0x8006BCEC`;
  - mapping `0x8007AECC`;
- setter at `0x8003DD68..0x8003DD6C` can replace those two pointers;
- static mapping data at `SLPS+0x6B6CC` matches all known runtime samples:
  - `0x8273 -> 481`;
  - `0x8264 -> 466`;
  - `0x8272 -> 480`;
  - `0x889F -> 0`.

Therefore mapping ownership is considered demonstrated and the read-only gate is open.

## Proof design

Version: `0.6.5.3 MAPPING-ONLY NATIVE-CELL PROOF`

Hard constraints:

- no code hook;
- no runtime pointer redirect;
- no 12x16;
- no composite overlay;
- native `12x12 / 72-byte / 4bpp / LOW nibble first` only.

Target chain:

```text
0x889F..0x88AA
  -> patched static mapping entries
  -> 12 selected atlas slots
  -> 12 native 72-byte glyph cells
```

Character Select test location remains:

```text
PRGPACK.BDP + 0xBFD2C
owner nested BDP = entry 29
```

Expected visual order:

```text
A Â Ấ Ẳ E Ê Ế Ể O Ô Ố Ỗ
```

## Slot safety

Builder does not blindly reuse atlas slots 0..11.

It reconstructs the renderer's valid mapping-code ranges from the static reverse, builds the current slot->code ownership set, scans static SLPS/PRGPACK data for mapped code usage, protects known reference slots `0, 466, 480, 481`, then chooses 12 slots with the lowest static-text usage score.

The exact selected slots are written into the generated build report so a runtime result can be traced deterministically.

## Tool

```text
tools/build_gaia_0653_mapping_only.py
tools/00_BUILD_0.6.5.3_MAPPING_ONLY.cmd
```

The builder only accepts the CLEAN BIN SHA1:

```text
f4d5298583c90d89c4b7e51d2dde160ee07f2aec
```

It regenerates BDP checksums plus changed Mode2/Form1 sector EDC/ECC.

## Runtime interpretation

- exact 12-glyph sequence visible: mapping-only architecture PASS;
- stable but wrong/repeated glyphs: inspect generated slot/mapping report before any new patch;
- black screen / FPS 0 / global corruption: stop immediately and mark unsafe.

Do not reuse the rejected 0.6.5.2 runtime redirect design.
