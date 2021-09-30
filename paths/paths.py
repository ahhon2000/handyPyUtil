from collections import namedtuple
from pathlib import Path

class TreeDictError(Exception): pass

TreeNode = namedtuple('TreeNode', (
    'path', 'fullpath', 'contents', 'parentNode',
))

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

        if not isinstance(n.contents, (set, dict, str, bytes)): raise TreeDictError(f'the value of a tree entry can only be a dict or a str, not {type(n.contents)}')

    def onDir(n):
        pass

    def onFile(n):
        if not isinstance(n.contents, (str, bytes)): raise TreeDictError(f'the contents of {n.fullpath} is neither a str nor bytes')

    traverseTree(tree, onPath=onPath, onNode=onNode, onDir=onDir, onFile=onFile)


def createTree(tree):
    """Create a directory structure described by set/dictionary `tree'

    Each entry in argument `tree' is a path if tree is a set, or a path-contents
    pair if it is a dict. Contents can be another tree set/dictionary or
    a str/bytes instance representing a file's contents. For example:

        tree = {
            '/tmp/dir': {
                'media': {'photos', 'videos'},
                'subdir': {
                    'memoirs.txt': 'I was born in...',
                },
            },
        }

    This structure of the `tree' argument orders to create directory
    /tmp/dir and subdirectories /tmp/dir/media, /tmp/dir/subdir.
    The latter will contain a file named `memoirs.txt' with the specified
    contents in it. Directory /tmp/dir/media will contain emptie directories
    photos, videos.

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
        p.makedir(exist_ok=True)

    def onFile(n):
        p = n.fullpath
        if isinstance(c, str): p.write_text(c)
        else: p.write_bytes(c)

    traverseTree(tree, onNode=onNode, onDir=onDir, onFile=onFile)
