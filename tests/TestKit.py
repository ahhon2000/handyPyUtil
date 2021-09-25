import re
import sys
import random
import time
import shutil
from pathlib import Path

from handyPyUtil.subproc import Pipe
from handyPyUtil.dates import Date
from handyPyUtil.strings import genRandomStr
from .TestKitRegister import TestKitRegister

class TestKit:
    def __init__(self,
        tmpDirParent = Path('/tmp'),
        tmpDirBase = ".handyTest",
        nocleanup=False,
        **kwarg,
    ):
        if not tmpDirParent.exists(): raise Exception(f'{tmpDirParent} does not exist')

        self.tmpDirParent = tmpDirParent
        self.tmpDirBase = tmpDirBase
        self.nocleanup = nocleanup
        self.tmpDir = None

    def __enter__(self):
        dt = Date("now").toText()
        sec = round(time.time())
        rnds = genRandomStr(10)

        tmpDirBase = self.tmpDirBase

        tmpDir = self.tmpDirParent / Path(f'{tmpDirBase}.{sec}.{rnds}')
        self.tmpDir = tmpDir 

        if tmpDir.exists(): raise Exception(f'{tmpDir} already exists')
        tmpDir.mkdir(parents=True)
        if not tmpDir.exists(): raise Exception(f'{tmpDir} does not exist')

        return self

    def __exit__(self, Type, value, tb):
        tmpDir = self.tmpDir
        if self.nocleanup:
            tkr = TestKitRegister()
            tkr.preserve(self)
            print(f'we have kept the tmp dir: {tmpDir}')
        else:
            if tmpDir.exists(): shutil.rmtree(tmpDir)

    def cleanup(self, after_nocleanup=False):
        tmpDir = self.tmpDir
        if tmpDir and tmpDir.exists():
            shutil.rmtree(tmpDir)
