import json

from .TriggerManager import TriggerManager
from .exceptions import *

def timingEvtToCallbackName(timing, evt):
    return f'{timing.lower()}{evt.capitalize()}'

def getTriggerName(tableName, timing, evt):
    trgn = f'trg_{tableName}_{timing}_{evt}'
    return trgn


class TriggerManagerSQL(TriggerManager):
    AVAILABLE_CALLBACKS = {
        timingEvtToCallbackName(timing, evt): {'timing': timing, 'event': evt}
            for timing in ('BEFORE', 'AFTER')
                for evt in ('INSERT', 'UPDATE', 'DELETE')
    }
    TMP_TBL_NAME = 'trigger_manager'

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self._tmpTblExists = False

    def createTrigger(self, tbl, trpar):
        timing, evt = trpar.get('timing', ''), trpar.get('event', '')
        cbn = timingEvtToCallbackName(timing, evt)
        if cbn not in self.AVAILABLE_CALLBACKS: raise Exception(f'illegal value of timing and/or event')
        if not tbl: raise Exception(f'no table name given')

        q = self.dbobj

        trgn = getTriggerName(tbl, timing, evt)

        cols = q.getColumns(tbl)
        rowTypes = {
            'INSERT': ('NEW',),
            'UPDATE': ('OLD', 'NEW',),
            'DELETE': ('OLD',),
        }[evt]

        initialTree = ",".join(f'"{rowType}": {{}}' for rowType in rowTypes)
        initialTree = "{" + initialTree + "}"

        pathValues = []
        for rowType in rowTypes:
            #pathValues.append((f'$.{rowType}', "json_set('{}')"))
            for col in cols:
                pathValues.append(
                    (f'$.{rowType}.{col}', f'{rowType}.`{col}`')
                )

        data = ",".join(f"'{p}',{v}" for p, v in pathValues)
        data = f"json_set('{initialTree}', {data})"

        req = f"""
            CREATE TRIGGER IF NOT EXISTS `{trgn}`
            {timing} {evt} ON `{tbl}`
            FOR EACH ROW
            BEGIN
                INSERT INTO `{self.TMP_TBL_NAME}` (
                    `table_name`, `timing`, `event`,
                    `data`
                ) VALUES (
                    '{tbl}', '{timing}', '{evt}',
                    {data}
                );
            END;
        """

        q(notriggers=True) / req
        self.logger.debug(f'created trigger "{trgn}"')

    def dropTrigger(self, tbl, trpar):
        # TODO complete
        assert 0

    def createTmpTbl(self): raise NotImplementedError()

    def connectCallbacks(self, *arg, **kwarg):
        if not self._tmpTblExists:
            self.createTmpTbl()
            self._tmpTblExists = True
        super().connectCallbacks(*arg, **kwarg)

    def nothingToCatch(self, qpars):
        if super().nothingToCatch(qpars): return True

        cursor = qpars.get('cursor')
        if not cursor: raise Exception(f'the trigger manager could find no cursor')
        if cursor.description is None: return False
        return True

    def _catchEvtsFromTmpTbl(self, timing, qpars):
        if self.nothingToCatch(qpars): return

        q = self.dbobj

        rs = q(timing=timing) / f"""
            SELECT `table_name`, `event`, `data` FROM `{self.TMP_TBL_NAME}`
            WHERE `timing` = %(timing)s
            ORDER BY `id`
        """

        bo = qpars['bindObject']
        for r in rs:
            tableName, evt, trgData = r['table_name'], r['event'], r['data']
            cbn = timingEvtToCallbackName(timing, evt)
            self.fire(bo, tableName, cbn, trgData)

        q(commit=False) / f"DELETE FROM `{self.TMP_TBL_NAME}`"
            

    def catchBeforeCommit(self, qpars):
        self._catchEvtsFromTmpTbl('BEFORE', qpars)

    def catchAfterCommit(self, qpars):
        self._catchEvtsFromTmpTbl('AFTER', qpars)
