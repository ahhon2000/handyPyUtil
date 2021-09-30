from collections import namedtuple
from pathlib import Path

class TreeDictError(Exception): pass

TreeNode = namedtuple('TreeNode', (
    'path', 'fullpath', 'contents', 'parentNode',
))

def dirIsEmpty(d):
    "Return True iff directory d is empty"

    d = Path(d)
    if not d.exists(): raise Exception(f'{d} does not exist')
    if not d.is_dir(): raise Exception(f'{d} is not a directory')

    return not bool(next(d.iterdir(), None))

def traverseTree(tree, parentNode=None,
    onPath=None, onNode=None, onDir=None, onFile=None
):
    treeItems = ((p,{}) for p in tree) if isinstance(tree,set) else tree.items()

    for p, c in treeItems:
        if onPath: onPath(p)
        p = Path(p)
        fp = parentNode.fullpath / p if parentNode else p

        n = TreeNode(p, fp, c, parentNode)

        if onNode: onNode(n)

        isDir = isinstance(c, (set, dict))
        if isDir:
            if onDir: onDir(n)
            traverseTree(c,
                parentNode = n,
                onPath=onPath, onNode=onNode, onDir=onDir, onFile=onFile,
            )
        else:
            if onFile: onFile(n)


def checkTree(tree):
    if not isinstance(tree, (set, dict)):
        raise TreeDictError(f"the `tree' argument is neither a dict nor a set; type={type(tree)}")

    def onPath(p):
        if not isinstance(p, (Path, str)): raise TreeDictError(f'an instance of {type(p)} cannot be a path')

    def onNode(n):
        if n.parentNode:
            if n.path.is_absolute(): raise TreeDictError(f"absolute paths are not allowed in subnodes: {n.path}")
        else:
            if not n.path.is_absolute(): raise TreeDictError(f"relative top-level paths are not allowed")

        if not isinstance(n.contents, (set, dict, str, bytes, Path)): raise TreeDictError(f'the contents part of a tree entry cannot be of type {type(n.contents)}')

    def onDir(n):
        pass

    def onFile(n):
        if not isinstance(n.contents, (str, bytes, Path)): raise TreeDictError(f'the contents of {n.fullpath} cannot be of type {type(n.contents)}')

    traverseTree(tree, onPath=onPath, onNode=onNode, onDir=onDir, onFile=onFile)


def createTree(tree):
    """Create a directory structure described by set/dictionary `tree'

    Each entry in argument `tree' is a path p if tree is a set, or a
    path-contents pair p: c if it is a dict.

    Contents c can be another tree set/dictionary or
    a str/bytes instance representing a file's contents. If contents is a Path
    instance t then a symlink at path p will be created
    pointing to t:  p -> t. The target path t can be relative or absolute.

    For example:

        tree = {
            '/tmp/dir': {
                'media': {'photos', 'videos'},
                'subdir': {
                    'memoirs.txt': 'I was born in...',
                    'a_symlink': Path('/abs/path/to/something/'),
                },
            },
        }

    This structure of the `tree' argument orders to create directory
    /tmp/dir and subdirectories /tmp/dir/media, /tmp/dir/subdir.

    Directory /tmp/dir/media will contain empty directories
    photos, videos.

    /tmp/dir/subdir will contain a file named `memoirs.txt' with the specified
    contents in it. Also, a symlink to /abs/path/to/something/ will be created
    in /tmp/dir/subdir.

    Paths can be strings or Path objects.

    Top-level paths must be absolute. Each lower-level path must be relative to
    its parent node in tree. E. g.,:

        tree = {
            '/tmp/dir': {
                'subdir1': {},
                'subdir2/subsubdir': {
                    'treasure': {}
                },
            }
        }

    In this example, both subdir1 and subdir2 are in /tmp/dir and subsubdir is
    in subdir2. The empty directory `treasure' is in
    /tmp/dir/subdir2/subsubdir/
    """

    checkTree(tree)

    def onNode(n):
        p = n.fullpath
        p.parent.mkdir(exist_ok=True, parents=True)

    def onDir(n):
        p = n.fullpath
        p.mkdir(exist_ok=True)

    def onFile(n):
        p = n.fullpath
        c = n.contents
        if isinstance(c, str): p.write_text(c)
        elif isinstance(c, bytes): p.write_bytes(c)
        elif isinstance(c, Path):
            t = c if c.is_absolute() else p.parent / c
            if p.is_symlink():
                tt = p.readlink()
                if tt != t:
                    raise TreeDictError(f'Symlink {p} already exists and points to {tt}, not to {t}. Cannot overwrite it')
            elif p.exists():
                raise TreeDictError(f'{p} already exists but it is not a symlink')
            else:
                p.symlink_to(t)

        else: raise TreeDictError('unexpected type of tree node contents: {c}')

    traverseTree(tree, onNode=onNode, onDir=onDir, onFile=onFile)
