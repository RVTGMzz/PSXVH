# Gaia Master — Font Isolation 0.6.3.9 HEIGHT FROM METADATA — DIAGNOSTIC FAIL

Runtime test date: **2026-09-12**

## Purpose

0.6.3.9 attempted to avoid both late `s0` target checks and global force-height16 by reading an assumed per-glyph height directly at the late sprite/layout stage:

```text
0x8003CCC0: lhu v0,2(s3)
0x8003CCC8: addiu v0,v0,1
```

Assumption:

```text
s3 still points to the current glyph metadata struct
metadata +2 = height_minus_1
native = 11
extended target = 15
```

## Runtime result

FAIL.

Observed screenshot:

- `TEST` is stacked vertically rather than laid out horizontally;
- target becomes a noisy/garbled texture block;
- layout is disturbed similarly to the 0.6.3.8 global-height experiment;
- the expected thick bright source-sentinel rows12..15 are not recovered.

## Conclusion

The assumption is invalid:

> `s3` at `0x8003CCC0` must not be treated as the original glyph metadata pointer without a real register-lifetime/dataflow proof.

Likewise, the block around `0x8003CCC0` cannot yet be described as a simple visible sprite-height control.

The vertical TEST behavior strongly suggests this value participates in broader layout/primitive/cache geometry, not merely a target texture window height.

## Next action

Do **not** build 0.6.3.10 immediately.

Reverse only:

```text
0x8003CCA0 .. 0x8003CD20
```

Required proof before another runtime probe:

1. register lifetime and meaning of `s1/s2/s3`;
2. actual semantic meaning of `lbu 64(s1)` at `0x8003CCC0`;
3. all stores/consumers of the post-`+1` value;
4. exact descriptor/primitive field controlling vertical texture sampling;
5. distinction between draw height, glyph advance, line metric and cache/tile dimension.

## Do not repeat

- do not retest 0.6.3.9;
- do not use `s3+2` at `0x8003CCC0` as per-glyph height without proof;
- do not globally force height16;
- do not reintroduce persistent/global target flags;
- do not modify shared `0x8003CD94..0x8003CDB4` allocator/cursor state.
