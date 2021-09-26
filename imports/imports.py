import sys, os
from pathlib import Path
from itertools import chain
import traceback

PROJECT_ROOT_PLACEHOLDER = '.project_root'

def inclPath(*dirs,
    iProjectRoot = True,
    iProjectRootParent = False,
    checkDirExistence = True,
):
    """Add each directory in dirs to sys.path, unless it is already there.

    An element in dirs can be either an absolute path or a path relative to
    the project root. It can be given either as a string or a Path instance.

    The project root is the nearest upper-level directory, relative to
    the inclPath() caller's file, found to contain a placeholder file
    `.project_root'.

    The project root is only searched for if dirs contains relative paths, or
    if at least one of iProjectRoot, iProjectRootParent is True.

    If iProjectRoot is True the project root will be added to sys.path
    as well. The same goes for iProjectRootParent

    This function will also make sure that the script's parent directory
    (i. e. sys.argv[0]) is on sys.path.

    *** USAGE ***
    
    1. If you have a script intended to be launched from any directory on the
    file system and you want to conveniently add the paths for that script's
    dependencies to sys.path you need to put a couple of lines of code at
    the top of your script. Follow the steps described in the comments in
    cfg.py.

    `Sourcing' cfg.py in that manner will automatically import inclPath(),
    which allows for including paths relative to the project root.

    Even without any calls to inclPath(), cfg.py will extend sys.path with
    the path for locating handyPyUtil and the script's parent directory.

    2. You can always import inclPath normally:

        from handyPyUtil.imports import inclPath

    3. Examples:

        inclPath('maintenance')
        inclPath('core', 'core/tests')
        inclPath('core')
        inclPath('mypackage', iProjectRoot=False)
        inclPath() # this will just include the project root and its parent

    """

    ps = list(map(Path, dirs))

    needProjectRoot = iProjectRoot or iProjectRootParent
    for p in ps:
        if not p.is_absolute(): needProjectRoot = True

    projectRoot = None
    if needProjectRoot:
        frames = list(reversed(traceback.extract_stack()))
        frameInd0 = None
        for i, frame in enumerate(frames):
            if frame.name == 'inclPath':
                frameInd0 = i + 1
                break
        if frameInd0 is None: raise Exception('could not detect the caller frame')

        for i in range(frameInd0, len(frames)):
            frame = frames[i]
            callerFile = Path(frame.filename).resolve()

            d = callerFile.parent
            while d != d.parent:
                if (d / PROJECT_ROOT_PLACEHOLDER).exists():
                    projectRoot = d
                    break
                d = d.parent

            if projectRoot: break

        if not projectRoot: raise Exception('Could not find the project root directory. Either mark it with a .project_root placeholder file or call inclPath() with iProjectRoot=False')

    existingPaths = set(str(Path(s).resolve()) for s in sys.path)
    pathsToAdd = {}  # format:  path_string: order_int

    def addPathIfNew(p):
        s = str(p)
        if s not in pathsToAdd  and  s not in existingPaths:
            pathsToAdd[s] = len(pathsToAdd)

    # add the script's parent
    addPathIfNew(Path(sys.argv[0]).resolve().parent)

    # add the project root
    if iProjectRoot: addPathIfNew(projectRoot)
    if iProjectRootParent: addPathIfNew(projectRoot.parent)

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

    if checkDirExistence:
        for s in ss:
            p = Path(s)
            if not p.exists(): raise ImportError(f'directory {p} does not exist')
            if not p.is_dir(): raise ImportError(f'file {p} is not a directory')

    sys.path.extend(ss)


def importClassesFromPackage(packageInitFile):
    """Import classes from `class files'

    A `class file' is a *.py file such that its name starts with a capital
    letter and it contains a class of the same name.

    NOTE: This function does not itself import anything, it returns a script
    instead that should be passed on to exec in the package's namespace.

    USAGE: In the package's __init__.py:

        from handyPyUtil.imports import importClassesFromPackage
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
