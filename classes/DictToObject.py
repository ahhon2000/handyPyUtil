class DictToObject:
    """Convert a dictionary to an object by mapping keys to attributes
    """

    def __init__(self, d):
        for k, v in d.items():
            setattr(self, k, v)
