from .TriggerManagerSQL import TriggerManagerSQL

class TriggerManager_sqlite(TriggerManagerSQL):
    def createTmpTbl(self):
        self.dbobj(notriggers=True) / f"""
            CREATE TABLE IF NOT EXISTS `{self.EXCH_TBL_NAME}` (
                `id` INTEGER NOT NULL PRIMARY KEY,
                `table_name` TEXT NOT NULL,
                `timing` TEXT NOT NULL,
                `event` TEXT NOT NULL,
                `data` TEXT NOT NULL
            )
        """
