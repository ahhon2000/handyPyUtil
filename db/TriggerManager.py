from itertools import chain
from collections import defaultdict

class TriggerManager:
    AVAILABLE_CALLBACKS = {}  # format:  CALLBACK_NAME: TRIGGER_PARS_DICT

    def __init__(self, dbobj):
        self.dbobj = dbobj
        self.triggers = defaultdict(lambda: defaultdict(list))

    def createTrigger(self, tbl, trpar): raise NotImplementedError()
    def dropTrigger(self, tbl, trpar): raise NotImplementedError()

    def nothingToCatch(self, qpars):
        if not self.triggers: return True
        return False

    def catchBeforeCommit(self, qpars): pass
    def catchAfterCommit(self, qpars): pass

    def connectCallbacks(self, tbl, **callbacks):
        """Associate callbacks with a DB table's triggers

        If tbl is a string containing the name of a table, connect each
        entry in `callbacks' that are not None to their respective triggers
        in the DB table.

        If tbl is TableRow or its subclass, first connect the callbacks
        defined as class methods of that class, if they exist.
        Then connect the callbacks in the `callbacks' dictionary, if any.

        If tbl is None or '*' each callback will be associated with all DB
        tables.

        The `callbacks' dictionary may contain any of the callbacks listed in
        in the AVAILABLE_CALLBACKS attribute. Note that trigger-callback names
        in TableRow and its subclasses must be prepended with an underscore
        (e. g., _beforeInsert() instead of beforeInsert()).

        When a trigger is fired its connected callbacks will be called in
        the same order they were registered. Each callback f will be called
        with the following arguments:

                f(bindObject, trgData),

        where bindObject is the bind object determined by Database.execute()
        and trgData is a dictionary containing data produced by the trigger,
        such as old/new column values, table name, etc.

        If a trigger is missing from the DB table it will be automatically
        created.
        """

        wrong_cbs = set(callbacks) - set(self.AVAILABLE_CALLBACKS)
        if wrong_cbs: raise Exception(f'illegal trigger callbacks: {wrong_cbs}')

        from . import TableRow
        tblIsTableRow = isinstance(tbl, type) and issubclass(tbl, TableRow)
        TRCls = tbl if tblIsTableRow else None

        # determine the table name
        tableName = None
        if TRCls: tableName = TRCls._tableName
        elif tbl == '*': tableName = None
        elif isinstance(tbl, str): tableName = tbl
        else: raise Exception(f'illegal value of argument "tbl"')

        trgsFromTRCls = (
            {'name': cbn, 'cb': cb}
                for cbn, cb in (
                    cbn, getattr(TRCls, '_' + cbn, None)
                        for cbn in self.AVAILABLE_CALLBACKS
                ) if cb is not None
        ) if TRCls else ()

        trgsFromCallbacks = (
            {'name': cbn, 'cb': cb} for cbn, cb in callbacks.items()
        )

        for trg in chain(trgsFromTRCls, trgsFromCallbacks):
            cbn, cb = trg['name'], trg['cb']
            trpar = self.AVAILABLE_CALLBACKS[cbn]
            self.createTrigger(tableName, trpar)

            self.triggers[tableName][cbn].append(cb)

    def fire(self, bindObject, tableName, cbn, trgData):
        """Fire all callbacks named cbn that were registered for a DB table

        Global callbacks (i. e. those which were registered for all tables)
        will be fired first, if any.
        """

        trgData['tableName'] = tableName
        trgs = self.triggers

        for tableName2 in (None, tableName):
            cbs = trgs.get(tableName2, {}).get(cbn, ()),
            for cb in cbs:
                cb(bindObject, trgData)
