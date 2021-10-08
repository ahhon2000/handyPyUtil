import json

from handyPyUtil.loggers.convenience import fmtExc
from .TriggerManager import TriggerManager
from .exceptions import *
from .TriggerExchTbl import TriggerExchTbl

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

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self._ready = False

    def reinit(self):
        self._ready = False
        TriggerExchTbl._create(self.dbobj)
        self._ready = True

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

        exchTblName = TriggerExchTbl._tableName
        req = f"""
            CREATE TRIGGER IF NOT EXISTS `{trgn}`
            {timing} {evt} ON `{tbl}`
            FOR EACH ROW
            BEGIN
                INSERT INTO `{exchTblName}` (
                    `id`,
                    `table_name`, `timing`, `event`,
                    `data`
                ) SELECT
                    (SELECT coalesce(max(id), 0) + 1 FROM `{exchTblName}`),
                    '{tbl}', '{timing}', '{evt}',
                    {data}
                ;
            END;
        """

        q(notriggers=True) / req
        self.logger.debug(f'created trigger "{trgn}" with the following request:\n{req}')

    def dropTrigger(self, tbl, trpar):
        # TODO complete
        assert 0

    def dropTmpTbl(self):
        self.dbobj(notriggers=True) / f"""
            DROP table IF EXISTS `{self.EXCH_TBL_NAME}`
        """
        self._ready = False

    def connectCallbacks(self, *arg, **kwarg):
        if not self._ready:
            self.reinit()
        super().connectCallbacks(*arg, **kwarg)

    def nothingToCatch(self, qpars):
        if super().nothingToCatch(qpars): return True

        cursor = qpars.get('cursor')
        if not cursor: raise Exception(f'the trigger manager could find no cursor')
        if cursor.description is None: return False
        return True

    def prepareForQuery(self, qpars):
        q = self.dbobj
        if self.triggers:
            TriggerExchTbl._clear(q)

    def catch(self, qpars):
        if self.nothingToCatch(qpars): return

        q = self.dbobj
        rs = TriggerExchTbl._getOrderedRawRows(q)

        try:
            bo = qpars['bindObject']
            for r in rs:
                tableName = r['table_name']
                timing = r['timing']
                evt = r['event']
                trgData = json.loads(r['data'])

                cbn = timingEvtToCallbackName(timing, evt)

                try:
                    self.fire(bo, tableName, cbn, trgData)
                except Exception as e:
                    msg = f"trigger callback `{cbn}' for table `{tableName}' failed"
                    msg += ": " + fmtExc(e, inclTraceback=self.debug)
                    self.logger.error(msg)
        finally:
            TriggerExchTbl._clear(q)
