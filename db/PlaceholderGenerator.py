
class PlaceholderGenerator:
    """A way to generate substitution placeholders for SQL requests

    If H is PlaceholderGenerator(positional, prefix, suffix) then H behaves
    as follows:

    str(H)               returns the string  positional
    H.some_parameter     returns the string  prefix + 'some_parameter' + suffix
    H('some_parameter')  returns the string  prefix + 'some_parameter' + suffix

    For example:
        H = PlaceholderGenerator('%s', '%(', ')s')

        f"SELECT {H}"             # produces "SELECT %s"
        f"SELECT {H.username}"    # produces "SELECT %s(username)s"
        colname = 'email'
        f"SELECT {H(colname)}"    # produces "SELECT %s(email)s"
    """

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
