
from .SmartQuery import SmartQuery

class TableNamespaceMap:
    def __init__(self, tableNamespace):
        self.tableNamespace = tableNamespace

    def __getitem__(self, tbln):
        return f'`{self.tableNamespace}_{tbln}`'


class TableNamespace(SmartQuery):
    def tryToExecute(self):
        r = self.getInternal('request')
        if r:
            tableNamespace = self.kwarg.get('tableNamespace')
            if tableNamespace:
                m = TableNamespaceMap(tableNamespace)
                r = r.format_map(m)
                self.setInternal('request', r, previouslySetOk=True)

        return super().tryToExecute()
