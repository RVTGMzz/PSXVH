# Gaia Master — Character Select custom glyph cache/font atlas reverse 0.1

## Mục tiêu

Probe visible chuyển sang full-width control để đi đúng renderer Nhật:

```text
ＴＥＳＴ亜
```

Mục tiêu cuối:

```text
ＴＥＳＴẾ
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

Relevant instructions:

```text
0x8003C4DC sll  v0,v0,1
0x8003C4E0 lw   v1,0x51C(gp)   # mapping base pointer
0x8003C4E4 lw   a0,0x518(gp)   # atlas base pointer
0x8003C4E8 addu v0,v0,v1
0x8003C4EC lhu  v1,0(v0)       # glyph index
0x8003C4F8 sll  v0,v1,3
0x8003C4FC addu v0,v0,v1
0x8003C500 sll  a1,v0,3        # glyph_index * 72
0x8003C504 addu a0,a0,a1       # final glyph pointer
```

Default font pointers are initialized by function at `0x8003DD48`:

```text
atlas ptr   = 0x8006BCEC
mapping ptr = 0x8007AECC
```

Corresponding SLPS static sources:

```text
atlas:   SLPS + 0x5C4EC
mapping: SLPS + 0x6B6CC
```

The `gp+0x518` / `gp+0x51C` pointer variables themselves start zero and are initialized at runtime, but the default mapping table is static in the executable.

Examples from the mapping table:

```text
0x8273 Ｔ -> glyph 481
0x8264 Ｅ -> glyph 466
0x8272 Ｓ -> glyph 480
0x889F 亜 -> glyph 0
```

## Atlas format — corrected final finding

Static atlas at `0x8006BCEC` is real font data:

```text
860 glyphs
72 bytes/glyph
12x12 pixels
4bpp
HIGH nibble first
```

Important correction: earlier reverse notes said `low nibble first`; that was wrong.

Direct rendering with **high nibble first** makes the mapped full-width Latin glyphs recognizable (`Ｔ`, `Ｅ`, `Ｓ`) and explains why the earlier custom glyph looked malformed.

Uppercase full-width `Ｅ` is glyph index 466 and is used as the native style/color reference.

## Font Isolation 0.6.2.7 — custom atlas runtime PASS

0.6.2.7 replaced atlas glyph index 0 and used an ASCII `TEST亜` control string.

Runtime user result:

```text
É É É É É
```

What this actually established:

- custom atlas bitmap injection renders at runtime;
- one-byte ASCII is not a valid control path for this Japanese renderer;
- replacing glyph index 0 globally is not a viable final strategy.

The dark/mismatched glyph style was also partly caused by using a synthetic bitmap rather than preserving the game's own native glyph body.

## 0.6.2.10 — early hook rejected

Hooking at `0x8003C4DC` disturbed the mapping pipeline and caused many/all visible text glyphs to collapse into the same repeated character.

This strategy is rejected.

## 0.6.2.11 — post-lookup hook breakthrough

Hook moved to:

```text
VA:          0x8003C504
SLPS offset: 0x2CD04
```

This is after mapping-table lookup and after glyph-index -> byte-offset calculation.

The jump delay slot executes the original:

```text
addu a0,a0,a1
```

so normal characters keep the exact original final glyph pointer.

Only `low16(s0) == 0x889F` overrides `a0` with the custom glyph pointer.

Control text uses correct full-width CP932:

```text
ＴＥＳＴ亜
82 73 82 64 82 72 82 73 88 9F
```

Runtime user result:

```text
ＴＥＳＴ?
```

This is a strong renderer-hook PASS:

- four control glyphs remain normal;
- only the target final character changes;
- therefore the post-lookup hook successfully isolates `0x889F` without corrupting global text.

The remaining `?`-like custom glyph is now explained by the reversed 4bpp nibble packing.

## 0.6.2.12 — current probe

Keep the proven 0.6.2.11 post-lookup hook and fix only the bitmap packing.

Custom glyph build rules:

- read the game's own full-width `Ｅ` glyph (index 466);
- decode/encode 12x12 4bpp **HIGH nibble first**;
- preserve body rows 2..11 literally byte-for-byte;
- write circumflex + acute only into the two blank top rows;
- use palette indices already present in the native E glyph.

Expected runtime:

```text
ＴＥＳＴẾ
```

Other text must remain normal, and the E body should inherit the game's native brightness/shadow style.

## Road to complete ROM

After `ＴＥＳＴẾ` passes:

1. build complete Vietnamese glyph inventory and assign compact runtime codes;
2. generalize the post-lookup hook into a Vietnamese custom-code lookup without disturbing untouched Japanese;
3. integrate `vi_full` instead of no-accent fallback;
4. solve/repack the 230 currently pending rows that overflow fixed 2-byte full-width slots;
5. clean mixed Japanese/Vietnamese intro fragments;
6. patch graphic-text menus (`Story Mode`, `VS`, `Weapon Skill List`, `Options`, `Character Select` candidates);
7. full runtime QA across menus/story/gameplay/save-load;
8. final reproducible patch/build package.

Current blocker is no longer whether custom Vietnamese glyphs can render. The remaining immediate task is correct atlas packing/style, with renderer isolation already proven by 0.6.2.11.
