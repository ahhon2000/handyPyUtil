from more_itertools import islice_extended

def subscriptPars(subscript):
    """Calculate and return (start, stop, step) for an int or slice subscript
    """

    i0, i1, step = 0, None, 1

    if subscript is None: pass
    elif isinstance(subscript, int):
        if subscript >= 0:
            i0, i1 = subscript, subscript + 1
        else:
            i0, i1, step = subscript, subscript - 1, -1
    elif isinstance(subscript, slice):
            i0, i1, step = subscript.start, subscript.stop, subscript.step
    else:
        raise Exception(f'unsupported subscript type: {type(subscript)}')

    return i0, i1, step


def subscriptToSlice(subscript):
    """Return a slice created from a subscript that can be of type int or slice
    """

    return slice(*subscriptPars(subscript))


def applySubscript(seq, subscript, intSubscrReturnsElem=True):
    """Return an iterator over a sequence for an int/slice subscript

    If intSubscrReturnsElem is True and subscript is an integer return
    the subscript-th element rather than a subsequence consisting of it.
    """

    vs = islice_extended(seq, *subscriptPars(subscript))
    if isinstance(subscript, int) and intSubscrReturnsElem:
        return next(vs)
    return vs
