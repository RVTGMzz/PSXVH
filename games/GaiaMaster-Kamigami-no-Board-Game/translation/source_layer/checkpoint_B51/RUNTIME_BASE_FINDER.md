# Gaia Master B51R1 runtime-base finder

B51R1 build mode must not guess a runtime base from its filename/version label.

Use the read-only finder:

`tools/find_gaia_b51r1_runtime_base.py`

Windows launcher:

`tools/00_FIND_B51R1_RUNTIME_BASE.cmd`

## Required base contract

A candidate BIN is accepted only when all of these are proven from its bytes:

- it is not the CLEAN image itself
- raw image size matches CLEAN
- PRGPACK BDP parses/checksums correctly
- frozen 60-glyph runtime mapping exists
- B40 / Batch42 exact fields: `560/560`
- B43 exact fields: `102/102`
- intro exact fields: `19/19`

The finder never modifies any BIN.

## Usage

Place the exact CLEAN BIN and candidate runtime BINs in the game directory, then run:

```bash
python tools/find_gaia_b51r1_runtime_base.py "GaiaMaster - Kamigami no Board Game (Japan).bin"
```

To scan another folder:

```bash
python tools/find_gaia_b51r1_runtime_base.py \
  "GaiaMaster - Kamigami no Board Game (Japan).bin" \
  --dir "C:\path\to\candidate-builds"
```

Recursive scan:

```bash
python tools/find_gaia_b51r1_runtime_base.py \
  "GaiaMaster - Kamigami no Board Game (Japan).bin" \
  --dir "C:\path\to\candidate-builds" \
  --recursive
```

Or double-click:

`tools/00_FIND_B51R1_RUNTIME_BASE.cmd`

## Selection rule

Use a BIN as `--build-from` only if the finder prints:

`PASS frozen60 + 560/102/19`

Do not use a file merely because its name says `0.6.55.0`, `R5`, `final`, or similar. The byte gates are authoritative.

## Safety

This is a read-only diagnostic utility. It does not patch font, text, BDP checksums, sectors, or any other bytes.
