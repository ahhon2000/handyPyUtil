
class PlaceholderGenerator:
    def __init__(self, positional, prefix, suffix):
        self._positional = positional
        self._prefix = prefix
        self._suffix = suffix

    def _enclose(self, a):
        return f'{self._prefix}{a}{self._suffix}'

    def __str__(self):
        return self._positional

    def __getattr__(self, a):
        if a[0] == '_':
            return self.__getattribute__(a)

        p = self._enclose(a)
        return p

    def __call__(self, a):
        return self._enclose(a)
