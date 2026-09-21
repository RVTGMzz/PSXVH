# B52R27 - Disc payload fingerprint resolver

Date: 2026-09-21

## Status

**TOOLING READY / REAL PAYLOAD SEARCH PENDING / NO PATCH CLAIM**

B52R27 is a read-only shortcut from a proven B52R24 linear DMA payload back to disc ownership.

Files:
- `tools/gaia_b52r27_disc_payload_fingerprint.py`
- `tools/00_RUN_B52R27_DISC_FINGERPRINT.cmd`

Inputs:
- `GaiaMaster_B52R24_DMA_SOURCE.bin`
- exact B52R14R1 BIN preferred, CLEAN fallback

Behavior:
- verifies exact known BIN SHA1;
- parses MODE2/Form1 ISO9660;
- indexes logical files recursively;
- searches the full captured payload inside each Form1 file;
- when no full match exists, compares aligned 64-byte anchors from start/middle/end;
- maps candidates to file-relative offset, ISO extent and starting LBA;
- skips oversized >64MiB and non-Form1 streams to keep the probe bounded.

Verdicts:
- `EXACT_DISC_PAYLOAD_MATCH_FOUND`
- `ALIGNED_ANCHOR_EVIDENCE_ONLY`
- `NO_DISC_FINGERPRINT_MATCH`

Evidence rule:
- EXACT is strong evidence that the captured payload exists verbatim in the reported ISO file/offset.
- aligned anchors are only suggestive.
- no match supports a transform/decompress/rasterize/compose hypothesis, but does not prove which one.
- no disc mutation is performed.

Validation:
- full Python source compiled successfully during authoring;
- `B52R27 DISC FINGERPRINT SELFTEST PASS`.

Real Gaia Master payload execution remains **PENDING**.

Overall Runtime PASS remains **NO**.
