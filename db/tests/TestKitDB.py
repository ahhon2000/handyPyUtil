from pathlib import Path
import sys, os
import stat

from ...tests import TestKit
from ..Database import DBTYPES

class TestKitDB(TestKit):
    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)

        self.databases = []

    def connect(self, DBCls=None, recreate_db=True, **dbkwarg):
        self._setDfltCfgFile(DBCls, dbkwarg)

        db = DBCls(debug=True, logger=self.logger, **dbkwarg)
        self.databases.append(db)

        if recreate_db: db.recreateDatabase()

        return db

    def _setDfltCfgFile(self, DBCls, dbkwarg):
        dbtype = DBCls.dbtype
        if dbtype not in (DBTYPES.mysql,): return

        dfltCfgFile = Path(sys.argv[0]).absolute().parent
        dfltCfgFile /= f'{DBCls.dbtype.name}.cnf'

        cfgFile = dbkwarg.setdefault('read_default_file', str(dfltCfgFile))
        cfgFile = Path(cfgFile)
        if cfgFile.exists():
            m = dfltCfgFile.stat().st_mode
            if m & (stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH):
                raise Exception(f'The permissions of {cfgFile} are too insecure')

    def cleanup(self, *arg, **kwarg):
        self._cleanupDatabases()

    def _cleanupDatabases(self):
        dbs = self.databases
        while dbs:
            db = dbs.pop()
            db.recreateDatabase()
            db.close()
