import numpy

class X:
    counter = 0

    def __repr__(self):
        string = str(X.counter)
        X.counter = X.counter + 1
        return string

    # __str__() isn't invoked by numpy
    __str__ = __repr__

shape = numpy.asarray([50, 50])
# print X()

flat = [X() for i in xrange(shape.prod())]
shaped = numpy.asarray(flat).reshape(shape)

print shaped
