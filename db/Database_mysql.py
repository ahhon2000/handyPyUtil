import MySQLdb

from .Database import DBTYPES
from . import Database

class Database_mysql(Database):
    def __init__(self,
        connect = True,
        **kwarg,  # may contain connection keyword arguments
    ):
        super().__init__(dbtype=DBTYPES.mysql, **kwarg)
        if connect: self.reconnect()

    def reconnect(self):
        conn_kwarg = self.conn_kwarg
        conn = MySQLdb.Connect(**conn_kwarg)

        self.connection = conn

    def connect(self, *arg, **kwarg):
        return self.reconnect(*arg, **kwarg):

    def execQuery(self, qpars):
        q = qpars['q']
        args = qpars['args']
        cursor = qpars['cursor']
        cursor.execute(q, args=args)
        
    def fetchRows(self, qpars):
        # use fetchall() instead of fetchone() here because requesting
        # rows one by one might cause latency
        return cursor.fetchall()
