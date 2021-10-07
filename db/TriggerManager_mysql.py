from .TriggerManagerSQL import TriggerManagerSQL

class TriggerManager_mysql(TriggerManagerSQL):
    def createTmpTbl(self):
        self.dbobj / f"""
            CREATE TEMPORARY TABLE `{self.TMP_TBL_NAME}` (
                `id` INTEGER UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
                `table_name` VARCHAR(128) NOT NULL,
                `timing` VARCHAR(16) NOT NULL,
                `event` VARCHAR(16) NOT NULL,
                `data` LONGTEXT NOT NULL
            )
        """
