import numpy

class X(numpy.ndarray):
    def __new__(self):
        return numpy.ndarray.__new__(X, (4, 1),
            buffer=numpy.ones((4, 1), dtype=numpy.int))

    def __rsub__(self, b):
        return 42
