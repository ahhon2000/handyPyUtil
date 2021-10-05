from collections import OrderedDict
import re
import sqlite3
import shutil
from pathlib import Path
from .util import convertPHolders_mysql_to_sqlite

from .Database import DBTYPES
from . import DatabaseSQL
from .PlaceholderGenerator import PlaceholderGenerator

from .exceptions import *


class Database_sqlite(DatabaseSQL):
    dbtype = DBTYPES.sqlite
    MAX_ROWS_PER_FETCH = 100
    H = PlaceholderGenerator('?', ':', '')

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
        r = convertPHolders_mysql_to_sqlite(qpars['request'])

        args = qpars.get('args')
        if args is None: args = ()
        cursor = None

        try:
            qpars['cursor'] = cursor = self.connection.cursor()
        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
            self.raiseDBOperationalError('connection problem', e)

        try:
            cursor.execute(r, args)
        except sqlite3.OperationalError as e:
            self.raiseDBOperationalError('failed to execute the query', e)

    def createDatabase(self):
        self.reconnect()

    def dropDatabase(self):
        path = self.path
        if path: path.unlink(missing_ok=True)

    def extractNamedPlaceholders(self, request):
        request = convertPHolders_mysql_to_sqlite(request)
        ps = OrderedDict()
        for colon, p in re.findall(r'(:)(\w+)\b', request):
            ps.setdefault(p, 0)
            ps[p] += 1

        return ps

    def RowToDictMaker(self, qpars):
        return lambda r: {k: r[k] for k in r.keys()}
