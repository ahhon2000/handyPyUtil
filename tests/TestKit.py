import sys
import random
import time
import shutil
from pathlib import Path

from handyPyUtil.subproc import Pipe
from handyPyUtil.dates import Date
from handyPyUtil.strings import genRandomStr


class TestKitBase:
    def __init__(self,
        tmpFileBase = "",
        nocleanup=False, **kwarg
    ):
        if not tmpFileBase: raise Exception('tmpFileBase is missing')
        self.tmpFileBase = tmpFileBase
        self.nocleanup = nocleanup

        tmpFileBase = tmpFileBase
        dt = Date("now").toText()
        sec = round(time.time())
        rnds = genRandomStr(10)

        tmpDir = Path(f'/tmp/{tmpFileBase}.{sec}.{rnds}')
        self.tmpDir = tmpDir 

        tmpDir.mkdir(parents=True)
        if not tmpDir.exists(): raise Exception(f'{tmpDir} does not exist')

        self._changeConfigPaths()

    def __enter__(self):
        return self

    def __exit__(self, Type, value, tb):
        tmpDir = self.tmpDir
        if self.nocleanup:
            print(f'we have kept the tmp dir: {tmpDir}')
        else:
            if tmpDir.exists(): shutil.rmtree(tmpDir)
