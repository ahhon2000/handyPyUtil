
def init():
    import pathlib
    import sys
    import os
    import psutil

    cfgPath = None
    for fh in sorted(
        psutil.Process().open_files(),
        reverse=True, key=lambda fh: fh.fd,
    ):
        f = pathlib.Path(fh.path).resolve()
        if f.name == 'cfg.py'  and  (f.parent / '.this_is_handy').exists():
            cfgPath, cfgfh = f, fh
            break

    if not cfgPath: raise ImportError(f'cannot locate the Handy cfg file')

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

    from handyPyUtil.imports import HandyCfg

    handCfg = HandyCfg(handyPath)

    return handyPath

HANDY_CFG = init()
del init

from handyPyUtil.imports import inclPath
