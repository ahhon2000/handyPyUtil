from math import isclose
import copy

from . import Database


class TableRow:
    """A model representing a row in a DB table, as well as the table itself

    Meta attributes (i. e., all attributes except those which model columns)
    start with an underscore.
    """

    _columnDefs = {}  # format:  {colname: {dbtype: coldef}}
    _indexDefs = {}   # format:  {indname: {dbtype: (col1, col2, ...)}}
    _tableName = ''

    def __init__(self, _bindObject, _fromRow=None, _fromId=None, _dbobj=None,
        **fieldVals,
    ):
        self._bindObject = _bindObject
        self._flgDeleted = False
        
        if not _dbobj:
            for k in ('q', '_dbobj', 'db', 'database', 'dbobj',):
                q = getattr(_bindObject, k, None)
                if q and isinstance(q, Database):
                        _dbobj = q
                        break
            if not _dbobj: raise Exception(f'could not find a Database instance')

        self._dbobj = q = _dbobj

        if _fromRow and _fromId:
            raise Exception(f'_fromRow and _fromId cannot be used together')

        tbl = self._tableName

        fs = None
        if _fromRow:
            fs = _fromRow
        elif _fromId:
            fs = q.getRowById(tbl, _fromId)
        else:
            fs = fieldVals

        for k in fs.keys():
            if k not in self._columnDefs: raise Exception(f'table `{tbl}` does not have a column named `{k}`')
            setattr(self, k, fs[k])

    def _getValues(self):
        return dict(
            (col, getattr(self, col))
                for col in self._columnDefs if hasattr(self, col)
        )

    def _setValues(self, vs):
        for k, v in vs.items():
            if k not in self._columnDefs: raise Exception(f'table `{self._tableName}` does not have a column named `{k}`')

            setattr(self, k, v)

    def _save(self, commit=True):
        self._dbobj.saveTableRow(self, commit=commit)

    def _delete(self, commit=True):
        self._dbobj.deleteTableRow(self, commit=commit)
        self._flgDeleted = True

    def _same(self, other, abs_tol=1e-9):
        for k in self._columnDefs:
            v0, v1 = (getattr(r, k, None) for r in (self, other))

            if isinstance(v0, (int, str)):
                if v0 != v1: return False
            elif isinstance(v0, float):
                if not isclose(v0, v1, abs_tol=abs_tol): return False
            elif v0 is None:
                if v1 is not None: return False
            else: raise Exception(f'unsupported field type: {type(v0)}')

        return True

    def _copy(self):
        return copy.copy(self)
