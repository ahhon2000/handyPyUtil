from .Database import DBTYPES
from . import Database

class DatabaseSQL(Database):
    def __init__(self, *arg, **kwarg):
        dbtype = kwarg.get('dbtype')
        if dbtype not in (DBTYPES.sqlite, DBTYPES.mysql):
            raise Exception(f'DatabaseSQL does not support dbtype={dbtype}')

        super().__init__(self, *arg, **kwarg):


    def prepareQuery(self, qpars):
        qpars['cursor'] = self.connection.cursor()

    def commitAfterQuery(qpars):
        # commit if this is a retrieval request,
        cursor = qpars.get('cursor')
        if cursor.description is None:
            self.connection.commit()

    def getRowById(self, tbl, Id):
        q = self.q
        naa0, naa1 = self.NAMED_ARG_AFFIXES
        rows = q(Id=Id) / f"SELECT * FROM `{tbl}` WHERE `id`={naa0}Id{naa1}"

        if not rows: raise ExcRecordNotFound(f'no record with id={Id}')
        return rows[0]

    def createTable(self, tableRow):
        q = self
        dbtype = self.dbtype
        tbl = tableRow.tableName

        cols = ', '.join(
            f"`{cname}` {cdef[dbtype]}"
                for cname, cdef in tableRow.columnDefs.items()
        )
        q / f"""CREATE TABLE IF NOT EXISTS `{tbl}` ({cols})"""

    def createIndices(self, tableRow):
        q = self
        dbtype = self.dbtype
        tbl = tableRow.tableName

        for iname, idef in tableRow.indexDefs.items():
            q / f"""
                CREATE INDEX IF NOT EXISTS {iname}
                ON `{tbl}` ({
                    ', '.join(f"`{col}`" for col in idef[dbtype])
                })
            """

    def saveTableRow(self, tableRow, commit=True):
        naa0, naa1 = self.NAMED_ARG_AFFIXES
        q = self
        
        vs = tableRow.getValues()
        sks = sorted(vs)
        tbl = tableRow.tableName

        Id = getattr(tableRow, 'id', None)
        if Id is None:
            vs.pop('id', None)
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
                            f"{naa0}{col}{naa1}" for col in sks
                        )
                    }
                )
            """
            vs['id'] = cursor.lastrowid
            setattr(tableRow, 'id', cursor.lastrowid)
        else:
            vs['id'] = Id
            q(commit=commit, **vs) / f"""
                UPDATE `{tbl}` SET
                    {
                        ", ".join(
                            f"`{col}` = {naa0}{col}{naa1}"
                                for col in tableRow.columnDefs
                        )
                    }
                WHERE `id` = {naa0}id{naa1}
                LIMIT 1
            """

        if len(vs) != len(tableRow.columnDefs):
            ks = set(tableRow.columnDefs) - set(vs)
            row = q(0, commit=commit, **vs) / f"""
                SELECT {
                    ', '.join(
                        f'`{k}`' for k in ks
                    )
                }
                FROM `{tbl}`
                WHERE `id` = {naa0}id{naa1}
            """

            for k in row.keys():
                setattr(tableRow, k, row[k])

    def deleteTableRow(self, tableRow, commit=True):
        naa0, naa1 = self.NAMED_ARG_AFFIXES
        Id = getattr(tableRow, 'id')
        tbl = tableRow.tableName

        self(Id = Id, commit=commit) / f"""
            DELETE FROM `{tbl}`
            WHERE `id` = {naa0}Id{naa1}
            LIMIT 1
        """
