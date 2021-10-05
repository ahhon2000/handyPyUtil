from collections import OrderedDict
import re
import sqlite3
import shutil
from pathlib import Path

from .Database import DBTYPES
from . import DatabaseSQL

from .exceptions import *


class Database_sqlite(DatabaseSQL):
    dbtype = DBTYPES.sqlite
    NAMED_ARG_AFFIXES = (':', '')
    MAX_ROWS_PER_FETCH = 100

    def __init__(self, *arg, **kwarg):
        path = kwarg.pop('path', None)
        if not path: raise Exception(f'cannot work with an Sqlite DB without a path')
        self.path = path = Path(path)
        self.dburi = f'file:{path}'

        dbname = re.sub(r'\..*', '', path.name)
        if not dbname: raise Exception(f'illegal DB name: {dbname}')
        self.dbname = dbname

        super().__init__(*arg, **kwarg)

    def reconnect(self):
        conn_kwarg = self.conn_kwarg
        conn = sqlite3.Connection(self.dburi, uri=True, **conn_kwarg)
        self.connection = conn

        conn.row_factory = sqlite3.Row

    def execQuery(self, qpars):
        r = qpars['request']
        args = qpars.get('args')

        try:
            qpars['cursor'] = cursor = self.connection.cursor()
            cursor.execute(r, args)
        except sqlite3.OperationalError as e:
            msg = fmtExc(e, inclTraceback=self.debug)
            msg = f'failed to execute the query: {msg}'
            self.logger.warning(msg)
            raise DBOperationalError(msg)

    def createDatabase(self):
        self.reconnect()

    def dropDatabase(self):
        path = self.path
        if path: path.unlink(missing_ok=True)

    def extractNamedPlaceholders(self, request):
        ps = OrderedDict()
        for colon, p in re.findall(r'(:)(\w+)\b', request):
            ps.setdefault(p, 0)
            ps[p] += 1

        return ps

    def RowToDictMaker(self, qpars):
        return lambda r: {k: r[k] for k in r.keys()}
