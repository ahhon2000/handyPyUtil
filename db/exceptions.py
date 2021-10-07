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
            msg += """

Request:
{request}
Arguments:
{args}
"""[1:-1]

        super().__init__(msg)

class ExcExecQuery(ExcExecute):
    DFLT_MSG = 'execQuery() failed'

class ExcTrgBeforeCommit(ExcExecute):
    DFLT_MSG = 'catchBeforeCommit() failed'

class ExcCommit(ExcExecute):
    DFLT_MSG = 'commitAfterQuery() failed'

class ExcTrgAfterCommit(ExcExecute):
    DFLT_MSG = 'catchAfterCommit() failed'
