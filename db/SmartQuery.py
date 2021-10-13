from itertools import chain
from more_itertools import nth, islice_extended
from collections.abc import Iterable

from .Database import Database
from handyPyUtil.iterators import applySubscript

class SmartQuery:
    INTERNAL_ATTR_TYPES = {
        'db': (Database,),
        'request': (str, bytes),
    }

    def __init__(self, *arg, **kwarg):
        self._internals = {
            'db': None, 'request': None,
        }

        self._positionalValues = []
        self._subscripts = []
        self.kwarg = {}

        self._consumeArg(arg, kwarg)

    def _consumeArg(self, arg, kwarg):
        from . import Database

        for i, a in enumerate(arg):
            processed_a = False
            for k, ts in self.INTERNAL_ATTR_TYPES.items():
                if isinstance(a, ts):
                    self.setInternal(k, a)
                    processed_a = True
                    break

            if not processed_a:
                if isinstance(a, SmartQuery):
                    for k, v in a._internals.items():
                        if v is not None:
                            self.setInternal(k, v)
                    self._extendPositionalValues(a._positionalValues)
                    self._extendSubscripts(a._subscripts)
                    self._update_kwarg(a.kwarg)
                elif isinstance(a, dict):
                    self._update_kwarg(a)
                elif isinstance(a, (tuple, list, set)):
                    self._extendPositionalValues(a)
                elif callable(a):
                    self._addFuncToCmpst(a)
                else: raise Exception(f'unsupported type of positional argument {i}: {type(a)}')

        self._update_kwarg(kwarg)

    def _extendSubscripts(self, ss):
        self._subscripts.extend(ss)

    def _update_kwarg(self, dic):
        kwarg = self.kwarg
        cmpst_cast = dic.get('cmpst_cast')

        for k, v in dic.items():
            if k in ('cmpst_cast', 'cmpst_carg', 'cmpst_ckwarg'):
                kwarg[k] = list(chain(kwarg.get(k, []), v))
            elif k == 'subscript':
                self._extendSubscripts((v,))
            else:
                kwarg[k] = v

        # fill cmpst_carg, cmpst_ckwarg, if missing
        if cmpst_cast is not None:
            cmpst_carg = dic.get('cmpst_carg')
            cmpst_ckwarg = dic.get('cmpst_ckwarg')
            if cmpst_carg is None:
                kwarg['cmpst_carg'] = list(kwarg.get('cmpst_carg', ())) + [
                    () for i in range(len(cmpst_cast))
                ]
            if cmpst_ckwarg is None:
                kwarg['cmpst_ckwarg'] = list(kwarg.get('cmpst_ckwarg', ())) + [
                    {} for i in range(len(cmpst_cast))
                ]

    def getInternal(self, k):
        return self._internals[k]

    def setInternal(self, k, v, previouslySetOk=False):
        ints = self._internals
        v0 = ints.get(k)
        if not previouslySetOk:
            if v0 is not None and not isinstance(v0, Database):
                raise Exception(f'the SmartQuery internal attribute "{k}" was set more than once')

        ints[k] = v

    def _appendPositionalValue(self, v):
        self._positionalValues.append(v)

    def _extendPositionalValues(self, vs):
        for v in vs:
            self._appendPositionalValue(v)

    def tryToExecute(self):
        ints = self._internals
        db, r = ints['db'], ints['request']

        if r is None: return self

        positionalValues = self._positionalValues
        namedValues, qpars = self._extract_from_kwarg()
        if positionalValues and namedValues: raise Exception(f'positional and named values cannot be used together')

        args = None
        if positionalValues:
            args = tuple(positionalValues)
        if namedValues:
            args = namedValues

        subscripts = self._subscripts
        if subscripts:
            qpars['subscript'] = subscripts[0]
        
        ret = db.execute(r, args=args, **qpars)

        for i in range(1, len(subscripts)):
            s = subscripts[i]
            if isinstance(s, (int, slice)) and \
                isinstance(ret, Iterable) and \
                    not isinstance(ret, (list, tuple, str, bytes)):

                ret = applySubscript(ret, s)
            else:
                ret = ret[s]
        return ret

    def _extract_from_kwarg(self):
        namedValues = {}
        qpars = {}

        r = self._internals.get('request')
        if r is None: raise Exception(f'no request string')
        db = self._internals['db']

        placeholders = set(db.extractNamedPlaceholders(r))

        for k, v in self.kwarg.items():
            if k in placeholders:
                namedValues[k] = v
            else:
                qpars[k] = v

        return namedValues, qpars

    def _addFuncToCmpst(self, f):
        kwarg = self.kwarg
        for k in ('cmpst_cast', 'cmpst_carg', 'cmpst_ckwarg'):
            kwarg.setdefault(k, [])

        kwarg['cmpst_cast'] = list(chain(kwarg.get('cmpst_cast', ()), (f,)))
        kwarg['cmpst_carg'] = list(chain(kwarg.get('cmpst_carg', ()), ((),)))
        kwarg['cmpst_ckwarg'] = list(chain(kwarg.get('cmpst_ckwarg', ()), ({},)))

    def __call__(self, *arg, **kwarg):
        self._consumeArg(arg, kwarg)
        return self.tryToExecute()

    def __truediv__(self, x):
        self._consumeArg((x,), {})
        return self.tryToExecute()

    def __mul__(self, x):
        self._appendPositionalValue(x)
        return self

    def __getitem__(self, subscript):
        self._extendSubscripts((subscript,))
        return self.tryToExecute()
