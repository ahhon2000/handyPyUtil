from .Database import DBTYPES
from . import TableRow

class TriggerExchTbl(TableRow):
    _tableName = 'trigger_manager_exchange'
    _columnDefs = {
        'id': {
            DBTYPES.sqlite: "INTEGER NOT NULL PRIMARY KEY",
            DBTYPES.mysql: "INTEGER UNSIGNED NOT NULL PRIMARY KEY",
        },
        'table_name': {
            DBTYPES.sqlite: "TEXT NOT NULL",
            DBTYPES.mysql: "VARCHAR(128) NOT NULL",
        },
        'timing': {
            DBTYPES.sqlite: "TEXT NOT NULL",
            DBTYPES.mysql: "VARCHAR(16) NOT NULL",
        },
        'event': {
            DBTYPES.sqlite: "TEXT NOT NULL",
            DBTYPES.mysql: "VARCHAR(16) NOT NULL",
        },
        'data': {
            DBTYPES.sqlite: "TEXT NOT NULL",
            DBTYPES.mysql: "LONGTEXT NOT NULL",
        },
    }

    @classmethod
    def _clear(Cls, q):
        q(notriggers=True, commit=False) / f"""
            DELETE FROM `{Cls._tableName}`
        """

    @classmethod
    def _getOrderedRawRows(Cls, q):
        rs = q(notriggers=True) / f"""
            SELECT * FROM `{Cls._tableName}`
            ORDER BY `id`
        """

        return rs

    @classmethod
    def _create(Cls, q):
        q.createTable(Cls)
