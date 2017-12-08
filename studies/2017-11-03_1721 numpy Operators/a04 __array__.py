#!/usr/bin/python

import numpy

class X(object):
    def __array__(self):
        return numpy.asarray([42, 43])

    def __radd__(self, other):
        return numpy.asarray([10, 11])

class Y(object):
    def __radd__(self, other):
        return numpy.asarray([11, 12])

ar = numpy.asarray([1, 2])
x = X()
y = Y()

print "ar + y =", repr(ar + y)
print "ar + x =", repr(ar + x)
