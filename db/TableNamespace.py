
from .SmartQuery import SmartQuery

class TableNamespaceMap:
    def __init__(self, tableNamespace):
        self.tableNamespace = tableNamespace

    def __getitem__(self, tbln):
        return f'`{self.tableNamespace}_{tbln}`'


class TableNamespace(SmartQuery):
    """Execute DB queries in a table namespace

    An object of this class behaves the same as SmartQuery, only table name
    placeholders in the request string are automatically replaced with
    the respective table names that belong to a given namespace.

    For example, a database managing a phonebook, purchases, memos for each
    a large number of users could have the following tables:

        user1_phonebook, user1_purchases, user1_memos,
        user2_phonebook, user2_purchases, user2_memos,
        ...

    The name of each user table here is prepended with that user's name in order
    to compartmentalise data. Thus the database has table namespaces
    `user1', `user2', and so on.

    The purpose of TableNamespace is to allow for requests like

        SELECT * FROM {phonebook}

    in which the real table name with the namespace prefix is substituted for
    the placeholder(s). In this example, if TableNamespace is told that
    it should work in the `user1` namespace then {phonebook} will be converted
    to `user1_phonebook` (including the backquotes).

            **** USAGE ****

    Step 1. Instantiate TableNamespace for some namespace:

        q = TableNamespace(dbobj, tableNamespace='user1')

    dbobj is an object of class Database.

    Step 2. Execute DB requests in that namespace:

        q / "CREATE TABLE IF EXISTS {memos}"
        q / "SELECT * FROM {phonebook}"
        
    NOTE: Use double curly braces in f-strings:

        q / f"SELECT * FROM {{purchases}} WHERE {col} = 5"
    """

    def __init__(self, *arg, inplaceOps=False, **kwarg):
        super().__init__(self, *arg, inplaceOps=inplaceOps, **kwarg)

    def tryToExecute(self):
        r = self.getInternal('request')
        if r:
            tableNamespace = self.kwarg.pop('tableNamespace', None)
            if tableNamespace:
                m = TableNamespaceMap(tableNamespace)
                r = r.format_map(m)
                self.setInternal('request', r, previouslySetOk=True)

        return super().tryToExecute()
