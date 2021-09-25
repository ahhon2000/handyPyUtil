import re
import pickle
import time
import shutil

from handyPyUtil.settings import TESTKIT_REGISTER_DIR
from handyPyUtil.strings import genRandomStr

PRESERVED_PREFIX = 'preserved'
PRESERVED_SUFFIX = 'pickle'
PRESERVED_GLOB = f'{PRESERVED_PREFIX}.*.{PRESERVED_SUFFIX}'

class TestKitRegister:
    def __init__(self):
        pass

    def uncleanedIter(self):
        for f in sorted(TESTKIT_REGISTER_DIR.glob(PRESERVED_GLOB)):
            tk = None
            try:
                tk = self.recoverPreserved(f)
            except Exception as e:
                print(f'failed to recover {f}')

            if not tk: continue

            yield tk

    def getPreservedTKFile(self, tk, genRandom=False):
        def fileFromBasename(fnb):
            fnb = re.sub(r'^[.]+', '', fnb)
            fn = f'{PRESERVED_PREFIX}.{fnb}.{PRESERVED_SUFFIX}'
            return TESTKIT_REGISTER_DIR / fn

        TESTKIT_REGISTER_DIR.mkdir(exist_ok=True)

        retf = None
        if genRandom:
            sec = round(time.time())
            rnds = genRandomStr(10)
            retf = fileFromBasename(f'{sec}.{rnds}')
        else:
            if tk.tmpDir:
                retf = fileFromBasename(f'{tk.tmpDir.name}')
            else:
                retf = self.getPreservedTKFile(tk, genRandom=True)

        if retf.exists(): retf = getPreservedTKFile(tk, genRandom=True)

        return retf

    def preserve(self, tk):
        f = self.getPreservedTKFile(tk)
        b = pickle.dumps(tk)

        f.write_bytes(b)

    def recoverPreserved(self, f):
        b = f.read_bytes()
        tk = pickle.loads(b)
        return tk

    def cleanup(self):
        success = True
        for tk in self.uncleanedIter():
            try:
                print(f'cleaning up {tk.tmpDir}')
                tk.cleanup(after_nocleanup=True)
            except Exception as e:
                success = False
                print(f"\tfailed: {e}")

        if success:
            if TESTKIT_REGISTER_DIR.exists():
                shutil.rmtree(TESTKIT_REGISTER_DIR)
