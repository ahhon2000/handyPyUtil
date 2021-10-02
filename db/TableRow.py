from math import isclose
import copy

from . import Database


class TableRow:
    columnDefs = {}  # format:  {colname: {dbtype: coldef}}
    indexDefs = {}   # format:  {indname: {dbtype: (col1, col2, ...)}}
    tableName = ''

    def __init__(self, bindObject, fromRow=None, fromId=None, dbobj=None):
        self.bindObject = bindObject
        self.flgDeleted = False
        
        if not dbobj:
            for k in ('q', 'dbobj', 'db', 'database'):
                q = getattr(bindObject, k, None)
                if q and isinstance(q, Database):
                        dbobj = q
                        break
            if not dbobj: raise Exception(f'could not find a Database instance')

        self.dbobj = self.q = q = dbobj

        if fromRow and fromId:
            raise Exception(f'fromRow and fromId cannot be used together')

        tbl = self.tableName

        fs = None
        if fromRow:
            fs = fromRow
        elif fromId:
            q.getRowById(tbl, fromId)
        else:
            fs = kwarg

        for k in fs.keys():
            if k not in self.columnDefs: raise Exception(f'table `{tbl}` does not have a column named `{k}`')
            setattr(self, k, fs[k])

    def getValues(self):
        return dict(
            (col, getattr(self, col))
                for col in self.columnDefs if hasattr(self, col)
        )

    def setValues(self, vs):
        for k, v in vs.items():
            if k not in self.columnDefs: raise Exception(f'table `{self.tableName}` does not have a column named `{k}`')

            setattr(self, k, v)

    @classmethod
    def createTable(Cls, q):
        for k in q.PROHIBITED_COL_NAMES:
            raise Exception(f'"{k}" is not allowed to be used as a column name')
        q.createTable(Cls)

    @classmethod
    def createIndex(Cls, q):
        q.createIndices(Cls)

    def save(self, commit=True):
        self.q.saveTableRow(self, commit=commit)

    def delete(self):
        self.q.deleteTableRow(self)
        tableRow.flgDeleted = True

    def same(self, other, abs_tol=1e-9):
        for k in self.columnDefs:
            v0, v1 = (getattr(r, k, None) for r in (self, other))

            if isinstance(v0, (int, str)):
                if v0 != v1: return False
            elif isinstance(v0, float):
                if not isclose(v0, v1, abs_tol=abs_tol): return False
            elif v0 is None:
                if v1 is not None: return False
            else: raise Exception(f'unsupported field type: {type(v0)}')

        return True

    def copy(self):
        return copy.copy(self)
