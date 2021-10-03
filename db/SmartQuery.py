class SmartQuery:
    def __init__(self, *arg, **qpars):
        self._consumeArg(arg, qpars)

    def _consumeArg(self, arg, qpars):
        from . import Database

        self.db, self.request, self.index = None, None, None
        self.qpars = {}

        for i, a in enumerate(arg):
            if isinstance(a, Database):
                if self.db is not None: raise Exception(f'the db paramater was set more than once')
                self.db = a
            elif isinstance(a, (str, bytes)):
                if self.request is not None: raise Exception(f'the request was set more than once')
                self.request = a
            elif isinstance(a, int): 
                if self.index is not None: raise Exception(f'the index parameter was set more than once')
                self.index = a
            if isinstance(a, SmartQuery):
                arg2 = tuple(
                    a2 for a2 in (a.db, a.request, a.index) if a is not None
                )
                self._consumeArg(arg2, a.qpars)
            elif isinstance(a, dict):
                self.qpars.update(a)
            else: raise Exception(f'unsupported type of positional argument {i}: {type(a)}')

        self.qpars.update(qpars)

    def _execute(self):
        db, r, qpars, index = self.db, self.request, self.qpars, self.index

        if r is None: return self

        ret = db.execute(r, **qpars)
        if index is None: return ret
        return ret[index]

    def __call__(self, *arg, **qpars):
        return self._execute()

    def __truediv__(self, x):
        self._consumeArg((x,), {})
        return self._execute()
