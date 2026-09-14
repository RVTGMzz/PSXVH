#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaia Master 0.6.28.0 - Batch 19 report compiler V2 safety wrapper.

V2 disables automatic consensus promotion keyed only by vi_game_current.
Reason: the legacy fallback is accentless and can be semantically ambiguous
(e.g. NHAN may represent nhận / nhẫn / nhân). Japanese-keyed consensus and
curated STYLE mappings remain enabled.

The underlying report/output format remains identical to V1.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE / "gaia_batch19_report_compiler_06280.py"


def load_v1():
    spec = importlib.util.spec_from_file_location("gaia_batch19_report_v1", V1)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {V1}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = load_v1()
    original_build_candidates = mod.build_candidates

    def build_candidates_safe(row, semantic, style, consensus_jp, consensus_fallback):
        # Deliberately pass an empty fallback-consensus map. This preserves the
        # proven Japanese consensus + curated STYLE paths while preventing
        # accentless fallback collisions from inventing a wrong Vietnamese meaning.
        return original_build_candidates(row, semantic, style, consensus_jp, {})

    mod.build_candidates = build_candidates_safe
    print("[SAFETY V2] Accentless fallback consensus promotion: DISABLED")
    print("[SAFETY V2] Japanese consensus + curated STYLE mappings: ENABLED")
    return mod.main()


if __name__ == "__main__":
    raise SystemExit(main())
