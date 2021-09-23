"""
    USAGE:
        If you have a script that needs to be launched from any directory on
        the file system you can manage its sys.path in the following way:

        1. Put the following line at the top of the script:

            with open("/path/to/handyPyUtil/cfg.py") as _: exec(_.read())

        This will add the path for locating handyPyUtil to sys.path. The
        script's parent directory will be added, too.

        2. [OPTIONAL] Add paths to sys.path with inclPath(), which has been
        automatically imported by cfg.py:

            inclPath('maintenance/tests', 'core')

        See inclPath()'s comments for its usage and more examples.

        NOTE: Neither cfg.py nor inclPath will add a path to sys.path if it
        is already there.
"""

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

    from handyPyUtil.imports import inclPath, HandyCfg

    # add the script's parent directory to sys.path
    inclPath(Path(sys.argv[0]).resolve().parent, includeProjectRoot=False)

    handCfg = HandyCfg(handyPath)

    return handyPath

HANDY_CFG = init()
del init

from handyPyUtil.imports import inclPath
