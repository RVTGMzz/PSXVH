# Gaia Master — Font Narrow Bank Scanner 0.1

## Why this scanner exists

`FontPrivateBankScanner 0.1` closed the first spacing-data gate:

- best private 12x12 bank = slots `432..440`;
- all 9 slots are unmapped and have zero static text hits;
- >=9 zero-hit CP932 codes exist;
- but the only large zero/NOP run was `SLPS+0x5C0E0..<0x5C2B8` with 4 direct control refs.

Manual reverse then exposed a better path.

## Important cave rejection

Renderer 1-byte narrow source base is:

```text
RAM  0x8006BAAC
SLPS 0x5C2AC
```

The old zero-run candidate ends at `SLPS+0x5C2B8`, so its final **12 bytes overlap the native narrow font resource**.

Therefore:

> `0x5C0E0..<0x5C2B8` is rejected as a code cave. Do not inject code there.

## Native narrow-bank finding

Gaia already has a separate 1-byte narrow-glyph source path.

Key reverse facts:

```text
halfwidth remap table RAM = 0x8007E01C
narrow source base RAM    = 0x8006BAAC
main 12x12 atlas RAM      = 0x8006BCEC
```

For the Character Select 12-pixel class:

```text
state dimension = 11
state+0x3E      = 8
```

The one-byte path computes a narrow metadata width before glyph copy. Its native copy returns `8`, which makes cache miss choose the existing `state+0x3E = 8` horizontal advance.

No `record+6` override is needed if we can stay entirely on this native path.

## Packed source geometry

For dimension 11:

```text
rows = 12
source bytes per narrow glyph row = 3
packed pair row = 3 bytes glyph A + 3 bytes glyph B
pair block = 12 * 6 = 72 bytes
```

The region from `0x8006BAAC` to main atlas `0x8006BCEC` is exactly 576 bytes, matching 8 packed pairs / 15 usable narrow source indices.

Source address for resolved narrow index `i`:

```text
source = 0x8006BAAC
       + 3 * ((i & ~1) * 12)
       + 3 * (i & 1)
```

The narrow copy reads 3 source bytes per row with a 6-byte source stride, so the two glyph halves in a pair remain independently replaceable.

## Scanner goal

`tools/font_narrow_bank_scanner_0.1.py` is READ-ONLY and accepts only the clean BIN.

It:

1. decodes ASCII `0x21..0x7F` aliases;
2. decodes halfwidth table aliases `0xA0..0xDD`;
3. resolves aliases to native narrow source indices `0..14`;
4. aggregates aliases by **actual source index** to detect source sharing;
5. scans strict null-terminated text-like segments in PRGPACK and SLPS;
6. rejects halfwidth entries whose `0x2000` flag makes their resolved index state-dependent;
7. identifies distinct source indices with zero strict-text alias hits and at least one valid halfwidth code candidate;
8. reports whether at least 9 such sources exist for:

```text
C h ọ n SPACE t ư ớ g
```

## If scanner PASSes

Do not boot immediately.

Next gate:

1. cross-check the 9 selected halfwidth aliases/source indices against Translation Master / known Japanese strings;
2. design a compact ~6px-wide Vietnamese glyph style inside the native packed source bank;
3. build exactly one **data-only** Character Select proof.

Desired pipeline:

```text
Vietnamese private 1-byte code
 -> existing halfwidth remap table
 -> selected native narrow source index
 -> native narrow copy
 -> copy_return = 8
 -> native cached advance = 8px
```

No code cave, no cursor hook, no cached-advance hook, no pointer redirect.

## If scanner is negative

- no emulator test;
- keep `0.6.6.1` as runtime baseline;
- return to offline isolated cache-advance reverse work.

## Hard rules

- no production 12x16;
- no `0.6.5.2` pointer redirect;
- no composite overlay;
- no global spacing/cursor mutation;
- never use the rejected zero-run `0x5C0E0..<0x5C2B8` as a cave.
