"""
    USAGE:
        If you have a script that needs to be launched from any directory on
        the file system you can manage its sys.path in the following way:

        1. Place a link to handyPyUtil/cfg.py in the script's directory or
        anywhere in its parent directories. The link filename need not be
        `cfg.py' but it must be the same as in the next step.

        2. Put the following lines at the top of the script:

from pathlib import Path as P; E=P.exists;R=P.resolve; l=R(P(__file__)).parents
with open(R(next(filter(E,(p/'cfg.py' for p in l))))) as _:exec(_.read())

        This will search for the first occurrence of cfg.py from the script's
        directory and above. Once found, cfg.py will be resolved for symlinks
        to detect the location of handyPyUtil.

        The path for locating handyPyUtil will be added to sys.path, along with
        the script's parent directory.

        3. [OPTIONAL] Add paths to sys.path with inclPath(), which at this point
        has been automatically imported by cfg.py:

            inclPath('maintenance/tests', 'core')

        See inclPath()'s comments for its usage and more examples.

        NOTE: Neither cfg.py nor inclPath will add a path to sys.path if it
        is already there.
"""

# TODO replace with hcfg.py

def init():
    from pathlib import Path
    import sys
    import os
    import psutil

    cfgPath = None
    for fh in sorted(
        psutil.Process().open_files(),
        reverse=True, key=lambda fh: fh.fd,
    ):
        f = Path(fh.path).resolve()
        if f.name == 'cfg.py'  and  (f.parent / '.this_is_handy').exists():
            cfgPath, cfgfh = f, fh
            break

    if not cfgPath: raise ImportError(f'cannot locate the Handy cfg file')

    handyPath = cfgPath.parent

    if not next(
        (
            p for p in (
                Path(s).resolve() for s in sys.path
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
