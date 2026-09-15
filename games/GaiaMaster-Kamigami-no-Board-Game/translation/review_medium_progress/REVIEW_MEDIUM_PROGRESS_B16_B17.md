# Gaia Master REVIEW-MEDIUM progress through Batch17

Translation-first/source-triage checkpoint. Runtime/build is untouched and this is not a Runtime PASS.

## Input corpus

- Full reviewed-deduped queue: 6,229 unique Japanese candidates
- HIGH-FIRST: 3,504, restored from the closed Batch15 checkpoint
- REVIEW-MEDIUM: 2,725

## Batch16 - NUL review

All 251 REVIEW-MEDIUM rows whose best scanner occurrence is NUL-terminated were reviewed.

- 41 source translations added
- 1 proper-name row preserved
- 1 system/input-table fragment preserved
- 1 row parked for context review
- 207 NUL scanner false positives classified
- token/control order gate: PASS

## Batch17 - CTRL review

All 324 remaining REVIEW-MEDIUM rows whose best scanner occurrence is CTRL-terminated were reviewed.

- 324 scanner false positives classified
- coherent-Japanese safety gate hits: 0
- protected halfwidth UI keyword hits: 0

After Batch17, 2,150 REVIEW-MEDIUM rows remain untouched, all with best terminator OTHER.

## Safety rules

- Original Japanese/file/offset evidence is preserved.
- No ROM patching is performed by this pass.
- No runtime/build strings are changed.
- Do not claim Runtime PASS without gameplay screenshot evidence.
