import re
import MySQLdb
from collections import OrderedDict

from .Database import DBTYPES
from . import DatabaseSQL
from .PlaceholderGenerator import PlaceholderGenerator
from . import TriggerManager_mysql

from .exceptions import *
from handyPyUtil.loggers.convenience import fmtExc

class Database_mysql(DatabaseSQL):
    dbtype = DBTYPES.mysql
    H = PlaceholderGenerator('%s', '%(', ')s')

    def __init__(self, *arg, **kwarg):
        kwarg.setdefault('TrgMgrCls', TriggerManager_mysql)
        super().__init__(*arg, **kwarg)

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
        except MySQLdb.OperationalError:
            self.raiseDBConnectionError(f'could not get a cursor', e)

        try:
            cursor.execute(r, args=args)
        except MySQLdb.OperationalError as e:
            self.raiseDBOperationalError(f'failed to execute the query', e)
            raise DBOperationalError(msg)

    def createDatabase(self):
        self(commit=False, notriggers=True) / f"""
            CREATE DATABASE IF NOT EXISTS
            `{self.dbname}` DEFAULT CHARSET utf8
        """,
        self(commit=False, notriggers=True) / f"""
            USE `{self.dbname}`
        """,

    def dropDatabase(self):
        self(commit=False, notriggers=True) / f"""
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
