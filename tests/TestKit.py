import re
import sys, os
import random
import time
import shutil
import argparse
from pathlib import Path
from multiprocessing import Process

from handyPyUtil.subproc import Pipe
from handyPyUtil.dates import Date
from handyPyUtil.strings import genRandomStr
from handyPyUtil.loggers import addStdLogger
from handyPyUtil.paths import createTree

from handyPyUtil.imports import importByPath
from .TestKitRegister import TestKitRegister

class TestKit:
    def __init__(self,
        tmpDirParent = Path('/tmp'),
        tmpDirBase = ".handyTest",
        nocleanup=False,
        logger = None,
        **kwarg,
    ):
        addStdLogger(self, default=logger, debug=True)

        self.cmdl = cmdl = self._getCmdLineOpts()

        if not tmpDirParent.exists(): raise Exception(f'{tmpDirParent} does not exist')

        self.tmpDirParent = tmpDirParent
        self.tmpDirBase = tmpDirBase
        self.tmpDir = None

        self.nocleanup = cmdl.nocleanup or nocleanup

        self.processes = {}  # format: pid: process

    def _getCmdLineOpts(self):
        argp = argparse.ArgumentParser()

        argp.add_argument('-n', '--nocleanup', action="store_true", help="do NOT clean up after the test is done")
        argp.add_argument("arguments", nargs='*')

        cmdl = argp.parse_args(sys.argv[1:])
        return cmdl

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
            self.logger.info(f'we have kept the tmp dir: {tmpDir}')
        else:
            self.cleanup()

    def forkProcess(self, target, args=(), kwargs={}, **pkwarg):
        """Fork a process and kill it after the `with' clause

        The process will be added to this object's `processes' dictionary with
        its pid as the key.

        Additional keyword arguments can be given to the Process constructor
        as pkwarg.
        """

        ps = self.processes

        p = Process(target=target, args=args, kwargs=kwargs, **pkwarg)
        ps[p.pid] = p
        p.start()

        return p

    def _cleanupProcesses(self):
        ps = self.processes
        for pid, p in ps.items():
            p.kill()
        ps.clear()

    def cleanup(self, after_nocleanup=False):
        self._cleanupProcesses()

        tmpDir = self.tmpDir
        if tmpDir and tmpDir.exists():
            shutil.rmtree(tmpDir)

    def createTree(self, tree):
        """Create a tree in tmpDir

        See paths.createTree() for the format of the argument.

        NOTE: The argument to this class's createTree() can only contain
        relative paths.
        """

        tmpDir = self.tmpDir
        tree2 = {tmpDir: tree}
        createTree(tree2)
