from enum import Enum

from ..classes import ClonableClass
from ..loggers import addStdLogger

from .exceptions import *

class DBTYPES(Enum):
    sqlite = 0
    mysql = 1


class Database(ClonableClass):
    dbtype = None
    NAMED_ARG_AFFIXES = (None, None)
    MAX_RECONNECTION_ATTEMPTS = 3

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
        from .SmartQuery import SmartQuery
        return SmartQuery(self) / x

    def __mul__(self, x):
        from .SmartQuery import SmartQuery
        return SmartQuery(self) * x

    def __call__(self, *arg, **kwarg):
        from .SmartQuery import SmartQuery
        return SmartQuery(self, *arg, **kwarg)()

    def sql(self, *arg, **kwarg):
        return self.execute(*arg, **kwarg)

    def execute(self, request,
        args = None,
        cast = None,
        carg = (),
        ckwarg = None,  # defaults to an empty dict
        commit = True,
        aslist = False,
        returnCursor = False,
        rawExceptions = None,  # defaults to self.debug if not given
        bindObject = None,
    ):
        """Execute a DB request with optional arguments args

        args, if given, can be a sequence or a dictionary. It should contain
        values for substitution for placeholders in request.

        See RowMapper for a description of how the `cast' argument works.

        Do NOT override this method. Instead, override its callbacks:
            execQuery(), fetchRows(), and others
        """

        ckwarg = ckwarg if ckwarg else {}
        if rawExceptions is None: rawExceptions = self.debug
        qpars = {vn: v for vn, v in locals().items()}

        r = request
        success = False
        for attempt in range(0, self.MAX_RECONNECTION_ATTEMPTS + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"reconnection attempt #{attempt}")
                    self.reconnect()

                self.execQuery(qpars)
                success = True
            except DBOperationalError:
                self.logger.warning(f'connection failure')
            except Exception as e:
                if rawExceptions: raise e
                raise Exception(f"""
{self.dbtype.name} request failed: {e}:
Request:
{r}
Arguments:
{args}
"""[1:-1])
            if success: break
        if not success:
            raise Exception(f'failed to execute the query')

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
    def extractNamedPlaceholders(self, request): raise Exception('unimplemented')
