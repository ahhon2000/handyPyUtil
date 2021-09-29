from handyPyUtil.imports.imports import importClassesFromPackage
print(f'init PACKAGE = {__package__}') # TODO rm
exec(importClassesFromPackage(__file__))

from .util import *
