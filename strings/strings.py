import random

_DFLT_ALPHABET = [
    chr(ord(b) + i)
        for b, n in (('a', 26), ('A', 26), ('0', 10),)
            for i in range(n)
]

def genRandomStr(k, alphabet=_DFLT_ALPHABET):
    s = ''.join(
        random.choices(alphabet, k=k)
    )

    return s
