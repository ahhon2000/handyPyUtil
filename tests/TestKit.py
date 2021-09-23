import re
import sys
import random
import time
import shutil
from pathlib import Path

from handyPyUtil.subproc import Pipe
from handyPyUtil.dates import Date
from handyPyUtil.strings import genRandomStr

TMP = Path('/tmp')
TMP_DIR_BASE = ".handyTest"

class TestKit:
    def __init__(self,
        nocleanup=False, **kwarg
    ):
        self.nocleanup = nocleanup
        self.tmpDir = None

    def __enter__(self):
        dt = Date("now").toText()
        sec = round(time.time())
        rnds = genRandomStr(10)

        tmpDir = TMP / Path(f'{TMP_DIR_BASE}.{sec}.{rnds}')
        self.tmpDir = tmpDir 

        tmpDir.mkdir(parents=True)
        if not tmpDir.exists(): raise Exception(f'{tmpDir} does not exist')

        return self

    def __exit__(self, Type, value, tb):
        tmpDir = self.tmpDir
        if self.nocleanup:
            print(f'we have kept the tmp dir: {tmpDir}')
        else:
            if tmpDir.exists(): shutil.rmtree(tmpDir)

    def cleanup(self):
        for d in (
            f for f in TMP.iterdir()
                if f.is_dir() and TMP_DIR_BASE == f.name[0:len(TMP_DIR_BASE)]
        ):
            print(f'removing {d}')
            shutil.rmtree(d)
