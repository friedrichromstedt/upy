import numpy

class X:
    counter = 0

    def __init__(self, *coordinates):
        self.coordinates = coordinates

    def __repr__(self):
        string = str(X.counter)
        X.counter = X.counter + 1
        print self.coordinates
        return string

    # __str__() isn't invoked by numpy
    __str__ = __repr__

shape = numpy.asarray([50, 50])
# print X()

x, y = numpy.meshgrid(*(numpy.arange(comp) for comp in shape))
#print "x ="
#print x
#print "y ="
#print y
flat = [X(xi, yi) for (xi, yi) in zip(x.flat, y.flat)]
shaped = numpy.asarray(flat).reshape(shape)

print shaped
