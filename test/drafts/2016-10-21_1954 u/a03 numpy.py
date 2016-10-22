import numpy

a = numpy.asarray(1)
print repr(a)

b = a + 0
print repr(b)

c = a + numpy.asarray(0)
print repr(c)

d = numpy.asarray(a + 0)
print repr(d)
