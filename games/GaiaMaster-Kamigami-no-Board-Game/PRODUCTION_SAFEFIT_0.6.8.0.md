# Gaia Master 0.6.8.0 — PROD60 SAFE-FIT vi_full BATCH 1

Status: **READY FOR RUNTIME TEST**

## Font baseline

`0.6.7.2` is frozen as the current visual source-of-truth:
- native 12x12 / 72-byte / 4bpp;
- static mapping-only;
- baseline normalization from 0.6.6.1;
- horn on `ơ/ư` hugs the body;
- acute/grave are separated from the horn;
- full-width spacing is accepted for now.

## Production codepage

Current `vi_full` needs exactly 60 custom Vietnamese glyphs. Frozen production slots use:
- 34 completely unmapped zero-hit atlas slots;
- 26 mapped-but-static-unused zero-hit slots;
- 4 zero-hit reserve slots remain untouched.

## Batch 1 policy

The builder loads Translation Master 0.6 parts 01..06 and applies a row only if:
1. `vi_full` is non-empty;
2. file is `PRGPACK.BDP` or `SLPS_020.75`;
3. Japanese source bytes match CLEAN data exactly;
4. source is followed by NUL;
5. no printf/control token is present (`%s`, `%d`, `%4d`, `%+3d`, `/V`, `/v`, etc.);
6. encoded Vietnamese byte length is no larger than the original Japanese byte length.

Rows that fail any gate are skipped and logged. No relocation or file expansion occurs.

## Immediate anchors

```text
PRGPACK+0xBFBEC -> Đã ổn?
PRGPACK+0xBFD2C -> Chọn tướng
PRGPACK+0xBFE4C -> Nhấn O
```

These should remain visually equivalent to the accepted 0.6.7.2 output.

## Output/report

Local package:

```text
GaiaMaster_0.6.8.0_PRODUCTION_SAFE_FIT_BATCH1.zip
```

Generated runtime files:

```text
[VI 0.6.8.0 PROD60 SAFEFIT B1].bin
[VI 0.6.8.0 PROD60 SAFEFIT B1].cue
[VI 0.6.8.0 PROD60 SAFEFIT B1].txt
[VI 0.6.8.0 CODEPAGE60].txt
```

The TXT report contains:
- exact Translation Master sources;
- APPLIED count;
- skipped control-token count;
- skipped overlength count;
- source mismatch/unsupported counts;
- full applied/skipped row lists;
- output BIN SHA1.

## Runtime gate

PASS if:
- three anchors render like 0.6.7.2;
- normal play remains stable;
- safe-fit translated rows appear correctly without global corruption.

On PASS, next work is a token-aware encoder for formatter/control rows. On freeze/corruption, stop immediately and inspect the generated report before any new build.
