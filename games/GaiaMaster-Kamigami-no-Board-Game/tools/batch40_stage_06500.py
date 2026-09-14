#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import batch29_stage_06390 as base
ROOT=Path(__file__).resolve().parent.parent;TR=ROOT/"translation"
TARGETS=TR/"BATCH40_NEW_EXACT_OFFSET_0.6.50.0.csv";FINAL=TR/"BATCH40_FINAL_EXACT_SET_0.6.50.0.csv"
base.TARGETS=TARGETS;base.FINAL=FINAL

def build_plan():return base.build_plan()
@contextmanager
def staged_sources(plan=None):
    plan=plan or build_plan()
    with base.staged_sources(plan):yield plan
if __name__=="__main__":
    plan=build_plan()
    with staged_sources(plan):pass
    c=plan["counts"]
    print("BATCH40 PRODUCTION STAGING SELFTEST PASS")
    for k in ("targets","final_verify","shadows","sinks","gameplay_mask","compact13_mask","compact14_mask","preserve","legacy"):
        print(f"{k}={c[k]}")
    print("source_restore=PASS")
