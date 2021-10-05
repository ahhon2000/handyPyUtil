import re

def convertPHolders_mysql_to_sqlite(r):
    pphr = re.compile(r'(?P<perc>([^%]|^)(%%)*)%s\b')
    nphr = re.compile(r'(?P<perc>([^%]|^)(%%)*)%\((?P<ph>\w+)\)s')

    r = pphr.sub(r'\g<perc>?', r)
    r = nphr.sub(r'\g<perc>:\g<ph>', r)

    r = re.sub(r'%%', r'%', r)

    return r
