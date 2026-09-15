#!/usr/bin/env python3
# -*- coding: ascii -*-
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import traceback
from pathlib import Path

CLEAN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"
BUILDER_NAME = "build_gaia_06551_batch45r2_font_micro_polish.py"
LOG_NAME = "BUILD_LOG_0.6.55.1_BATCH45R2.txt"


def normalize_root_arg(raw: str) -> str:
    """Normalize a package-root argv value before Path() sees it.

    Windows launchers commonly expose %%~dp0 with a trailing backslash. If that
    path is passed as a quoted argv value, the closing quote can leak into the
    argument seen by Python. Be deliberately defensive here so a dirty launcher
    cannot create an invalid log path.
    """
    s = str(raw).strip()
    while s.startswith('"'):
        s = s[1:]
    s = s.rstrip(' \t\r\n"')
    while len(s) > 3 and s.endswith(("\\", "/")):
        s = s[:-1]
        s = s.rstrip(' \t\r\n"')
    if not s:
        raise ValueError("Package root argument is empty after normalization")
    return s


def _selftest() -> int:
    cases = {
        'C:\\Users\\win\\Downloads\\Pkg\\': 'C:\\Users\\win\\Downloads\\Pkg',
        'C:\\Users\\win\\Downloads\\Pkg" ': 'C:\\Users\\win\\Downloads\\Pkg',
        '"C:\\Users\\win\\Downloads\\Pkg\\"': 'C:\\Users\\win\\Downloads\\Pkg',
        '  "C:\\Users\\win\\Downloads\\Pkg"  ': 'C:\\Users\\win\\Downloads\\Pkg',
    }
    for raw, want in cases.items():
        got = normalize_root_arg(raw)
        if got != want:
            raise RuntimeError("root argv normalization failed: %r -> %r, want %r" % (raw, got, want))
    print("PACKAGE DRIVER ROOT-ARGV SELFTEST PASS")
    return 0


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().lower()


def log_line(log, text=""):
    line = str(text)
    print(line, flush=True)
    log.write(line + "\n")
    log.flush()


def find_clean(root: Path, log) -> Path:
    candidates = []
    for p in root.rglob("*.bin"):
        if not p.is_file():
            continue
        # The package itself never contains ROM/BIN files under Core. Skip any
        # accidental generated output under Core anyway and prefer root-level ROMs.
        try:
            rel = p.relative_to(root)
        except ValueError:
            rel = p
        if rel.parts and rel.parts[0].lower() == "core":
            continue
        candidates.append(p)

    candidates.sort(key=lambda p: (len(p.relative_to(root).parts), str(p).lower()))
    log_line(log, "BIN candidates found: %d" % len(candidates))
    for p in candidates:
        try:
            got = sha1_file(p)
        except Exception as e:
            log_line(log, "  SKIP %s :: %r" % (p, e))
            continue
        log_line(log, "  SHA1 %s  %s" % (got, p.name))
        if got == CLEAN_SHA1:
            return p.resolve()
    raise RuntimeError("Exact CLEAN Japan BIN not found; expected SHA1 %s" % CLEAN_SHA1)


def run_logged(cmd, cwd: Path, log, label: str) -> int:
    log_line(log, "")
    log_line(log, "=" * 78)
    log_line(log, label)
    log_line(log, "CMD: " + " ".join('"%s"' % x if " " in x else x for x in cmd))
    log_line(log, "CWD: %s" % cwd)
    log_line(log, "=" * 78)
    cp = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert cp.stdout is not None
    for line in cp.stdout:
        log_line(log, line.rstrip("\r\n"))
    rc = cp.wait()
    log_line(log, "%s RETURN CODE: %d" % (label, rc))
    return rc


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        return _selftest()
    if len(sys.argv) != 2:
        print("Usage: package_driver_06551.py PACKAGE_ROOT")
        return 2

    raw_root = sys.argv[1]
    clean_root = normalize_root_arg(raw_root)
    root = Path(clean_root).expanduser().resolve()
    log_path = root / LOG_NAME
    tools = root / "Core" / "tools"
    builder = tools / BUILDER_NAME

    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        try:
            log_line(log, "GAIA MASTER 0.6.55.1 BATCH45R2 - FAIL-PERSISTENT DRIVER")
            log_line(log, "Python: %s" % sys.executable)
            log_line(log, "Python version: %s" % sys.version.replace("\n", " "))
            log_line(log, "Raw root argv: %r" % raw_root)
            log_line(log, "Normalized package root: %s" % root)
            log_line(log, "Expected CLEAN SHA1: %s" % CLEAN_SHA1)

            if not root.is_dir():
                raise RuntimeError("Package root does not exist: %s" % root)
            if not builder.is_file():
                raise RuntimeError("Builder missing: %s" % builder)

            clean = find_clean(root, log)
            log_line(log, "[OK] CLEAN BIN: %s" % clean)

            rc = run_logged(
                [sys.executable, str(builder), "--selftest"],
                tools,
                log,
                "STATIC SELFTEST",
            )
            if rc:
                raise RuntimeError("Static selftest failed with return code %d" % rc)

            rc = run_logged(
                [sys.executable, str(builder), str(clean)],
                tools,
                log,
                "CLEAN BUILD + R2 FONT PATCH",
            )
            if rc:
                raise RuntimeError("R2 builder failed with return code %d" % rc)

            final_report = clean.parent / "GaiaMaster_0.6.55.1_BATCH45R2_FINAL_REPORT.txt"
            if not final_report.is_file():
                raise RuntimeError("Builder returned 0 but final R2 report is missing: %s" % final_report)

            log_line(log, "")
            log_line(log, "RESULT: BUILD/STAGE PASS")
            log_line(log, "FINAL REPORT: %s" % final_report)
            log_line(log, "RUNTIME SCREENSHOT STILL REQUIRED")
            return 0
        except Exception as e:
            log_line(log, "")
            log_line(log, "RESULT: FAIL")
            log_line(log, "ERROR: %r" % e)
            log_line(log, "TRACEBACK:")
            for line in traceback.format_exc().splitlines():
                log_line(log, line)
            log_line(log, "")
            log_line(log, "SEND THIS FILE BACK: %s" % log_path.name)
            return 9


if __name__ == "__main__":
    raise SystemExit(main())
