# Gaia Master — Font Isolation 0.6.3.1 BASELINE + 16-ROW STRIDE — UNSAFE FAIL

Runtime test date: **2026-09-12**

## Runtime result

0.6.3.1 is an **unsafe regression**.

User screenshots show:

- unrelated Japanese text corrupted/repeated;
- Character Select header corrupted;
- probe line showing repeated/misplaced `Ａ/Ｅ`-like glyphs instead of an isolated target;
- later screen garbled;
- game freeze at that later screen.

Do **not** retest 0.6.3.1.

## What changed from structurally-safe 0.6.3.0

0.6.3.1 added:

1. target baseline Y `-4 px` near `0x8003CD08`;
2. target-specific rewrite of shared cache RAM/VRAM advance near `0x8003CD94`.

The second change is the strongest regression suspect.

## Native shared cache-advance block

```text
0x8003CD94  lw    v0,100(s1)
0x8003CD98  sll   v1,v1,3
0x8003CD9C  addu  v0,v0,v1
0x8003CDA4  sw    v0,100(s1)
0x8003CDA8  lhu   v0,50(s1)
0x8003CDAC  addiu v1,v1,1
0x8003CDB0  addu  v0,v0,v1
0x8003CDB4  sh    v0,50(s1)
```

This mutates shared converted-font-cache pointer state and VRAM row cursor. A target-specific 16-row replacement here can desynchronize every following glyph, which matches the runtime corruption/freeze pattern.

## Next diagnostic

Use **0.6.3.2 BASELINE ONLY**:

- keep 0.6.3.0 16-row source/copy/sprite path;
- apply only target `Y -= 4`;
- do not patch `0x8003CD94..0x8003CDB4`;
- append full-width `Ａ` sentinel after target.

Control:

```text
ＴＥＳＴ亜Ａ
```

Goal:

```text
ＴＥＳＴẾＡ
```

This isolates whether the shared cache-advance rewrite caused the 0.6.3.1 regression.
