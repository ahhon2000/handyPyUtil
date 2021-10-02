from enum import Enum

from . import SmartQuery
from ..loggers import addStdLogger

class DBTYPES(Enum):
    sqlite = 0
    mysql = 1

class Database:
    def __init__(self,
        dbtype = None,
        debug = False,
        logger = None,
        bindObject = None,  # object to bind row instances to (see RowMapper)
        **conn_kwarg,
    ):
        if not isinstance(dbtype, DBTYPES):
            raise Exception(f'illegal dbtype : {dbtype}')

        self.dbtype = dbtype
        self.debug = debug
        addStdLogger(self, default=logger)
        self.bindObject = bindObject

        self.connection = None
        self.conn_kwarg = conn_kwarg

    def execute(self, q, args=None):
        raise Exception('unimplemented method')

    def __truediv__(self, x):
        return SmartQuery(self) / x

    def __call__(self, *arg, **kwarg):
        return SmartQuery(self, *arg, **kwarg).execute()

    def sql(self, *arg, **kwarg):
        return self.execute(*arg, **kwarg)

    def execute(self, q, **kwarg):
        """Execute request r with optional arguments t

        See RowMapper for a description of how the `cast' argument works.
        The list of the keyword arguments and their defaults is at the top
        of this method's code.

        Do NOT override this method. Instead, override its callbacks:
            prepareQuery(), execQuery(), fetchRows()
        """

        kwarg.update({'q': q, 'args': args})

        #
        # The method's keyword arguments and their defaults
        #
        cast = kwarg.get('cast', None)
        carg = kwarg.get('carg', ())
        ckwarg = kwarg.get('ckwarg', {})
        commit = kwarg.get('commit', True)
        aslist = kwarg.get('aslist', False)
        returnCursor = kwarg.get('returnCursor', False)
        rawExceptions = kwarg.get('rawExceptions', False)
        bindObject = kwarg.get('bindObject', None)

        self.prepareQuery(kwarg)

        try:
            self.execQuery(kwarg)
        except Exception as e:
            if rawExceptions: raise e
            raise Exception(f"""
{self.dbtype.name} request failed: {e}:
Request:
{q}
Arguments:
{args}
"""[1:-1])

        cursor = kwarg.get('cursor')

        rowMapper = RowMapper(
            dbtype = self.dbtype,
            cast = cast, carg = carg, ckwarg = ckwarg,
            cursor = cursor,
            bindObject = bindObject if bindObject else self.bindObject,
        )

        rows = self.fetchRows(kwarg)
        rows = map(rowMapper, rows)
        if aslist: rows = list(rows)

        if self.dbtype in (DBTYPES.sqlite, DBTYPES.mysql):
            # commit if this is a retrieval request, unless we are told not to
            if cursor.description is None  and  commit:
                conn.commit()

        ret = cursor if returnCursor else rows
        return ret

    def prepareQuery(self, qpars):
        if self.dbtype in (DBTYPES.sqlite, DBTYPES.mysql):
            qpars['cursor'] = self.connection.cursor()
        else: raise Exception(f'unsupported DB type')

    def execQuery(self, qpars): pass
    def fetchRows(self, qpars): return ()
