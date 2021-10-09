from .Database import Database, DBTYPES
from . import TriggerManagerSQL
from .exceptions import *


class DatabaseSQL(Database):
    MAX_ROWS_PER_FETCH = 1000

    def __init__(self, *arg, **kwarg):
        if self.dbtype not in (DBTYPES.sqlite, DBTYPES.mysql):
            raise Exception(f'DatabaseSQL does not support dbtype={dbtype}')
        kwarg.setdefault('TrgMgrCls', TriggerManagerSQL)
        super().__init__(*arg, **kwarg)

    def commitAfterQuery(self, qpars):
        # commit if this is a retrieval request,
        cursor = qpars.get('cursor')
        if cursor.description is None:
            self.connection.commit()

    def getRowByColVal(self, tbl, col, val):
        q = self.q
        rows = q(aslist=True, val=val)/ f"""
            SELECT * FROM `{tbl}` WHERE `{col}`=%(val)s
            LIMIT 1
        """

        if not rows: raise ExcRecordNotFound(f'no record with {col}={val}')
        return rows[0]

    def getRowById(self, tbl, Id):
        return self.getRowByColVal(tbl, 'id', Id)

    def createTable(self, tableRow):
        q = self
        dbtype = self.dbtype
        tbl = tableRow._tableName

        cols = ', '.join(
            f"`{cname}` {cdef[dbtype]}"
                for cname, cdef in tableRow._columnDefs.items()
        )
        q(notriggers=True) / f"""CREATE TABLE IF NOT EXISTS `{tbl}` ({cols})"""

    def createIndices(self, tableRow):
        q = self
        dbtype = self.dbtype
        tbl = tableRow._tableName

        for iname, idef in tableRow._indexDefs.items():
            q / f"""
                CREATE INDEX IF NOT EXISTS {iname}
                ON `{tbl}` ({
                    ', '.join(f"`{col}`" for col in idef[dbtype])
                })
            """

    def saveTableRow(self, tableRow, commit=True):
        q = self
        vs = tableRow._getValues()
        sks = sorted(vs)
        tbl = tableRow._tableName
        pk = tableRow._primaryKey

        pkv = getattr(tableRow, pk, None)
        if pkv is None:
            vs.pop(pk, None)
            cursor = q(returnCursor=True, commit=commit, **vs) / f"""
                INSERT INTO `{tbl}` (
                    {
                        ", ".join(
                            f"`{col}`" for col in sks
                        )
                    }
                ) VALUES (
                    {
                        ", ".join(
                            f"%({col})s" for col in sks
                        )
                    }
                )
            """
            vs[pk] = cursor.lastrowid
            setattr(tableRow, pk, cursor.lastrowid)
        else:
            vs[pk] = pkv
            q(commit=commit, _pkv=pkv, **vs) / f"""
                UPDATE `{tbl}` SET
                    {
                        ", ".join(
                            f"`{col}` = %({col})s"
                                for col in tableRow._columnDefs
                        )
                    }
                WHERE `{pk}` = %(_pkv)s
                LIMIT 1
            """

        if len(vs) != len(tableRow._columnDefs):
            ks = set(tableRow._columnDefs) - set(vs)
            row = q(0, commit=commit, _pkv=pkv, **vs) / f"""
                SELECT {
                    ', '.join(
                        f'`{k}`' for k in ks
                    )
                }
                FROM `{tbl}`
                WHERE `{pk}` = %(_pkv)s
            """

            for k in row.keys():
                setattr(tableRow, k, row[k])

    def deleteTableRow(self, tableRow, commit=True):
        tbl = tableRow._tableName
        pk = tableRow._primaryKey
        pkv = getattr(tableRow, pk)

        self(_pkv=pkv, commit=commit) / f"""
            DELETE FROM `{tbl}`
            WHERE `{pk}` = %(_pkv)s
            LIMIT 1
        """
        
    def fetchRows(self, qpars):
        """Retrieve rows in chunks instead of calling fetchone() or fetchall()

        Requesting rows one by one might cause latency and pulling
        the whole result set would consume a lot of memory
        """

        cursor = qpars.get('cursor')
        chunkSz = self.MAX_ROWS_PER_FETCH

        while True:
            rs = cursor.fetchmany(chunkSz)
            if not rs: break

            for r in rs:
                yield r

    def getColumns(self, tbl):
        cur = self(returnCursor=True) / f"SELECT * FROM `{tbl}` LIMIT 0"
        cols = [
            cd[0] for cd in cur.description
        ]

        return cols
