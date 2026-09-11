# Gaia Master — Character Select custom glyph cache/font atlas reverse 0.1

## Mục tiêu

Probe visible:

```text
TEST亜
```

Mục tiêu cuối:

```text
TESTẾ
```

Không quay lại hook `Krom2RawAdd`: direct caller #1, direct caller #2 và global safe wrapper đều đã không chạm glyph Character Select.

## Source-of-truth

- clean BIN SHA1: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- `SLPS_020.75` SHA1: `1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5`
- `PRGPACK.BDP` SHA1: `a9b195b8ae5d8cad7f4f755daa08337d4671632c`
- Character Select text: `PRGPACK + 0xBFD2C`
- owner nested BDP: entry 29
- local offset in entry29: `+0x580`

## Stage 2 breakthrough — custom atlas path found

Renderer function around `0x8003C210` has two glyph sources.

For one state/size it still calls BIOS/Krom at:

```text
0x8003C4A0 -> 0x80068208
```

Character Select uses the alternate branch around:

```text
0x8003C4DC
```

Relevant logic:

```text
v0 = s0 & 0x7FFF
v0 *= 2
mapping = *(gp + 0x51C)
atlas   = *(gp + 0x518)
glyph_index = mapping[v0]
glyph_ptr = atlas + glyph_index * 72
```

Default font pointers are initialized by function at `0x8003DD48`:

```text
atlas ptr   = 0x8006BCEC
mapping ptr = 0x8007AECC
```

Corresponding SLPS locations:

```text
atlas static source: SLPS + 0x5C4EC
runtime mapping RAM: 0x8007AECC
```

The mapping region is zero-filled in the executable and therefore is populated dynamically at runtime. This explains why patching it statically is not valid.

## Atlas format confirmed

Static atlas at `0x8006BCEC` is real font data:

```text
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
low nibble first
```

Rendering the atlas directly confirms Japanese glyphs and Latin glyphs. Uppercase Latin `E` is glyph index 466 and provides the correct brightness/shadow style reference.

## Font Isolation 0.6.2.7 — result

Diagnostic 0.6.2.7 replaced static atlas glyph index 0 with a custom accented E-like glyph while leaving Character Select text as `TEST亜`.

Runtime user result:

```text
É É É É É
```

This is an important PASS for custom atlas injection: the game rendered the injected bitmap. However it also proved that replacing glyph index 0 globally is not a valid final strategy.

The repeated glyph is consistent with runtime mapping behavior/fallbacks: multiple probe characters reached glyph index 0 in that diagnostic context. The custom glyph color was darker because the diagnostic bitmap used too much intensity value 7 instead of preserving the game's native fill/shadow distribution.

Therefore 0.6.2.7 is considered:

```text
CUSTOM ATLAS RUNTIME PASS
MAPPING STRATEGY FAIL
```

## 0.6.2.8 TARGETED HOOK

Next probe no longer overwrites atlas glyph index 0.

Hook exactly the custom-atlas renderer branch:

```text
hook site VA:   0x8003C4DC
SLPS offset:    0x2CCDC
safe cave VA:   0x8006B8E0
safe cave file: 0x5C0E0
```

The original instruction at `0x8003C4DC` is:

```text
sll v0,v0,1
```

0.6.2.8 replaces it with a jump to the already runtime-validated safe cave. The original `0x8003C4E0` instruction executes in the jump delay slot.

The cave checks only:

```text
(s0 & 0x7FFF) == 0x089F
```

which corresponds to Shift-JIS `0x889F = 亜`.

For all other codes it executes the displaced original instruction and returns to the original mapping path.

For `0x889F` only, it bypasses the dynamic mapping table and points directly to one custom glyph stored inside the safe cave.

Custom glyph location:

```text
VA:          0x8006BA00
SLPS offset: 0x5C200
size:        72 bytes
format:      12x12 4bpp
```

The `Ế` diagnostic glyph is derived from the game's native uppercase E glyph style so its fill/shadow intensity should be much closer to normal UI text than 0.6.2.7.

Expected runtime:

```text
TESTẾ
```

If this passes, the next engineering step is to generalize the targeted hook into a compact Vietnamese codepage/custom atlas without disturbing untouched Japanese text.

## Road to complete ROM

After `TESTẾ` passes:

1. build full Vietnamese glyph set/codepage;
2. integrate `vi_full` instead of no-accent fallback;
3. solve/repack the 230 currently pending rows that overflow fixed 2-byte full-width slots;
4. clean mixed Japanese/Vietnamese intro fragments;
5. patch graphic-text menus (`Story Mode`, `VS`, `Weapon Skill List`, `Options`, `Character Select` candidates);
6. full runtime QA across menus/story/gameplay/save-load;
7. final reproducible patch/build package.

Current technical blocker risk is substantially lower than before Stage 2 because custom atlas rendering is now proven at runtime.
