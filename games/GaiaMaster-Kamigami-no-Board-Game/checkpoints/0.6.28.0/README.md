# Checkpoint 0.6.28.0 - Batch 19

Current candidate: Exact-Offset Lock / Session Handoff.

Key behavior:
- keeps Batch 18 residual/consensus fitting;
- exports fitting translated rows into the proven exact `file + offset` compact override path;
- preserves historical 0.6.14.1 locks;
- generates `RESIDUAL_ALPHA`, `FIT_PRESSURE`, and `EXACT_OFFSET_LOCKS` reports;
- recovers outputs from package or temporary source folders;
- font remains frozen;
- legacy coverage gate remains 397/397.

Runtime status: candidate only. Syntax PASS. Clean-ROM build and runtime QA pending.

Next work should consume the three Batch 19 reports and runtime screenshots. Do not reopen font work unless runtime demonstrates a real glyph defect.
