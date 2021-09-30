"""
    USAGE:
        If you have a script that needs to be launched from any directory on
        the file system you can manage its sys.path in the following way:

        1. Place a link to handyPyUtil/cfg.py in the script's directory or
        anywhere in its parent directories. The link filename need not be
        `cfg.py' but it must be the same as in the next step.

        2. Copy the contents of handyPyUtil/boilerplate_for_scripts and
        place it at the top of the script. It's just a few lines.

        These lines will first attempt to import handyPyUtil normally, in case
        Python already knows where to look for handyPyUtil (e. g., from the
        PYTHONPATH environment variable). On failure, a search will be
        performed for the first occurrence of cfg.py, starting from the
        script's directory and above. Once found, cfg.py will be resolved for
        symlinks to detect the location of handyPyUtil and import it.

        The script's parent directory will be added to sys.path, unless it is
        already there.

        3. [OPTIONAL] Add paths to sys.path with inclPath(), which at this point
        has been automatically imported by the boilerplate code from
        the previous step:

            inclPath('maintenance/tests', 'core')

        See inclPath()'s comments for its usage and more examples.

        NOTE: Neither cfg.py nor inclPath() will add a path to sys.path if it
        is already there.
"""

def init():
    from pathlib import Path
    import sys
    import os
    import importlib.util

    cfgPath = Path(O.name).resolve()
    if cfgPath.name != 'cfg.py': raise Exception(f"the symlink does not lead to handyPyUtil's cfg.py; path={cfgPath}")
    if not (cfgPath.parent / '.this_is_handy').exists(): raise Exception(f"the symlink does not lead to handyPyUtil")

    handyPath = cfgPath.parent

    # import handy
    spec = importlib.util.spec_from_file_location(
        'handyPyUtil', str(handyPath / '__init__.py'),
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)

    from handyPyUtil.imports import inclPath, HandyCfg

    # add the script's parent directory to sys.path
    ipr = inclPath(Path(sys.argv[0]).resolve().parent,
        iProjectRoot=False, iProjectRootParent=False,
    )

    # If cfg.py is executed in a script set the script's __package__ variable
    # to the scripts parent packages, like so:
    #
    #   top_package.package_level1.package_level2.....script_parent_package
    #
    # This facilitates relative imports, which otherwise don't work in scripts
    if __name__ == '__main__':
        global __package__
        __package__ = ipr.get('specName')

    handCfg = HandyCfg(handyPath)

    return handyPath

HANDY_CFG = init()
del init

from handyPyUtil.imports import inclPath
