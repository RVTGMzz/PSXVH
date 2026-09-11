# Gaia Master — Font Isolation 0.6.2.9 FULLWIDTH CONTROL

## Runtime result leading into this test

0.6.2.7 and 0.6.2.8 showed the injected accented E glyph repeated for every control character instead of preserving `TEST` and changing only `亜`.

The important correction is that the probe text had accidentally regressed to one-byte ASCII (`54 45 53 54`). This project had already established that one-byte ASCII does not follow the valid Japanese renderer path, while full-width CP932 Latin does.

## 0.6.2.9 correction

Use full-width CP932 control text:

```text
ＴＥＳＴ亜
```

Bytes:

```text
82 73 82 64 82 72 82 73 88 9F
```

The targeted custom-atlas hook now compares the original renderer input register directly:

```text
s0 == 0x889F
```

Only `亜` should be intercepted. The four full-width Latin letters must follow the original renderer path.

## Expected runtime

```text
ＴＥＳＴẾ
```

Visually, only the final glyph should change to the injected Vietnamese E-circumflex-acute test glyph.

## Current reverse facts retained

- Character Select text: `PRGPACK.BDP + 0xBFD2C`
- owner nested BDP: entry 29
- custom atlas renderer branch: around `0x8003C4DC`
- atlas glyph format: 12x12, 4bpp, 72 bytes/glyph
- injected code target: Shift-JIS `0x889F = 亜`
- safe cave: `SLPS + 0x5C0E0`, VA `0x8006B8E0`

If 0.6.2.9 passes, the next step is to stop single-glyph probing and expand to a Vietnamese runtime glyph/codepage layer, then migrate `vi_full` and address the remaining overflow/graphics/QA work.
