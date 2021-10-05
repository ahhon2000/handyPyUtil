from collections import OrderedDict
import re
import sqlite3

from .Database import DBTYPES
from . import DatabaseSQL

from .exceptions import ExcRecordNotFound


class Database_mysql(DatabaseSQL):
    # TODO set self.dbname on connection
    dbtype = DBTYPES.mysql
    NAMED_ARG_AFFIXES = (':', '')

    def getRowById(self, tbl, Id):
        q = self.q

        rows = q(Id=Id) / f"SELECT * FROM `{tbl}` WHERE id=:Id"

        if not rows: raise ExcRecordNotFound(f'no record with id={Id}')
        return rows[0]

    def createDatabase(self): pass
    def dropDatabase(self): pass

    def extractNamedPlaceholders(self, request):
        ps = OrderedDict()
        for colon, p in re.findall(r'(:)(\w+)\b', request):
            ps.setdefault(p, 0)
            ps[p] += 1

        return ps

    def RowToDictMaker(self, qpars):
        return lambda r: {k: r[k] for k in r.keys()}
