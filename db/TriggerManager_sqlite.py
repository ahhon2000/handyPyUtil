from . import TriggerManagerSQL

class TriggerManager_sqlite(TriggerManagerSQL):
    def createTmpTbl(self):
        self.dbobj / f"""
            CREATE TEMPORARY TABLE `{self.TMP_TBL_NAME}` (
                `id` INTEGER UNSIGNED NOT NULL PRIMARY KEY AUTOINCREMENT,
                `table_name` TEXT NOT NULL,
                `timing` TEXT NOT NULL,
                `event` TEXT NOT NULL,
                `data` TEXT NOT NULL
            )
        """
