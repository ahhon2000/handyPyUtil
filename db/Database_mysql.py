import MySQLdb

from .Database import DBTYPES
from . import DatabaseSQL
from .exceptions import *

class Database_mysql(DatabaseSQL):
    dbtype = DBTYPES.mysql
    NAMED_ARG_AFFIXES = ('%(', ')s')

    def reconnect(self):
        conn_kwarg = self.conn_kwarg
        conn = MySQLdb.Connect(**conn_kwarg)

        self.connection = conn

        r = self(0) / "SELECT DATABASE() as n"
        self.dbname = r['n']

    def execQuery(self, qpars):
        r = qpars['request']
        args = qpars.get('args')
        cursor = qpars['cursor']
        cursor.execute(r, args=args)
        
    def fetchRows(self, qpars):
        # use fetchall() instead of fetchone() here because requesting
        # rows one by one might cause latency
        cursor = qpars.get('cursor')
        return cursor.fetchall()

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
