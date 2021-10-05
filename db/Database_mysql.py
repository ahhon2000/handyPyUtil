import re
import MySQLdb
from collections import OrderedDict

from .Database import DBTYPES
from . import DatabaseSQL
from .exceptions import *
from handyPyUtil.loggers.convenience import fmtExc

class Database_mysql(DatabaseSQL):
    dbtype = DBTYPES.mysql
    NAMED_ARG_AFFIXES = ('%(', ')s')

    def reconnect(self):
        conn_kwarg = self.conn_kwarg
        conn = MySQLdb.Connect(**conn_kwarg)

        self.connection = conn

        r = self[0] / "SELECT DATABASE() as n"
        self.dbname = r['n']

    def execQuery(self, qpars):
        r = qpars['request']
        args = qpars.get('args')

        try:
            qpars['cursor'] = cursor = self.connection.cursor()
            cursor.execute(r, args=args)
        except MySQLdb.OperationalError as e:
            msg = fmtExc(e, inclTraceback=self.debug)
            msg = f'failed to execute the query: {msg}'
            self.logger.warning(msg)
            raise DBOperationalError(msg)

    def createDatabase(self):
        self(commit=False) / f"""
            CREATE DATABASE IF NOT EXISTS
            `{self.dbname}` DEFAULT CHARSET utf8
        """,
        self(commit=False) / f"""
            USE `{self.dbname}`
        """,

    def dropDatabase(self):
        self(commit=False) / f"""
            DROP DATABASE IF EXISTS
            `{self.dbname}`
        """

    def extractNamedPlaceholders(self, request):
        ps = OrderedDict()
        for perc, p in re.findall(r'(%+)\((\w+)\)s', request):
            if len(perc) % 2:
                ps.setdefault(p, 0)
                ps[p] += 1

        return ps

    def RowToDictMaker(self, qpars):
        cursor = qpars.get('cursor')
        return lambda r, cursor=cursor: dict(
            zip(
                (f[0] for f in cursor.description),
                r,
            )
        )
