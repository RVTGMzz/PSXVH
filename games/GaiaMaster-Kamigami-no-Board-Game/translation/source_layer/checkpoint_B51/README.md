# Gaia Master B51R1 guarded exact-offset overlay

Branch: `gaia-character-select-font-atlas-reverse-01`
Date: 2026-09-16

## Current status

**B51R1 STATIC CI PASS** is now proven.

The canonical binary/runtime checkpoint is still **B50** because no real CLEAN BIN or proven runtime base BIN was available to this connected environment for the binary dry-run/build.

Do not call B51R1 build PASS or Runtime PASS yet.

Static proof:

`B51R1_STATIC_CI_PROOF.txt`

Validated commit:

`33a5049bf6dc932a95892eeb1dbb99033c8d074b`

GitHub Actions run:

`35005218964`

## What CI proved

- B51/B51R1 Python import + syntax: PASS
- canonical B50 restore SHA256: PASS
- B50 raw size: `162851 / 162851`
- B50 exact runtime candidates: `1229 / 1229`
- B50 direct `vi_full`: `41 / 41`
- B50 compact candidates: `1188 / 1188`
- raw B50 frozen-codepage debt: exactly `19` unsupported characters across `64` exact rows
- B51R1 text-only correction coverage: `64 / 64`
- corrected frozen-60 charset: PASS, `0` unsupported rows
- canonical B50 mutated: NO
- new font glyphs added: `0`
- B40 / Batch42 protected exact manifest: `560 / 560`
- B43 protected exact manifest: `102 / 102`
- combined historical exact manifests: `662 / 662`
- intro protected exact manifest: `19 / 19`
- legacy Alpha static contract: `397 / 397`
- Translation Master row contract: `596 / 596`
- duplicate / overlap / byte / token guards: PASS
- ROM/font/pointer modified by static validation: NO
- Runtime PASS claim: NO

## Why B51R1 exists

B50 passed static byte-fit, but B51 production encoding exposed a second constraint: the runtime font is a frozen 60-glyph Vietnamese codepage.

The B50 overlay contained 19 Vietnamese characters that are valid Unicode and fit the source byte budgets, but are not available in the frozen production codepage. They appeared in 64 exact runtime rows.

B51R1 fixes this **without changing the font**.

Correction layer:

`translation/source_layer/B51_RUNTIME_CHARSET_CORRECTIONS.csv`

Rules:

- exactly 64 file+offset corrections
- every correction must match the original B50 candidate exactly before replacement
- replacement must preserve formatter/control-token order
- replacement must remain inside the original field
- replacement may not exceed the already-approved B50 candidate byte budget
- B50 itself stays immutable
- no new Vietnamese glyphs are added

## B43 padded-field compatibility

Static CI also exposed an incorrect new assumption in the first B51 validator.

The historical B43 manifest contains legitimate padded fields where `field_bytes` can be larger than the literal Japanese CP932 byte length. Example: `PRGPACK.BDP+0xDE0A0`.

The proven B43 builder treats manifest `field_bytes` as authoritative and compares the padded CLEAN field after decoding/space trimming. B51R1 now follows that proven historical behavior instead of forcing `field_bytes == len(japanese.encode(cp932))` for B43 regression manifests.

This changes only the validator's historical compatibility rule. It does not loosen the exact B50 source-field identity rule.

## Canonical B50 input

Restored artifact:

`translation/source_layer/checkpoint_B50/GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv`

Expected raw byte size:

`162851`

Expected raw SHA256:

`448bc34afa675299b0de20c54d804d5765e7f9954f67c39058884b318de504b7`

Expected gzip SHA256:

`4b8373f53ea04b3b89420c874870b07016fd817c51e603b5644643e6cc122b60`

B51R1 restores this CSV from the four archived base64 parts and verifies both hashes before use.

## CLEAN source contract

Exact CLEAN Japan BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

The CLEAN BIN remains the immutable source-identity oracle.

## Additive-layer rule

B50/B51R1 is an additive source layer, not a replacement superset of the older exact runtime manifests.

Historical fields are protected:

- a B51R1 write that does not overlap a protected historical field is allowed
- an exact same-span, exact same-byte overlap is allowed
- any partial or conflicting overlap hard-fails
- build base must already byte-verify Batch42/B40 `560/560`, Batch43 `102/102`, and intro `19/19` before B51R1 is applied
- those same historical fields are verified again after B51R1 is applied

Current static CI found `0` B51R1 overlaps with B40, B43, or intro19.

## No-font rule

B51R1 is text-only.

It does not invoke `READABLE`, `R5_PATCHED`, Batch45 font-polish code, or any font builder.

Build mode snapshots the build base's font atlas and mapping ranges and requires byte-identical values after patching and after output read-back.

## Tools

Core guarded layer:

`tools/build_gaia_b51_guarded_exact_overlay.py`

Production wrapper with frozen-60 corrections:

`tools/build_gaia_b51r1_guarded_exact_overlay.py`

Static CI validator:

`tools/validate_gaia_b51_static.py`

Windows guarded dry-run launcher:

`tools/00_RUN_B51R1_GUARDED_DRYRUN.cmd`

Windows guarded build launcher:

`tools/00_BUILD_B51R1_GUARDED_EXACT_OVERLAY.cmd`

## Next required binary step

Run the guarded dry-run against the exact CLEAN Japan BIN:

```bash
python tools/build_gaia_b51r1_guarded_exact_overlay.py "GaiaMaster - Kamigami no Board Game (Japan).bin"
```

A successful real execution may be called **B51R1 GUARDED DRY-RUN PASS**.

It is not yet a build PASS or Runtime PASS.

Only after the real dry-run is clean, build from a known-good runtime base BIN that already carries frozen-60 and passes the historical `560/102/19` contracts:

```bash
python tools/build_gaia_b51r1_guarded_exact_overlay.py \
  "GaiaMaster - Kamigami no Board Game (Japan).bin" \
  --build-from "KNOWN_GOOD_RUNTIME_BASE.bin"
```

B51R1 deliberately refuses CLEAN itself as `--build-from`, because this layer does not install/regenerate Vietnamese font data.

## Runtime rule

Even after a successful guarded build:

**Runtime PASS = NO**

Gameplay screenshots are mandatory before any Runtime PASS claim. Compact B24-B49 story strings still require visual/editorial judgment in actual gameplay.
