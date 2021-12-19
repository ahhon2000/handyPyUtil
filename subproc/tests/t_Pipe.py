#!/usr/bin/python3
try:from pathlib import Path as P;R=P.resolve;E=P.exists; F = R(P(__file__));\
    L = lambda p: p / 'cfg.py'; from handyPyUtil import A; exec(A)
except: O=open(R(next(filter(E,map(L,F.parents))))); exec(O.read()); O.close()

import sys

from handyPyUtil.subproc import Pipe


for printOutput in (False, True):
    p = Pipe(['ls', '/oeiejfoeijoijf898ij'], printOutput=True)
    assert p.status == 2
    assert not p.stdout
    assert p.stderr
