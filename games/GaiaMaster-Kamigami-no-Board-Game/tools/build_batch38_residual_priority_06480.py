#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import build_batch35_residual_priority_06450 as base

VERSION="0.6.48.0"
ROOT=Path(__file__).resolve().parent.parent
TR=ROOT/"translation"
base.VERSION=VERSION
base.B33=TR/"BATCH37_FINAL_EXACT_SET_0.6.47.0.csv"
base.OUT=TR/"BATCH38_RESIDUAL_PRIORITY_0.6.48.0.csv"
base.REPORT=ROOT/"checkpoints"/VERSION/"BATCH38_RESIDUAL_PRIORITY_REPORT.txt"

if __name__=="__main__":
    raise SystemExit(base.main())
