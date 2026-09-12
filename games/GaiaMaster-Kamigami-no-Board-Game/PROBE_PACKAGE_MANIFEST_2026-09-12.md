# Gaia Master — probe package manifest 2026-09-12

This manifest records the exact locally generated probe packages from the current checkpoint so future sessions can identify them unambiguously.

## 0.6.3.2 BASELINE ONLY

Package:

```text
GaiaMaster_FontIsolation_0.6.3.2_BASELINE_ONLY.zip
```

SHA-256:

```text
8f1634a1824179f9ecedfb7fc09a613473fb9e1045d330886e38e5184545cc89
```

Contents:

```text
00_RUN_PROBE_0632.cmd
MANUAL_FALLBACK.txt
README_VI.txt
build_font_probe_0632.py
```

Builder size:

```text
21502 bytes
```

Runtime status:

```text
STABLE PASS WITH LOWER-ROW LOSS
```

## 0.6.3.3 EOL OVERWRITE TEST

Package:

```text
GaiaMaster_FontIsolation_0.6.3.3_EOL_OVERWRITE_TEST.zip
```

SHA-256:

```text
fabb1f5a1661eef1a98e3ee9492458d6f83a6a9157f7ce0ef52d35486fb52ec9
```

Contents:

```text
00_RUN_PROBE_0633.cmd
MANUAL_FALLBACK.txt
README_VI.txt
build_font_probe_0633.py
```

Builder size:

```text
21577 bytes
```

Runtime status:

```text
BUILT / awaiting runtime result
```

## Important

These ZIP binaries are diagnostic build packages generated during the ChatGPT work session. The repository source-of-truth is the surrounding technical documentation:

```text
HANDOFF_CURRENT.md
LATEST.md
CHARACTER_SELECT_FONT_REVERSE_0.1.md
PROBE_BUILD_INDEX.md
FONT_ISOLATION_0.6.3.2_STABLE_PASS.md
FONT_ISOLATION_0.6.3.3_EOL_OVERWRITE_TEST.md
```

If the local ZIP files are later re-generated, compare the package SHA-256 values above before assuming they are byte-identical to the 2026-09-12 versions.
