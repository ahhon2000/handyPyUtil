import time
from enum import Enum
from more_itertools import islice_extended

from ..classes import ClonableClass
from ..loggers import addStdLogger
from ..loggers.convenience import fmtExc

from .exceptions import *

from handyPyUtil.iterators import applySubscript

class DBTYPES(Enum):
    sqlite = 0
    mysql = 1

class Database(ClonableClass):
    dbtype = None
    MAX_RECONNECTION_ATTEMPTS = 3
    H = None   # placeholder generator

    def __init__(self,
        connect = True,
        debug = False,
        logger = None,
        bindObject = None,
        RowMapperMaker = None,
        TrgMgrCls = None,
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

        if not RowMapperMaker:
            from . import RowMapper
            RowMapperMaker = RowMapper
        self.RowMapperMaker = RowMapperMaker

        if not TrgMgrCls:
            from . import TriggerManager
            TrgMgrCls = TriggerManager
        self.triggerManager = trgMgr = TrgMgrCls(self)

        # TODO make sure execute() is called from the same thread as __init__()

        if connect: self.reconnect()

    def close(self):
        self.connection.close()

    def __truediv__(self, x):
        from .SmartQuery import SmartQuery
        return SmartQuery(self) / x

    def __mul__(self, x):
        from .SmartQuery import SmartQuery
        return SmartQuery(self) * x

    def __getitem__(self, x):
        from .SmartQuery import SmartQuery
        return SmartQuery(self)[x]

    def __call__(self, *arg, **kwarg):
        from .SmartQuery import SmartQuery
        return SmartQuery(self, *arg, **kwarg)()

    def sql(self, *arg, **kwarg):
        "A synonym for execute()"
        return self.execute(*arg, **kwarg)

    def execute(self, request,
        args = None,
        cast = None,
        carg = (),
        ckwarg = None,  # defaults to an empty dict
        cmpst_cast = (),
        cmpst_carg = (),
        cmpst_ckwarg = (),
        commit = True,
        aslist = False,
        returnCursor = False,
        RowMapperMaker = None,
        RowToDictMaker = None,
        subscript = None,
        bindObject = None,     # Database.RowMapperMaker by default
    ):
        """Execute a DB request with optional arguments args

        args, if given, can be a sequence or a dictionary. It should contain
        values to substitute for placeholders in request.

        See RowMapper for a description of how the `cast' argument works and
        what bindObject is.

        You can supply a different RowMapperMaker than the default one
        (RowMapper).

        The `subscript' argument can be a row index or slice. It will be
        passed on to the methods of database-specific subsclasses in order
        to retrieve a subset of rows.

        RowToDictMaker is a function that creates a function to convert
        retrieved raw rows to dictionaries.
        The default maker should be defined in subclasses. If not, a trivial
        function returning the raw row itself will be used.

        Do NOT override this method. Instead, override its callbacks:
            execQuery(), fetchRows(), and others
        """

        ckwarg = ckwarg if ckwarg else {}

        if not RowToDictMaker: RowToDictMaker = self.RowToDictMaker
        bindObject = bindObject if bindObject else self.bindObject

        # The values of variables set before this line will be copied to qpars
        qpars = {vn: v for vn, v in locals().items()}

        trgMgr = self.triggerManager
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
                raise self._rollbackOnExc(qpars, excIn=e, excOut=ExcExecQuery)

            if success: break

        if not success:
            raise self._rollbackOnExc(qpars, excOut=ExcExecQuery)

        try: trgMgr.catchBeforeCommit(qpars)
        except Exception as e:
            raise self._rollbackOnExc(qpars, excIn=e, excOut=ExcTrgBeforeCommit)

        if commit:
            try: self.commitAfterQuery(qpars)
            except Exception as e:
                raise self._rollbackOnExc(qpars, excIn=e, excOut=ExcCommit)

        try: trgMgr.catchAfterCommit(qpars)
        except Exception as e:
            raise self._rollbackOnExc(qpars, excIn=e, excOut=ExcTrgAfterCommit)

        # Prepare the value to be returned

        cursor = qpars.get('cursor')
        ret = None

        if returnCursor:
            ret = cursor
        else:
            if not RowMapperMaker: RowMapperMaker = self.RowMapperMaker
            rowMapper = RowMapperMaker(qpars)

            rows = applySubscript(
                self.fetchRows(qpars), subscript,
                intSubscrReturnsElem = False,
            )
            rows = map(rowMapper, rows)

            if isinstance(subscript, int): ret = next(rows)
            elif aslist: ret = list(rows)
            else: ret = rows

        return ret

    def _rollbackOnExc(self, qpars, excIn=None, excOut=None):
        "Roll back the current transaction after exception e. Return e"

        e = excOut(self,exc=excIn, request=qpars['request'], args=qpars['args'])
        self.logger.error(str(e))

        self.rollback()

        return e

    def commit(self):
        "Perform an explicit commit. Useful after an execute(commit=False) call"

        self.connection.commit()

    def recreateDatabase(self):
        self.dropDatabase()
        self.createDatabase()

    def raiseDBOperationalError(self, msg0, e):
        msg = msg0
        msg += ': ' + fmtExc(e, inclTraceback=self.debug)
        self.logger.warning(msg)

        raise DBOperationalError(msg)

    """
    
      *** Methods to Override in Subclasses ***
    
    Request-related methods exchange parameters by means of the `qpars'
    dictionary initially filled out by execute()
    """

    def reconnect(self): raise NotImplementedError()
    def execQuery(self, qpars): raise NotImplementedError()
    def fetchRows(self, qpars): raise NotImplementedError()
    def commitAfterQuery(self, qpars): pass
    def rollback(self, qpars): self.connection.rollback()
    def getRowById(self): raise NotImplementedError()
    def createTable(self, tableRow): raise NotImplementedError()
    def createIndices(self, tableRow): raise NotImplementedError()
    def saveTableRow(self, tableRow, commit=True):raise NotImplementedError()
    def deleteTableRow(self, tableRow, commit=True):raise NotImplementedError()
    def createDatabase(self): raise NotImplementedError()
    def dropDatabase(self): raise NotImplementedError()
    def extractNamedPlaceholders(self, request): raise NotImplementedError()
    def RowToDictMaker(self, qpars): return lambda row: row
