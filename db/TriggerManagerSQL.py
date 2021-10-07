from .TriggerManager import TriggerManager
from .exceptions import *


class TriggerManagerSQL(TriggerManager):
    AVAILABLE_CALLBACKS = {
        f'{timing.lower()}{evt.capitalize()}': {'timing': timing, 'event': evt}
            for timing in ('BEFORE', 'AFTER'):
                for evt in ('INSERT', 'UPDATE', 'DELETE'):
    }

    def createTrigger(self, tbl, trpar):
        # TODO complete
        assert 0

    def dropTrigger(self, tbl, trpar):
        # TODO complete
        assert 0

    def nothingToCatch(self, qpars):
        if super().nothingToCatch(qpars): return True

        cursor = qpars.get('cursor')
        if not cursor: raise Exception(f'the trigger manager could find no cursor')
        if cursor.description is None: return False
        return True

    def catchBeforeCommit(self, qpars):
        if self.nothingToCatch(qpars): return

    def catchAfterCommit(self, qpars):
        if self.nothingToCatch(qpars): return
