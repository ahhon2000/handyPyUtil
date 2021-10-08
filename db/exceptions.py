from ..loggers.convenience import fmtExc

class ExcRecordNotFound(Exception): pass
class DBOperationalError(Exception): pass

class ExcExecute(Exception):
    DFLT_MSG = 'request failed'
    def __init__(self, dbobj, exc=None, request='', args=(), msg=''):
        msg = msg if msg else self.DFLT_MSG
        excMsg = fmtExc(exc, inclTraceback=dbobj.debug) if exc else 'unknown error'
        msg = f"{dbobj.dbtype.name}: {msg}: {excMsg}"

        if dbobj.debug:
            msg += f"""

Request:
{request}
Arguments:
{args}
"""[1:-1]

        super().__init__(msg)

class ExcExecQuery(ExcExecute):
    DFLT_MSG = 'execQuery() failed'

class ExcCommit(ExcExecute):
    DFLT_MSG = 'commitAfterQuery() failed'

class ExcTrgCatch(ExcExecute):
    DFLT_MSG = 'failed while catching trigger events'

class ExcTrgPrepare(ExcExecute):
    DFLT_MSG = 'failed while preparing triggers for a query'
