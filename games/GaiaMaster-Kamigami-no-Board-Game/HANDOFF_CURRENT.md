# HANDOFF CURRENT - Gaia Master PS1 Viet hoa

Updated: 2026-09-16
Branch: `gaia-character-select-font-atlas-reverse-01`
Repo: `ronvotri/Viet-Hoa-PS1`

## Current priority

Translation-first source work has reached **B51R1 STATIC CI PASS**.

Important distinction:

- **B50 remains the canonical validated binary/source checkpoint** because no real CLEAN BIN/runtime base BIN was available inside the connected environment for actual binary execution.
- **B51R1 STATIC CI PASS is proven** and is the production-candidate layer to use for the next real BIN dry-run/build.
- Do not resume font work unless the user explicitly returns to it.
- Do not call Runtime PASS without gameplay screenshots.

## Clean source contract

Exact CLEAN Japan BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

Never patch an unknown or already modified BIN as the CLEAN source oracle.

## Source-layer state

Full scanner/source triage is closed.

Final translated source layer before production materialization:

- unique translated Japanese rows: `1,186`
- exact source occurrences: `1,229`
- context rows intentionally parked: `4`

Parked rows:

- `PRGPACK.BDP 0x1269bc` - `俺は`
- `PRGPACK.BDP 0xde9fc` - `ファ：`
- `PRGPACK.BDP 0x16e580` - `（未使用`
- `PRGPACK.BDP 0x96290` - `体力が%d%s`

Do not guess these four without better runtime context.

## B23-B49 static-fit history

B23 established the runtime field-budget model:

- source field = Japanese CP932 byte budget
- ordinary display chars = two runtime bytes
- `%...`, `/V`, `/v`, `/Pxx`, `/PFx` controls keep raw/control byte lengths

B24-B49 produced compact runtime candidates without overwriting meaning-first `vi_full`.

Final B49:

- unique translated rows ready: `1186/1186`
- exact occurrences ready: `1229/1229`
- rows still needing compact: `0`
- candidate-vs-field byte gate: PASS
- ROM/font/pointer modified: NO
- Runtime PASS: NO

## B50 canonical exact-offset overlay

Canonical artifact:

`GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv`

Archived under:

`translation/source_layer/checkpoint_B50/`

Restore script:

`translation/source_layer/checkpoint_B50/restore_b50_overlay.py`

Raw size:

`162851`

Raw SHA256:

`448bc34afa675299b0de20c54d804d5765e7f9954f67c39058884b318de504b7`

Gzip SHA256:

`4b8373f53ea04b3b89420c874870b07016fd817c51e603b5644643e6cc122b60`

B50 static materialization:

- exact rows: `1229/1229`
- direct `vi_full`: `41`
- compact candidates: `1188`
- duplicate exact keys: `0`
- overlapping exact fields: `0`
- byte-fit violations: `0`
- negative free-byte rows: `0`
- token/control preservation: PASS
- ROM/font/pointer modified: NO
- Runtime PASS: NO

## Important B51 discovery: B50 byte-fit was not enough

The first B51 production encoder audit found that B50 contained Unicode Vietnamese characters outside the frozen 60-glyph runtime codepage.

Full static census proved exactly:

- unsupported runtime characters: `19`
- affected exact B50 rows: `64`

The unsupported set was:

`À Á Â É è õ ý Ă Ư ẳ ẵ ẹ Ế ễ Ồ Ở ỡ Ừ ỳ`

This is production-charset debt in B50, not a request to expand the font.

## B51R1 frozen-60 text correction layer

Correction manifest:

`translation/source_layer/B51_RUNTIME_CHARSET_CORRECTIONS.csv`

Production wrapper:

`tools/build_gaia_b51r1_guarded_exact_overlay.py`

B51R1 rules:

- keep canonical B50 immutable
- apply exactly `64` file+offset text corrections
- correction must match the exact old B50 candidate before replacement
- preserve formatter/control token order
- correction must fit the exact B50 source field
- correction may not exceed the already-approved B50 candidate byte budget
- no new glyphs
- no font/mapping mutation

One correction was tightened after CI caught a byte overflow:

`PRGPACK.BDP+0x90054` changed from proposed `hay bị dí` to `bị dí`, staying within the original 16-byte field/budget.

## B43 padded-field compatibility correction

CI then exposed an overly strict new validator assumption at:

`PRGPACK.BDP+0xDE0A0`

Historical B43 manifest row:

- Japanese: `はい　　　いいえ`
- Vietnamese: `Có    Không`
- `field_bytes = 22`

The proven B43 builder treats manifest `field_bytes` as authoritative and permits padded source fields. It does **not** require `field_bytes == len(japanese.encode(cp932))`.

B51R1 therefore uses the historical compatible rule for B40/B43 regression manifests:

`field_bytes >= literal Japanese CP932 bytes`

This relaxation applies only to historical manifest reconstruction. B50 exact source-field identity remains strict.

## B51R1 STATIC CI PASS

Static validator:

`tools/validate_gaia_b51_static.py`

Workflow:

`.github/workflows/gaia-b51-static-validation.yml`

Validated commit:

`33a5049bf6dc932a95892eeb1dbb99033c8d074b`

GitHub Actions run:

`35005218964`

Result: **SUCCESS**

Proof file:

