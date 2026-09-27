# Reference study: yugioh-fm-vi-patch

Reference reviewed: https://github.com/2ez4gcx/yugioh-fm-vi-patch  
Reviewed for Gaia Master workflow on 2026-09-27.

## What is publicly visible

The public Yu-Gi-Oh! Forbidden Memories repository is primarily a **release repository**, not a reverse-engineering source tree.

It publishes:
- PPF 3.0 patch files only, not the original game image;
- a small Python PPF applier;
- exact SHA-256 contract for the supported original BIN;
- exact SHA-256 contract for each patched BIN;
- automatic CUE generation;
- a `.gitattributes` rule forcing Windows batch files to CRLF;
- a `.gitignore` excluding BIN/CUE/ISO/IMG.

Its README also states that the translation includes:
- Vietnamese diacritics;
- a redrawn font;
- variable character widths;
- some code-byte modifications in addition to translated text/font data.

The public repository does **not** expose the author's extraction/reinsertion/VWF reverse tools, so the exact renderer-hook implementation cannot be copied or treated as evidence for Gaia Master's renderer.

## Lessons adopted for Gaia Master

### 1. Separate reverse/build workspace from public release artifact

Gaia's current B52 reverse tooling may stay detailed and evidence-heavy.

A future public release should be much smaller:
- patch file;
- patch applier;
- hashes;
- CUE helper;
- user-facing README;
- screenshots.

Do not ship source ROM/BIN/ISO.

### 2. Use a strong clean-image identity contract

Current reverse tooling uses exact SHA-1 contracts. For public release, also publish SHA-256 for:
- supported CLEAN image;
- final patched image.

The applier must stop on a wrong original image instead of applying optimistically.

### 3. Prefer patch distribution rather than a rebuilt disc image

PPF 3.0 is a strong fit for a fixed-layout MODE2/2352 PS1 release because it records changed raw offsets while leaving the original disc outside the repository.

Gaia should only generate the PPF after a final runtime-proven build is frozen.

### 4. Never overwrite the user's original disc

The release applier should:
1. verify original hash;
2. create a separate output BIN;
3. apply patch records;
4. create matching CUE;
5. verify final output hash.

This is already philosophically aligned with B52R31's guarded-output-copy design.

### 5. Treat line endings as part of build reliability

The Yu-Gi-Oh repo explicitly uses:

```
*.bat text eol=crlf
```

Gaia hit a real Windows CMD failure caused by launcher encoding/newline handling. PSXVH now adopts root-level `.gitattributes` rules for `.cmd/.bat/.ps1` CRLF.

### 6. Keep raw disc images out of Git history

PSXVH now has root `.gitignore` rules for BIN/CUE/ISO/IMG/CHD/MDF/MDS/PBP and large runtime RAM/DMA BIN captures.

Final patch files such as `.ppf` are intentionally **not** ignored.

### 7. VWF is an option, not a conclusion

Yu-Gi-Oh's README proves that a PS1 Vietnamese translation can successfully use variable-width rendering and code modifications.

It does **not** prove Gaia Master uses a compatible renderer or that Gaia should abandon the current frozen 12x12/mapping-only architecture.

For Gaia:
- keep current architecture frozen while live-source ownership is unresolved;
- if B52R24/B52R25 later proves the remaining UI is renderer-generated and fixed-width is the actual blocker, reopen a VWF/renderer-hook branch as a separately tested architecture experiment;
- do not mix such an experiment into the current canonical runtime line without evidence.

## Future Gaia release package

After final runtime validation, target package:

```
GaiaMaster-VI/
  gaia-master-vi.ppf
  apply_patch.py
  tao_cue.bat
  README.md
  SHA256SUMS.txt
```

Optional variants should each be generated directly from the same supported CLEAN image, never stacked on each other.

## Current status

This reference changes **release engineering and Windows checkout hygiene** now.

It does not change:
- B52R14R1 as current exact reverse base;
- the B52R22-B52R32 runtime ownership chain;
- the frozen 12x12 production architecture;
- the rule that overall Runtime PASS remains NO until gameplay proof exists.
