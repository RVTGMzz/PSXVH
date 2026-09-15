#!/usr/bin/env python3
# -*- coding: ascii -*-
from __future__ import annotations

import package_driver_06551 as core

# IMPORTANT: Do not put BATCH4 or BATCH5 in this diagnostic filename.
# Historical builder 0.6.14 renames changed files containing BATCH4 -> BATCH5.
# The persistent log is open while that builder runs, so a BATCH4 substring
# makes Windows attempt to rename an open file and raises PermissionError 13.
LOG_NAME = "BUILD_LOG_0.6.55.1_R2.txt"


def _log_name_gate() -> None:
    upper = LOG_NAME.upper()
    if "BATCH4" in upper or "BATCH5" in upper:
        raise RuntimeError("Persistent log name collides with historical Batch4/5 rename rule")

    # Exact historical 0.6.14 rename transform must leave this name untouched.
    transformed = (
        LOG_NAME
        .replace("0.6.13.0", "0.6.14.0")
        .replace("06130", "06140")
        .replace("BATCH4", "BATCH5")
    )
    if transformed != LOG_NAME:
        raise RuntimeError("Persistent log name is not rename-safe: %r -> %r" % (LOG_NAME, transformed))


def main() -> int:
    _log_name_gate()
    core.LOG_NAME = LOG_NAME
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
