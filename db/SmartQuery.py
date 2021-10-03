from more_itertools import nth

from .Database import Database

class SmartQuery:
    INTERNAL_ATTR_TYPES = {
        'db': (Database,),
        'request': (str, bytes),
        'index': (int, slice),
    }

    def __init__(self, *arg, **kwarg):
        self._internals = {
            'db': None, 'request': None, 'index': None,
        }

        self._positionalValues = []
        self._kwarg = {}

        self._consumeArg(arg, kwarg)

    def _consumeArg(self, arg, kwarg):
        from . import Database

        for i, a in enumerate(arg):
            processed_a = False
            for k, ts in self.INTERNAL_ATTR_TYPES.items():
                if isinstance(a, ts):
                    self._setInternal(k, a)
                    processed_a = True
                    break

            if not processed_a:
                if isinstance(a, SmartQuery):
                    for k, v in a._internals.items():
                        if v is not None:
                            self._setInternal(k, v)
                    self._extendPositionalValues(a._positionalValues)
                    self._kwarg.update(a._kwarg)
                elif isinstance(a, dict):
                    self._kwarg.update(a)
                elif isinstance(a, (tuple, list, set)):
                    self._extendPositionalValues(a)
                else: raise Exception(f'unsupported type of positional argument {i}: {type(a)}')

        self._kwarg.update(kwarg)

    def _setInternal(self, k, v):
        ints = self._internals
        v0 = ints.get(k)
        if v0 is not None  and  not isinstance(v0, Database):
            raise Exception(f'the SmartQuery internal attribute "{k}" was set more than once')

        ints[k] = v

    def _appendPositionalValue(self, v):
        self._positionalValues.append(v)

    def _extendPositionalValues(self, vs):
        for v in vs:
            self._appendPositionalValue(v)

    def _execute(self):
        ints = self._internals
        db, r, index = ints['db'], ints['request'], ints['index']

        if r is None: return self

        positionalValues = self._positionalValues
        namedValues, qpars = self._extract_from_kwarg()
        if positionalValues and namedValues: raise Exception(f'positional and named values cannot be used together')

        args = None
        if positionalValues:
            args = tuple(positionalValues)
        if namedValues:
            args = namedValues
        
        ret = db.execute(r, args=args, **qpars)
        if index is None: return ret
        return nth(ret, index)

    def _extract_from_kwarg(self):
        namedValues = {}
        qpars = {}

        r = self._internals.get('request')
        if r is None: raise Exception(f'no request string')
        db = self._internals['db']

        placeholders = set(db.extractNamedPlaceholders(r))

        for k, v in self._kwarg.items():
            if k in placeholders:
                namedValues[k] = v
            else:
                qpars[k] = v

        return namedValues, qpars

    def __call__(self, *arg, **kwarg):
        self._consumeArg(arg, kwarg)
        return self._execute()

    def __truediv__(self, x):
        self._consumeArg((x,), {})
        return self._execute()

    def __mul__(self, x):
        self._appendPositionalValue(x)
        return self
