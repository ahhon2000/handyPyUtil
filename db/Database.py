from enum import Enum

from ..classes import ClonableClass
from .SmartQuery import SmartQuery
from ..loggers import addStdLogger

from .exceptions import *

class DBTYPES(Enum):
    sqlite = 0
    mysql = 1


class Database(ClonableClass):
    dbtype = None
    PROHIBITED_COL_NAMES = (
        'cast', 'carg', 'ckwarg', 'commit', 'aslist', 'returnCursor',
        'rawExceptions ', 'bindObject',
        'flgDeleted', 'fromRow', 'fromId', 'dbobj',
    )
    NAMED_ARG_AFFIXES = (None, None)

    def __init__(self,
        connect = True,
        debug = False,
        logger = None,
        bindObject = None,
        **conn_kwarg,
    ):
        """Initialise the database interface

        bindObject is the object to bind row instances to (see RowMapper).
        If not given, will be set to this database object.

        conn_kwarg will be passed on to the DB-specific connection function
        """

        dbtype = self.dbtype
        if not isinstance(dbtype, DBTYPES):
            raise Exception(f'illegal dbtype : {dbtype}')

        self.debug = debug
        addStdLogger(self, default=logger)
        self.bindObject = bindObject if bindObject else self

        self.connection = None
        self.conn_kwarg = conn_kwarg

        self.q = self
        self.dbname = ''

        if connect: self.reconnect()

    def close(self):
        self.connection.close()

    def __truediv__(self, x):
        return SmartQuery(self) / x

    def __call__(self, *arg, **kwarg):
        return SmartQuery(self, *arg, **kwarg)()

    def sql(self, *arg, **kwarg):
        return self.execute(*arg, **kwarg)

    def execute(self, r, **qpars):
        """Execute request r with optional arguments args

        The list of the keyword arguments and their defaults are in this
        method's code at the top.

        See RowMapper for a description of how the `cast' argument works.

        Do NOT override this method. Instead, override its callbacks:
            prepareQuery(), execQuery(), fetchRows(), and others
        """

        qpars['request'] = r

        #
        # The method's keyword arguments and their defaults
        #
        args = qpars.get('', None)
        cast = qpars.get('cast', None)
        carg = qpars.get('carg', ())
        ckwarg = qpars.get('ckwarg', {})
        commit = qpars.get('commit', True)
        aslist = qpars.get('aslist', False)
        returnCursor = qpars.get('returnCursor', False)
        rawExceptions = qpars.get('rawExceptions', self.debug)
        bindObject = qpars.get('bindObject', None)

        self.prepareQuery(qpars)

        try:
            self.execQuery(qpars)
        except Exception as e:
            if rawExceptions: raise e
            raise Exception(f"""
{self.dbtype.name} request failed: {e}:
Request:
{r}
Arguments:
{args}
"""[1:-1])

        cursor = qpars.get('cursor')

        from . import RowMapper
        rowMapper = RowMapper(
            dbtype = self.dbtype,
            cast = cast, carg = carg, ckwarg = ckwarg,
            cursor = cursor,
            bindObject = bindObject if bindObject else self.bindObject,
        )

        rows = self.fetchRows(qpars)
        rows = map(rowMapper, rows)
        if aslist: rows = list(rows)

        if commit: self.commitAfterQuery(qpars)

        ret = cursor if returnCursor else rows
        return ret

    def recreateDatabase(self):
        self.dropDatabase()
        self.createDatabase()

    def reconnect(self): raise Exception(f'unimplemented')
    def prepareQuery(self, qpars): pass
    def execQuery(self, qpars): raise Exception('unimplemented')
    def fetchRows(self, qpars): raise Exception('unimplemented')
    def commitAfterQuery(self, qpars): pass
    def getRowById(self): raise Exception('unimplemented')
    def createTable(self, tableRow): raise Exception('unimplemented')
    def createIndices(self, tableRow): raise Exception('unimplemented')
    def saveTableRow(self,tableRow,commit=True):raise Exception('unimplemented')
    def deleteTableRow(self, tableRow, commit=True):raise Exception('unimplemented')
    def createDatabase(self): raise Exception('unimplemented')
    def dropDatabase(self): raise Exception('unimplemented')
