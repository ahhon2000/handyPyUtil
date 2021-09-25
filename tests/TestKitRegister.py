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


    def preserve(self, tk):
        b = pickle.dumps(tk)

        fn = None
        if tk.tmpDir:
            fn = f'{tk.tmpDir.name}'
        else:
            sec = round(time.time())
            rnds = genRandomStr(10)
            fn = f'{sec}.{rnds}'

        fn = re.sub(r'^[.]+', '', fn)
        fn = f'{PRESERVED_PREFIX}.{fn}.{PRESERVED_SUFFIX}'

        TESTKIT_REGISTER_DIR.mkdir(exist_ok=True)

        f = TESTKIT_REGISTER_DIR / fn
        if f.exists(): raise Exception(f'{f} exists')

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
            shutil.rmtree(TESTKIT_REGISTER_DIR)
