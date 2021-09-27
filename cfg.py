"""
    USAGE:
        If you have a script that needs to be launched from any directory on
        the file system you can manage its sys.path in the following way:

        1. Place a link to handyPyUtil/cfg.py in the script's directory or
        anywhere in its parent directories. The link filename need not be
        `cfg.py' but it must be the same as in the next step.

        2. Copy the contents of handyPyUtil/boilerplate_for_scripts and
        place it at the top of the script. It's just a few lines.

        First, they will attempt to import handyPyUtil normally, in case
        Python already knows where to look for handyPyUtil (e. g. from the
        environment). On failure, a search will be performed for
        the first occurrence of cfg.py, starting from the script's directory
        and above. Once found, cfg.py will be resolved for symlinks to detect
        the location of handyPyUtil. The path for locating handyPyUtil will be
        added to sys.path, along with the script's parent directory.

        3. [OPTIONAL] Add paths to sys.path with inclPath(), which at this point
        has been automatically imported by the boilerplate code from
        the previous step:

            inclPath('maintenance/tests', 'core')

        See inclPath()'s comments for its usage and more examples.

        NOTE: Neither cfg.py nor inclPath will add a path to sys.path if it
        is already there.
"""

def init():
    from pathlib import Path
    import sys
    import os

    cfgPath = Path(O.name).resolve()
    if cfgPath.name != 'cfg.py': raise Exception(f"the symlink does not lead to handyPyUtil's cfg.py; path={cfgPath}")
    if not (cfgPath.parent / '.this_is_handy').exists(): raise Exception(f"the symlink does not lead to handyPyUtil")

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
    inclPath(Path(sys.argv[0]).resolve().parent,
        iProjectRoot=False, iProjectRootParent=False,
    )

    handCfg = HandyCfg(handyPath)

    return handyPath

HANDY_CFG = init()
del init

from handyPyUtil.imports import inclPath
