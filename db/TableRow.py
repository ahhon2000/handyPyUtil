from math import isclose
import copy

from . import Database
from .exceptions import *


def _getDBObj(*arg):
    for a in arg:
        if isinstance(a, Database): return a
        if not a: continue

        if isinstance(a, dict):
            candidate = a.get('_dbobj')
            if isinstance(candidate, Database): return candidate

        for k in ('q', '_dbobj', 'db', 'database', 'dbobj',):
            candidate = getattr(a, k, None)
            if candidate and isinstance(candidate, Database):
                return candidate

    raise Exception(f'could not find a Database instance')


class TableRow:
    """A model representing a row in a DB table, as well as the table itself

    Meta attributes (i. e., all attributes except those which model columns)
    start with an underscore.
    """

    _columnDefs = {}  # format:  {colname: {dbtype: coldef}}
    _indexDefs = {}   # format:  {indname: {dbtype: (col1, col2, ...)}}
    _tableName = ''
    _primaryKey = 'id'
    _constraints = {}  # format:  {dbtype: ["constr1", "constr2", ..], ...}

    def __init__(self, _bindObject,
        _dbobj = None,
        **fieldVals,
    ):
        self._bindObject = _bindObject
        self._flgDeleted = False
        self._dbobj = q = _getDBObj(_dbobj, _bindObject)
        tbl = self._tableName

        fs = fieldVals

        for k in fs.keys():
            if k not in self._columnDefs: raise Exception(f'table `{tbl}` does not have a column named `{k}`')
            setattr(self, k, fs[k])

    @classmethod
    def _fromColVal(Cls, bo, col, val, *arg, **kwarg):
        """Return a TableRow with the given column value

        Return None if the record can't be found in the DB
        """

        _dbobj = _getDBObj(kwarg, bo)
        kwarg['_dbobj'] = _dbobj  # to help the TableRow constructor find _dbobj

        try:
            fs = _dbobj.getRowByColVal(Cls._tableName, col, val)
        except ExcRecordNotFound:
            return None

        return Cls(bo, *arg, **fs, **kwarg)

    @classmethod
    def _fromPK(Cls, bo, pkv, *arg, **kwarg):
        """Return the TableRow whose primary key equals pkv

        Return None if the record can't be found in the DB
        """

        pk = Cls._primaryKey
        return Cls._fromColVal(bo, pk, pkv, *arg, **kwarg)

    @classmethod
    def _fromId(Cls, bo, Id, *arg, **kwarg):
        return Cls._fromColVal(bo, 'id', Id, *arg, **kwarg)

    @classmethod
    def _fromRow(Cls, bo, *arg, **kwarg):
        row = arg[-1]
        return Cls(bo, *(arg[0:-1]), **row, **kwarg)

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

    def _deepcopy(self):
        return copy.deepcopy(self)

    @classmethod
    def _nRecords(Cls, q):
        col = next(iter(Cls._columnDefs))
        return q[0]['n'] / f"SELECT count(`{col}`) as n FROM `{Cls._tableName}`"

    @classmethod
    def _isEmpty(Cls, q):
        n = Cls._nRecords(q)
        return n == 0

    def _getDynamicConstraints(self):
        """
        Return a dictionary of constraints to be used just before table creation

        The format of the returned dictionary:
        {
            DBTYPE1: (CONSTR1, CONSTR2, ...),
            DBTYPE2: (CONSTR1, CONSTR2, ...),
            ...
        }

        Each CONSTR element is a string
        """

        return {}
