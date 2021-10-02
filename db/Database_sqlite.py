import sqlite3

from .Database import DBTYPES
from . import DatabaseSQL

from .exceptions import ExcRecordNotFound

class Database_mysql(DatabaseSQL):
    NAMED_ARG_AFFIXES = (':', '')

    def __init__(self,
        connect = True,
        **kwarg,  # may contain connection keyword arguments
    ):
        super().__init__(dbtype=DBTYPES.mysql, **kwarg)
        if connect: self.reconnect()

    def getRowById(self, tbl, Id):
        q = self.q

        rows = q(Id=Id) / f"SELECT * FROM `{tbl}` WHERE id=:Id"

        if not rows: raise ExcRecordNotFound(f'no record with id={Id}')
        return rows[0]
