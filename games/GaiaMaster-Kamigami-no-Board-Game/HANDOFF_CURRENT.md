# HANDOFF CURRENT - Gaia Master PS1 Viet hoa

Updated: 2026-09-15 23:59 +07
Branch: `gaia-character-select-font-atlas-reverse-01`
Repo: `ronvotri/Viet-Hoa-PS1`

## Current priority

Translation-first source work has reached the B50 exact-offset runtime-candidate overlay milestone.

Do not resume the old font-first priority automatically. Font work is parked unless the user explicitly returns to it.

Do not call Runtime PASS without gameplay screenshot evidence.

## Clean source contract

Exact CLEAN Japan BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

Never patch an unknown or already modified BIN.

## Scanner/source triage completion

Full scanner run from the CLEAN BIN produced:

- scanner candidates: 13,330
- raw unseen unique Japanese: 6,361
- reviewed committed unique JP already known: 634
- new source occurrences: 12,517
- new unique Japanese queue: 6,229
- HIGH-FIRST: 3,504
- REVIEW-MEDIUM: 2,725

Both HIGH-FIRST and REVIEW-MEDIUM source triage are closed.

Final full 6,229-row triage state before context cleanup:

- source-translated: 1,177
- proper names preserved: 59
- system/input-table rows preserved: 16
- scanner false positives: 4,963
- context-review rows: 14
- untouched: 0

Batch22 then resolved 9 context rows as real source translations and reclassified 1 known overlap artifact.

Current translated source layer:

- unique translated Japanese rows: 1,186
- exact source occurrences: 1,229
- context rows still intentionally parked: 4

The 4 parked rows are:

- `PRGPACK.BDP 0x1269bc` - `俺は`
- `PRGPACK.BDP 0xde9fc` - `ファ：`
- `PRGPACK.BDP 0x16e580` - `（未使用`
- `PRGPACK.BDP 0x96290` - `体力が%d%s`

Do not guess these four without better context.

## B22R1 exact occurrence correction

B22 originally split `all_exact_refs` using the wrong delimiter. B22R1 fixed it to `|`.

B22R1 proof:

- unique translated Japanese rows: 1,186
- expanded exact occurrences: 1,229
- expected occurrence_count sum: 1,229
- exact-ref parse/conservation: PASS
- token/control audit: PASS

## B23 static byte-fit preflight

Method:

- source field size = exact CP932 byte length of Japanese source
- ordinary display chars = 2 runtime bytes
- `%...`, `/V`, `/v`, `/Pxx`, `/PFx` controls retain their control/ASCII byte lengths

Initial B23 result:

- unique translations: 1,186
- direct `vi_full` fits: 37
- rows needing compact: 1,149

No ROM/font/pointer data was modified.

## B24-B49 compact-fit completion

B24 through B49 produced separate `vi_compact` runtime candidates without overwriting meaning-first `vi_full`.

Final B49 result:

- translated unique source rows: 1,186
- exact occurrences represented: 1,229
- direct `vi_full` fits: 37
- compact fits B24-B49: 1,149
- unique rows ready by static byte-fit: 1,186 / 1,186
- exact occurrences ready by byte-fit: 1,229 / 1,229
- unique rows still needing compact: 0
- exact occurrences still needing compact: 0
- candidate-vs-field byte gate: PASS
- ROM/font/pointer modified: NO
- Runtime PASS claim: NO

Important: compact text is a static-field candidate. Some aggressively shortened story fragments and abbreviations must still be judged in gameplay before final editorial lock.

## B50 canonical exact-offset overlay

B50 expands the completed source layer to every real file+offset occurrence.

B50 result:

- exact occurrences expected: 1,229
- exact occurrences materialized: 1,229
- file+offset collisions: 0
- byte-fit violations: 0
- negative free-byte rows: 0
- direct `vi_full` exact occurrences: 41
- compact exact occurrences: 1,188
- static exact-occurrence gate: PASS
- ROM/font/pointer modified: NO
- Runtime PASS claim: NO

Canonical artifact:

`GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv`

Original byte size: `162851`

Original SHA256:

`448bc34afa675299b0de20c54d804d5765e7f9954f67c39058884b318de504b7`

The exact overlay is archived in the repo as gzip -> base64 -> 4 UTF-8 text parts under:

`translation/source_layer/checkpoint_B50/parts/`

Restore with:

`translation/source_layer/checkpoint_B50/restore_b50_overlay.py`

Checkpoint README:

`translation/source_layer/checkpoint_B50/README.md`

The restore script verifies gzip SHA256, raw byte size, and raw SHA256 before writing the CSV.

## Next task for the new chat: B51

Start from the restored B50 exact-offset overlay.

B51 goal: create a guarded exact-offset patch/build layer against the exact CLEAN BIN, without silently touching unrelated bytes.

Required B51 behavior:

1. Require CLEAN Japan BIN SHA1 exactly `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`.
2. Restore/read B50 overlay from the repo checkpoint.
3. Before each write, verify the exact Japanese source identity at `file + offset` and verify the expected field byte size.
4. Preserve token/control order for `%s`, `%d`, `%2d`, `%4d`, `%5d`, `%+3d`, `/V`, `/v`, `/Pxx`, `/PFx`.
5. Reject duplicate or overlapping writes.
6. Write only the exact field span, preserving field termination/padding rules used by the proven builders.
7. Produce a dry-run report first with planned writes, source verification, byte fit, and collisions.
8. Only after the dry-run is clean should a build artifact be produced.
9. Re-run historical exact-field regression gates after patching.
10. Do not call Runtime PASS until the user runs it and provides gameplay screenshots.

Prefer a new B51 tool/script rather than mutating historical builders.

## Historical runtime/build contracts that must not regress

Previously proven build contracts include:

- Batch42 exact fields: 560 / 560
- Batch43: 102 / 102
- combined exact fields: 662 / 662
- legacy Alpha gate: 397 / 397
- Translation Master runtime audit: 596 / 596
- intro exact fields: 19 / 19

These are historical regression gates, not whole-game source coverage.

## Frozen formatting controls

Preserve exact token order where present:

`%s`, `%d`, `%2d`, `%4d`, `%5d`, `%+3d`, `/V`, `/v`, `/Pxx`, `/PFx`

## Font work parked

Do not let font work distract from B51 unless the user explicitly returns to it.

Still remembered:

- plain lowercase `ă` should revert to the proven historical 0.6.55.0 glyph
- current `â`/circumflex family should NOT be reset
- `ẻ/ể` hook-above polish remains separate
- later regression phrase: `100 năm một lần`

Frozen font architecture remains:

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

`Tiếp tục Gaia Master từ HANDOFF_CURRENT.md trên branch gaia-character-select-font-atlas-reverse-01. Current canonical checkpoint là B50 exact-offset overlay 1229/1229 static byte-fit PASS. Restore overlay từ translation/source_layer/checkpoint_B50 rồi làm B51 guarded dry-run/build layer. Không đụng font và không gọi Runtime PASS khi chưa có screenshot gameplay.`
