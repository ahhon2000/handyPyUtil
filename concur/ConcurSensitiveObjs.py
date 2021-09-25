import threading

class ConcurSensitiveObjs:
    """
    A container for concurrency-sensitive objects that may need a lock
    to work with them.

    The first argument to the constructor is the RLock to use. If it is omitted
    a new RLock will be created.

    USAGE:
        # Adding objects
        concur = ConcurSensitiveObjs(rlock)  # arg 'rlock' is optional
        concur.some_var1 = ...
        concur.some_var2 = ...

        # Accessing objects without locking is as simple as:
        print(concur.some_var1)

        # Accessing objects WITH locking:
        with concur:    # the lock is acquired
            concur.some_var1 = ...
            ... = concur_some_var2
            ...
                        # the lock is released upon exiting the with block
    """

    def __init__(self, lock=None):
        if lock is None: lock = threading.RLock()
        self._lock = lock

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, Type, value, tb):
        self._lock.release()
