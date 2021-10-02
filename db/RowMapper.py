from .Database import DBTYPES
from . import TableRow

def RowMapper(
    dbtype = None,
    cast = None, carg = (), ckwarg = {},
    cursor = None,
    bindObject = None,
):
    """Create a function for mapping db rows returned by fetch* methods

    The function returned is meant to be used internally in Database.execute()
    which should apply it to each retrieved row.

    If cast is None the rows will be cast to type dict.

    If cast is given then each retrieved row r will be cast as follows:
        - if carg is a tuple or list:
            cast(*carg, r, **ckwarg)

        - otherwise carg will be treated as the first argument to cast():
            cast(carg, r, **ckwarg)

        - if cast is a descendant of the TableRow class then each row will be
        passed on to the cast function as the keyword argument `fromRow' and
        the constructor will receive bindObject as the first argument:

            cast(bindObject, *carg, fromRow=r, **ckwarg)  # carg is tuple/list
            cast(bindObject, carg, fromRow=r, **ckwarg)   # carg is smth else

    Note that execute() is supposed to know which object to bind
    TableRow instances to.

    Examples:

        execute("some query", cast=TableRow)
        # Convert each row r to TableRow(bindObject, fromRow=r)

        execute("some query", cast=print, carg=("Row:",))
        # Call  print("Row:", r) for each row r

        execute("some query", cast=TableRowChild, carg=14)
        # Convert each row r to TableRowChild(bindObject, 14, fromRow=r)
    """

    if not isinstance(carg, (tuple, list)): carg = (carg,)

    rowToDict = None
    if dbtype == DBTYPES.sqlite:
        rowToDict = lambda r: {k: r[k] for k in r.keys()}
    elif dbtype == DBTYPES.mysql:
        rowToDict = lambda r: dict(
            zip(
                (f[0] for f in cursor.description()),
                r,
            )
        )
    else: raise Exception(f'unsupported database type: {dbtype}')

    rowMapper = rowToDict
    if cast:
        if isinstance(cast, type) and issubclass(cast, TableRow):
            rowMapper = lambda r: cast(bindObject, *carg,
                fromRow = rowToDict(r),
                **ckwarg
            )
        else:
            rowMapper = lambda r: cast(*carg, rowToDict(r), **ckwarg)

    return rowMapper
