from functools import reduce
from itertools import chain
import time

from .TableRow import TableRow

def RowMapper(qpars):
    """Create a function for mapping db rows returned by fetch* methods

    The function returned is meant to be used internally in Database.execute()
    which should apply it to each retrieved row.

    If no cast function is provided the rows will be cast to type dict.

    It is possible to specify either a single convertor function (with the
    `cast' parameter) or a composition of functions (with `cmst_cast').

        *** SINGLE FUNCTION ***

    If cast is given then each retrieved row r will be cast
    as follows:

        - if carg is a tuple or list:
            cast(*carg, r, **ckwarg)

        - otherwise carg will be treated as the first argument to cast():
            cast(carg, r, **ckwarg)

        - if cast is a descendant of the TableRow class then each row will be
        passed on to the cast function as the keyword argument `_fromRow' and
        the constructor will receive bindObject as the first argument:

            cast(bindObject, *carg, _fromRow=r, **ckwarg)  # carg is tuple/list
            cast(bindObject, carg, _fromRow=r, **ckwarg)   # carg is smth else

    Note that execute() is supposed to know which object to bind
    TableRow instances to.

        *** COMPOSITION OF FUNCTIONS ***

    A sequence of one or more functions can be given as the cmpst_cast argument.
    In this case, they will be applied in reverse order, i. e.
    from right to left. The `cast' function (which defaults to dict) will be
    called on the row prior to cmpst_cast.

    The positional and keyword arguments to the i-th function in cmpst_cast
    must be the i-th elements in cmpst_carg and cmpst_ckwarg, respectively.
    
    The typing and application rules for each function in the composition
    sequence are the same as for a single function (see above).

    Examples:

        execute("some query", cast=TableRow)
        # Convert each row r to TableRow(bindObject, _fromRow=r)

        execute("some query", cast=print, carg=("Row:",))
        # Call  print("Row:", r) for each row r

        execute("some query", cast=TableRowChild, carg=14)
        # Convert each row r to TableRowChild(bindObject, 14, _fromRow=r)

        execute("some query",
            cmpst_cast =  (f,         TableRow,  g),
            cmpst_carg  = ((),        (),       ()),
            cmpst_kwarg = ({'x': 10}, {},       {}),
        )
        # Convert each row r to
        #    f(TableRow(bindObject, _fromRow=g(r)), x=10)
    """

    cast = qpars.get('cast', None)
    carg = qpars.get('carg', ())
    ckwarg = qpars.get('ckwarg', {})
    cmpst_cast = qpars.get('cmpst_cast', ())
    cmpst_carg = qpars.get('cmpst_carg', ())
    cmpst_ckwarg = qpars.get('cmpst_ckwarg', ())
    RowToDictMaker = qpars.get('RowToDictMaker', None)
    bindObject = qpars.get('bindObject', None)

    if not isinstance(carg, (tuple, list)): carg = (carg,)

    funcsAndTheirArgs=[] # each el. is ((f1,arg1,kwarg1), (f2,arg2,kwarg2), ...)
    if cast:
        funcsAndTheirArgs.append(((cast, carg, ckwarg),))
    if cmpst_cast:
        nf = len(cmpst_cast)
        if nf != len(cmpst_carg): raise Exception(f'the number of composite functions != the number of their positional arguments')
        if nf != len(cmpst_ckwarg): raise Exception(f'the number of composite functions != the number of their keyword arguments')

        funcsAndTheirArgs.append(
            reversed(list(
                zip(cmpst_cast, cmpst_carg, cmpst_ckwarg)
            ))
        )

    rowToDict = RowToDictMaker(qpars)
    #gs = [lambda r: rowToDict(r)]
    gs = [rowToDict]
    for f, arg, kwarg in chain(*funcsAndTheirArgs):
        g = None
        if isinstance(f, type) and issubclass(f, TableRow):
            g = lambda r, bindObject=bindObject, f=f, arg=arg, kwarg=kwarg: \
                f(bindObject, *arg, _fromRow = r, **kwarg)
        else:
            g = lambda r, f=f, arg=arg, kwarg=kwarg: f(*arg, r, **kwarg)
        gs.append(g)

    rowMapper = lambda r, gs=gs: reduce(lambda rr, g: g(rr), gs, r)
    return rowMapper
