class ClonableClass:
    EDITABLE_TUPLE_ATTRS = ()

    @classmethod
    def cloneClass(Cls, **kwarg):
        """Clone class Cls with optional changes controlled by kwarg

        For each ATTR in EDITABLE_TUPLE_ATTRS, this method accepts the
        following keyword arguments:

            set_ATTR, add_ATTR, rm_ATTR

        If one of them is given then the clone's tuple attribute ATTR will be
        modified accordingly. If it doesn't exist in the parent class
        it will be created in the clone.

        Example:

            class A(ClonableClass):
                LETTERS = ('a', 'b', 'c')
                EDITABLE_TUPLE_ATTRS = ('LETTERS',)
                ...

            class B(
                A.cloneClass(add_LETTERS=('d', 'e'))
            ):
                ...

        B.LETTERS will be the following tuple: ('a', 'b', 'c', 'd', 'e')
        """

        n = Cls.__name__
        clsCnt = []
        exec(f"""
class {n}(Cls): pass
clsCnt.append({n})
""")
        Clone = clsCnt.pop()

        for a in Clone.EDITABLE_TUPLE_ATTRS:
            available_cmds = set(f'{cmd}_{a}' for cmd in ('set', 'add', 'rm'))
            cmds = available_cmds.intersection(kwarg)

            if len(cmds) == 0:
                pass
            elif len(cmds) == 1:
                cmd = cmds.pop()
                v0, v = getattr(Clone, a, ()), kwarg[cmd]

                if cmd == f'set_{a}':
                    v = tuple(v)
                elif cmd == f'add_{a}':
                    v = tuple(list(v0) + list(v))
                elif cmd == f'rm_{a}':
                    vset = set(v)
                    v = tuple(x for x in v0 if x not in vset)
                else: raise Exception(f'unexpected command: {cmd}')

                setattr(Clone, a, v)
            else: raise Exception(f'incompatible options')

        return Clone
