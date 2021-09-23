import sys, os
from pathlib import Path
from itertools import chain
import inspect

PROJECT_ROOT_PLACEHOLDER = '.project_root'

def inclPath(*dirs, includeProjectRoot=True):
    """Add each directory in dirs to sys.path, unless it is already there.

    An element in dirs can be either an absolute path or a path relative to
    the project root. It can be given either as a string or a Path instance.

    The project root is the nearest upper-level directory, relative to
    the inclPath() caller's file, found to contain a placeholder file
    `.project_root'.

    The project root is only searched for if dirs contains relative paths or
    if includeProjectRoot is True.

    If includeProjectRoot is True the project root will be added to sys.path
    as well.

    This function will also make sure that the script's parent directory
    (i. e. sys.argv[0]) is on sys.path.

    *** USAGE ***
    
    1. If you have a script intended to be launched from any directory on the
    file system and you want to conveniently add the paths for that script's
    dependencies to sys.path put the following line at top of the script:

        with open("/path/to/handyPyUtil/cfg.py") as _: exec(_.read())

    This will automatically import inclPath() and allow for including
    paths relative to the script's parent directory.

    2. In any case, you can always import inclPath normally:

        from handyPyUtil.imports import inclPath

    3. Examples:

        inclPath('maintenance')
        inclPath('core', 'core/tests')
        inclPath('core')
        inclPath('mypackage', includeProjectRoot=False)
        inclPath()    # this will just add the project root to sys.path

    """

    ps = list(map(Path, dirs))

    needProjectRoot = includeProjectRoot
    for p in ps:
        if not p.exists(): raise ImportError(f'directory {p} does not exist')
        if not p.is_dir(): raise ImportError(f'file {p} is not a directory')

        if not p.is_absolute(): needProjectRoot = True

    projectRoot = None
    if needProjectRoot:
        frames = inspect.stack()
        callerFile = None
        for i, frame in enumerate(frames):
            if frame.function == 'inclPath':
                callerFile = Path(frames[i+1].filename).resolve()
                break

        if not callerFile: raise Exception(f'could not determine the caller file')

        d = callerFile.parent
        while d != d.parent:
            if (d / PROJECT_ROOT_PLACEHOLDER).exists():
                projectRoot = d
                break
            d = d.parent
        if not projectRoot: raise Exception('Could not find the project root directory. Either mark it with a .project_root placeholder file or call inclPath() with includeProjectRoot=False')

    existingPaths = set(str(Path(s).resolve()) for s in sys.path)
    pathsToAdd = {}  # format:  path_string: order_int

    def addPathIfNew(p):
        s = str(p)
        if s not in pathsToAdd  and  s not in existingPaths:
            pathsToAdd[s] = len(pathsToAdd)

    # add the script's parent
    addPathIfNew(Path(sys.argv[0]).resolve().parent)

    # add the project root
    if includeProjectRoot: addPathIfNew(projectRoot)

    # add unique paths from dirs
    for p in ps:
        if not p.is_absolute(): p = (projectRoot / p).resolve()
        s = str(p)
        addPathIfNew(s)

    
    # extend sys.path with pathsToAdd
    ss = [
        s for s, i in sorted(
            pathsToAdd.items(),
            key = lambda it: it[1],
        )
    ]

    sys.path.extend(ss)


def importClassesFromPackage(packageInitFile):
    """Import classes from `class files'

    A `class file' is a *.py file such that its name starts with a capital
    letter and it contains a class of the same name.

    NOTE: This function does not itself import anything, it returns a script
    instead that should passed on to exec in the package's namespace.

    USAGE: In the package's __init__.py:
        exec(importClassesFromPackage(__file__))

    """

    ls = []
    for f in Path(packageInitFile).resolve().parent.iterdir():
        if f.suffix != '.py': continue
        if not f.is_file()  or  not f.stem[0].isupper(): continue
        modname = f.stem

        ls.append(f"from . import {modname} as tmpmod")
        ls.append(f"""
if hasattr(tmpmod, '{modname}'):
    from .{modname} import {modname}
"""[1:-1])

    scr = "\n".join(ls)

    return scr
