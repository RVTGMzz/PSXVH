# Gaia Master B51 guarded exact-offset overlay

Branch: `gaia-character-select-font-atlas-reverse-01`
Date: 2026-09-16

## Status

B51 tooling is implemented, but the canonical source checkpoint remains **B50** until the guarded dry-run and build are executed against the actual BIN files.

Current execution status:

- B50 checkpoint restore/hash contract: implemented in B51 tool
- B50 exact schema gate: implemented
- B50 row gate: `1229`
- B50 production split gate: `41` direct `vi_full` + `1188` compact candidates
- CLEAN source identity gate: implemented
- duplicate/overlap rejection: implemented
- token/control preservation: implemented for `%...`, `/V`, `/v`, `/Pxx`, `/PFx`
- BDP owner-boundary gate: implemented
- historical B40/Batch42 protection: `560`
- historical B43 protection: `102`
- combined historical exact protection: `662`
- legacy Alpha static contract: `397`
- Translation Master row contract: `596`
- intro exact protection: `19`
- font-atlas write guard: implemented
- font-mapping write guard: implemented
- font/mapping read-back equality after build: implemented
- actual guarded dry-run on CLEAN BIN: **PENDING LOCAL BIN**
- actual guarded build on proven runtime BIN: **PENDING LOCAL BIN**
- Runtime PASS claim: **NO**

Do not promote B51 to a runtime checkpoint until gameplay screenshots are supplied after a successful build.

## Canonical B50 input

Restored artifact:

`translation/source_layer/checkpoint_B50/GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv`

Expected raw byte size:

`162851`

Expected raw SHA256:

`448bc34afa675299b0de20c54d804d5765e7f9954f67c39058884b318de504b7`

Expected gzip SHA256:

`4b8373f53ea04b3b89420c874870b07016fd817c51e603b5644643e6cc122b60`

B51 restores this CSV directly from the four archived base64 parts and verifies both hashes before use.

## CLEAN source contract

Exact CLEAN Japan BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

The CLEAN BIN is used as the immutable source-identity oracle. B51 refuses an unknown or already-modified BIN in the CLEAN argument.

## Additive-layer rule

B50 is an **additive source layer**, not a replacement superset of the historical runtime manifests.

Therefore B51 does not require the 560 Batch42 fields, 102 Batch43 fields, or 19 intro fields to be present in B50. Instead it protects those historical spans:

- a B50 write that does not overlap a protected field is allowed;
- an exact same-span, exact same-byte overlap is allowed;
- any partial or conflicting overlap hard-fails the dry-run.

In build mode the chosen runtime base must already byte-verify the historical `560 + 102 + 19` contracts before B50 is applied. The same contracts are byte-verified again after B50 is applied.

## No-font rule

B51 is text-only.

It imports the historical LEGACY module only for frozen constants, encoding helpers, ISO/BDP parsing, checksums, and sector regeneration. It does **not** invoke `READABLE`, `R5_PATCHED`, Batch45 font-polish code, or any font builder.

Build mode also snapshots the base BIN's font atlas and mapping ranges and requires them to be byte-identical after patching and after read-back.

## Tool

`tools/build_gaia_b51_guarded_exact_overlay.py`

### Guarded dry-run

From the game directory:

```bash
python tools/build_gaia_b51_guarded_exact_overlay.py "GaiaMaster - Kamigami no Board Game (Japan).bin"
```

A successful execution may be called **B51 guarded dry-run/static PASS**. It is not a build PASS and not a Runtime PASS.

### Guarded build

Use a known-good runtime base BIN that already carries the frozen 60-glyph codepage and passes the historical 560/102/19 byte contracts:

```bash
python tools/build_gaia_b51_guarded_exact_overlay.py \
  "GaiaMaster - Kamigami no Board Game (Japan).bin" \
  --build-from "KNOWN_GOOD_RUNTIME_BASE.bin"
```

B51 deliberately refuses to use the CLEAN BIN itself as `--build-from`, because B51 does not install or regenerate the Vietnamese font/codepage.

A successful execution may be called **B51 guarded build + static byte verification PASS** only when the generated report confirms every gate.

## Runtime rule

Even after a successful guarded build:

**Runtime PASS = NO**

Gameplay screenshots are mandatory before any Runtime PASS claim. Compact B24-B49 story strings still require visual/editorial judgment in real gameplay.
