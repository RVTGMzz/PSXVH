# Gaia Master B50 exact-offset runtime candidate checkpoint

Branch: `gaia-character-select-font-atlas-reverse-01`
Date: 2026-09-15

This directory archives the canonical B50 exact-offset runtime candidate overlay needed for the next chat/session.

## Canonical artifact

Original filename:

`GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv`

Original byte size: `162851`

Original SHA256:

`448bc34afa675299b0de20c54d804d5765e7f9954f67c39058884b318de504b7`

The CSV is stored as gzip -> base64 -> 4 lexical parts because the GitHub connector only accepts UTF-8 text writes.

Compressed gzip byte size: `34538`

Compressed gzip SHA256:

`4b8373f53ea04b3b89420c874870b07016fd817c51e603b5644643e6cc122b60`

Base64 character length: `46052`

Parts:

- `parts/GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv.gz.b64.part01`
- `parts/GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv.gz.b64.part02`
- `parts/GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv.gz.b64.part03`
- `parts/GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv.gz.b64.part04`

Use `restore_b50_overlay.py` in this directory to reconstruct and verify the original CSV.

## B50 gates

- unique translated Japanese source rows behind overlay: `1186`
- exact source occurrences materialized: `1229 / 1229`
- direct `vi_full` exact occurrences: `41`
- compact-candidate exact occurrences: `1188`
- duplicate `file + offset` collisions: `0`
- byte-fit violations: `0`
- negative free-byte rows: `0`
- source token/control preservation: PASS
- ROM/font/pointer modified: NO
- Runtime PASS claim: NO

## Clean source contract

Known CLEAN Japan BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

Never patch from an unknown or already modified BIN.

## Next step

B51 should consume the restored B50 overlay and build a guarded exact-offset patch layer against the exact CLEAN BIN. Before writing each field, verify the Japanese source bytes/identity and field size. Preserve all existing project hard gates. Do not call Runtime PASS until a successful build is followed by gameplay screenshot evidence.
