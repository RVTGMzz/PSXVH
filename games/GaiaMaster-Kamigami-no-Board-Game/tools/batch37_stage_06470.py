#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import batch29_stage_06390 as base
ROOT=Path(__file__).resolve().parent.parent
TR=ROOT/"translation"
TARGETS=TR/"BATCH37_NEW_EXACT_OFFSET_0.6.47.0.csv"
FINAL=TR/"BATCH37_FINAL_EXACT_SET_0.6.47.0.csv"
base.TARGETS=TARGETS
base.FINAL=FINAL

def build_plan():return base.build_plan()
@contextmanager
def staged_sources(plan=None):
    plan=plan or build_plan()
    with base.staged_sources(plan):yield plan
if __name__=="__main__":
    plan=build_plan()
    with staged_sources(plan):pass
    c=plan["counts"]
    print("BATCH37 PRODUCTION STAGING SELFTEST PASS")
    print(f"targets={c['targets']}")
    print(f"final_verify={c['final_verify']}")
    print(f"legacy={c['legacy']}/397")
    print(f"shadows={c['shadows']}")
    print(f"sinks={c['sinks']}")
    print(f"gameplay_mask={c['gameplay_mask']}")
    print(f"compact13_mask={c['compact13_mask']}")
    print(f"compact14_mask={c['compact14_mask']}")
    print(f"preserve={c['preserve']}")
    print("source_restore=PASS")
