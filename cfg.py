import pathlib
import sys
import os
import psutil

def init():
    cfgPath, cfgfh = None, None
    for fh in sorted(
        psutil.Process().open_files(),
        reverse=True, key=lambda fh: fh.fd,
    ):
        f = pathlib.Path(fh.path).resolve()
        print(f.name)
        if f.name == 'cfg.py'  and  (f.parent / '.this_is_handy').exists():
            cfgPath, cfgfh = f, fh
            break

    if not cfgPath: raise ImportError(f'cannot locate the handy cfg file')

    #os.close(cfgfh.fd)

    handyPath = cfgPath.parent

    if not next(
        (
            p for p in (
                pathlib.Path(s).resolve() for s in sys.path
            ) if p.exists() and p.samefile(handyPath.parent)
        ),
        None,
    ):
        sys.path.append(str(handyPath.parent))

    return handyPath


handyPath = init()
from handyPyUtil.imports import inclPath, HandyCfg

HANDY_CFG = HandyCfg(handyPath)

del init, handyPath
