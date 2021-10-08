from .TriggerManagerSQL import TriggerManagerSQL

class TriggerManager_mysql(TriggerManagerSQL):
    def createTmpTbl(self):
        self.dbobj(notriggers=True) / f"""
            CREATE TABLE IF NOT EXISTS `{self.EXCH_TBL_NAME}` (
                `id` INTEGER UNSIGNED NOT NULL PRIMARY KEY,
                `table_name` VARCHAR(128) NOT NULL,
                `timing` VARCHAR(16) NOT NULL,
                `event` VARCHAR(16) NOT NULL,
                `data` LONGTEXT NOT NULL
            )
        """
