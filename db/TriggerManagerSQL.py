import json

from .TriggerManager import TriggerManager
from .exceptions import *

def timingEvtToCallbackName(timing, evt):
    return f'{timing.lower()}{evt.capitalize()}'


class TriggerManagerSQL(TriggerManager):
    AVAILABLE_CALLBACKS = {
        timingEvtToCallbackName(timing, evt): {'timing': timing, 'event': evt}
            for timing in ('BEFORE', 'AFTER'):
                for evt in ('INSERT', 'UPDATE', 'DELETE'):
    }
    TMP_TBL_NAME = 'trigger_manager'

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self._tmpTblExists = False

    def createTrigger(self, tbl, trpar):
        # TODO complete
        assert 0

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

        rs = self.dbobj(timing=timing) / f"""
            SELECT `table_name`, `event`, `data` FROM `{self.TMP_TBL_NAME}`
            WHERE `timing` = %(timing)s
            ORDER BY `id`
        """

        bo = qpars['bindObject']
        for r in rs:
            tableName, evt, trgData = r['table_name'], r['event'], r['data']
            cbn = timingEvtToCallbackName(timing, evt)
            self.fire(bo, tableName, cbn, trgData)
            

    def catchBeforeCommit(self, qpars):
        self._catchEvtsFromTmpTbl('BEFORE', qpars)

    def catchAfterCommit(self, qpars):
        self._catchEvtsFromTmpTbl('AFTER', qpars)
