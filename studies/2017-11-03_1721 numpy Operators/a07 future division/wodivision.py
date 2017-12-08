class X(object):
    def __div__(self, o):
        return 42
    def __truediv__(self, o):
        return 43 / 2
    def __floordiv__(self, o):
        return 44
