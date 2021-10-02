from . import Database

class TableRow:
    def __init__(self, bindObject, fromRow=None, dbobj=None):
        self.bindObject = bindObject
        
        if not dbobj:
            for k in ('q', 'dbobj', 'db', 'database'):
                q = getattr(bindObject, k, None)
                if q and isinstance(q, Database):
                        dbobj = q
                        break
            if not dbobj: raise Exception(f'could not find a Database instance')

        self.dbobj = dbobj