`translation/source_layer/checkpoint_B51/B51R1_STATIC_CI_PROOF.txt`

Exact CI result:

- B51/B51R1 import + syntax: PASS
- B50 restore SHA256: PASS
- B50 size: `162851/162851`
- B50 exact candidate rows: `1229/1229`
- raw B50 unsupported chars: `19/19` known debt
- raw B50 rows needing charset cleanup: `64/64` known debt
- B51R1 exact-key corrections: `64/64`
- corrected frozen-60 charset gate: PASS, `0` unsupported rows
- canonical B50 mutated: NO
- new font glyphs added: `0`
- B50 direct `vi_full`: `41/41`
- B50 compact candidates: `1188/1188`
- B40 / Batch42 protected exact manifest: `560/560`
- B43 protected exact manifest: `102/102`
- combined protected historical fields: `662/662`
- intro protected exact manifest: `19/19`
- B51R1 overlap with B40: `0`
- B51R1 overlap with B43: `0`
- B51R1 overlap with intro19: `0`
- legacy Alpha static contract: `397/397`
- Translation Master row contract: `596/596`
- duplicate/overlap/byte/token gates: PASS
- ROM/font/pointer modified: NO
- CLEAN source identity tested: NO, needs real CLEAN BIN
- build/output bytes tested: NO, needs real runtime base BIN
- Runtime PASS: NO

## B51/B51R1 architecture

Core B51 tool:

`tools/build_gaia_b51_guarded_exact_overlay.py`

B51R1 production wrapper:

`tools/build_gaia_b51r1_guarded_exact_overlay.py`

B50/B51R1 is an additive text layer, not a replacement superset of older runtime manifests.

Historical exact spans are protected:

- B40/Batch42 `560`
- B43 `102`
- intro `19`

A new write may not partially/conflictingly overlap a protected historical field.

Build mode requires a known-good runtime base that already carries frozen-60 and already byte-verifies `560/102/19` before B51R1. These contracts are rechecked after patching.

B51R1 also snapshots font atlas + mapping and requires byte-identical values in memory and after output read-back.

It does not invoke `READABLE`, `R5_PATCHED`, Batch45 font-polish code, or any font builder.

## Windows launchers

Guarded dry-run:

`tools/00_RUN_B51R1_GUARDED_DRYRUN.cmd`

Guarded build:

`tools/00_BUILD_B51R1_GUARDED_EXACT_OVERLAY.cmd`

The dry-run launcher defaults to:

`GaiaMaster - Kamigami no Board Game (Japan).bin`

The build launcher requires a separate known-good runtime base BIN and explicitly warns not to use CLEAN as the build base.

## Next required step

Run the **real B51R1 guarded dry-run** against the exact CLEAN BIN:

```bash
python tools/build_gaia_b51r1_guarded_exact_overlay.py "GaiaMaster - Kamigami no Board Game (Japan).bin"
```

Or use:

`tools/00_RUN_B51R1_GUARDED_DRYRUN.cmd`

Only after the real CLEAN dry-run passes, build from a known-good runtime base:

```bash
python tools/build_gaia_b51r1_guarded_exact_overlay.py \
  "GaiaMaster - Kamigami no Board Game (Japan).bin" \
  --build-from "KNOWN_GOOD_RUNTIME_BASE.bin"
```

Or use:

`tools/00_BUILD_B51R1_GUARDED_EXACT_OVERLAY.cmd`

Do not use CLEAN itself as `--build-from`.

## Allowed claims right now

- B50 exact-offset static byte-fit PASS: YES
- B51R1 STATIC CI PASS: YES
- B51R1 real CLEAN guarded dry-run PASS: **NOT YET CLAIMED**
- B51R1 real build/static byte verification PASS: **NOT YET CLAIMED**
- Runtime PASS: **NO**

## Frozen formatting controls

Preserve exact order where present:

`%s`, `%d`, `%2d`, `%4d`, `%5d`, `%+3d`, `/V`, `/v`, `/Pxx`, `/PFx`

## Font work parked

Do not let font work distract from the current production pass.

Remembered only for a later explicit font session:

- plain lowercase `ă` should revert to the proven historical 0.6.55.0 glyph
- current `â`/circumflex family should not be reset
- `ẻ/ể` hook-above polish remains separate
- regression phrase: `100 năm một lần`

Frozen architecture remains:

- native 12x12 / 72-byte / 4bpp / LOW nibble first
- static mapping-only
- frozen 60-glyph Vietnamese codepage
- no renderer hook
- no pointer redirect
- no 12x16
- no 6x12
- no composite overlay

## Current continuation sentence for a fresh chat

Use:

`Tiếp tục Gaia Master từ HANDOFF_CURRENT.md trên branch gaia-character-select-font-atlas-reverse-01. B51R1 STATIC CI PASS đã chứng minh 1229/1229, correction frozen-60 64/64, 0 unsupported sau correction, historical 560/102/662/19/397/596 đều PASS. B50 vẫn là canonical binary checkpoint vì chưa chạy BIN thật. Bước kế tiếp là chạy build_gaia_b51r1_guarded_exact_overlay.py dry-run trên CLEAN SHA1 f4d5298583c90d89c4b7e51d2dde160ee07f2aec; chỉ sau khi PASS mới build từ known-good runtime base. Không đụng font và không gọi Runtime PASS khi chưa có screenshot gameplay.`
