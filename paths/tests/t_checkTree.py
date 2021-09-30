#!/usr/bin/python3
from pathlib import Path
cfgDir = Path(__file__).resolve().parent.parent.parent
cfgFile = cfgDir/ 'cfg.py'
with open(str(cfgFile)) as O: exec(O.read())

from handyPyUtil.paths import checkTree, TreeDictError


def doTest(case):
    tree = case['tree']
    mustFail = case.get('mustFail', False)

    if mustFail:
        failed = False
        try:
            checkTree(tree)
        except TreeDictError:
            failed = True

        assert failed
    else:
        checkTree(tree)


cases = [
    {
        'tree': {},
    }, {
        'tree': {'/tmp'},
    }, {
        'tree': {'tmp'},
        'mustFail': True,
    }, {
        'tree': {
            '/tmp/dir': {
                'media': {'photos', 'videos'},
                'subdir': {
                    'memoirs.txt': 'I was born in...',
                },
            },
        },
    }, {
        'tree': 1,
        'mustFail': True,
    }, {
        'tree': None,
        'mustFail': True,
    }, {
        'tree': {None: {}},
        'mustFail': True,
    }, {
        'tree': {
            '/tmp/dir': {
                'media': {'photos', 'videos'},
                'subdir': {
                    3: 'I was born in...',
                },
            },
        },
        'mustFail': True,
    }, {
        'tree': {'/tmp/': {'file.txt': 35}},
        'mustFail': True,
    }, {
        'tree': {'/tmp/': {Path('/home'): {}}},
        'mustFail': True,
    }, {
        'tree': {'/tmp/': {Path('/home'): dict()}},
        'mustFail': True,
    }, {
        'tree': {'tmp': {'dir'}},
        'mustFail': True,
    }, {
        'tree': {
            '/tmp/dir': {
                'media': {'photos', 'videos'},
                'subdir': {
                    Path('memoirs.txt'): 'I was born in...',
                },
            },
        },
    }, {
        'tree': {
            '/tmp/dir': {
                'media': {'photos', 'videos'},
                'subdir': {
                    Path('subsubdir/memoirs.txt'): 'I was born in...',
                },
            },
        },
    }, {
        'tree': {
            Path('/tmp/dir'): {
                'media': {'photos', 'videos'},
                'subdir': {
                    Path('subsubdir/memoirs.txt'): 'I was born in...',
                },
            },
        },
    }, {
        'tree': {
            Path('/tmp/dir/'): {
                'diary.lnk': Path('/home/user/diary'),
            },
        }
    }, {
        'tree': {
            Path('/tmp/dir/'): {
                'diary.lnk': Path('home/user/diary'),
            },
        },
    }, {
        'tree': {
            '/tmp/dir/': {
                'subdir': {
                    'notes.txt': "Once upon a time...",
                    'diary': Path('/home/user/diary'),
                },
            },
        }
    },
]

if __name__ == '__main__':
    for case in cases: doTest(case)
