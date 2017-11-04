from __future__ import division
import numpy

class Test(object):
    def __init__(self, desc=None):
        if desc is None:
            desc = ""
        self.desc = desc
    def __str__(self):
        return "Test(%s)" % self.desc
    def __repr__(self):
        return "Test('%s')" % self.desc

    def absolute(self):
        return Test("calculated by absolute")
    def abs(self):
        return Test("calculated by abs")
    def __abs__(self):
        return Test("calculated by __abs__")

    def __radd__(self, o):
        return Test('calculated by __radd__')
    def __rsub__(self, o):
        return Test('calculated by __radd__')
    def __rmul__(self, o):
        return Test('calculated by __rmul__')
    def __rdiv__(self, o):
        return Test('calculated by __rdiv__')
    def __rtruediv__(self, o):
        return Test('calculated by __rtruediv__')
    def __rfloordiv__(self, o):
        return Test('calculated by __rfloordiv__')

    def conj(self):
        return Test('calculated by conj')
    def conjugate(self):
        return Test('calculated by conjugate')

#    def __eq__(self, o):
#        print '{eq:%r:%r}' % (self, o)
#        return Test('calculated by __eq__')
#    def __ne__(self, o):
#        print '{ne:%r:%r}' % (self, o)
#        return Test('calculated by __ne__')

    def __neg__(self):
        return Test('calculated by __neg__')

    def __rpow__(self, o):
        return Test('calculated by __rpow__')

    def __rdiv__(self, o):
        return Test('calculated by __rdiv__')

    def sqrt(self):
        return Test('calculated by sqrt')

    def square(self):
        return Test('calculated by square')
    def __pow__(self):
        return Test('calculated by __pow__')
    def __mul__(self, o):
        return Test('calculated by __mul__')

t = Test()
sc = numpy.asarray(42)
ar = numpy.asarray([10])
ar2 = numpy.asarray([10, 11])
print "-- numpy.absolute() --"
print "numpy.absolute(t):", numpy.absolute(t)

print "-- numpy addition for scalar ndarray --"
print "sc + t:", sc + t
print "repr(sc + t):", repr(sc + t)

print "-- numpy addition for non-scalar ndarray --"
print "ar + t:", ar + t
print "repr(ar + t):", repr(ar + t)
print "repr(numpy.add(ar, t)):", repr(numpy.add(ar, t))

print "-- numpy subtraction --"
print "repr(sc - t):", repr(sc - t)
print "repr(ar2 - t):", repr(ar2 - t)

print "-- numpy multiplication --"
print "repr(sc * t):", repr(sc * t)
print "repr(ar2 * t):", repr(ar2 * t)

print "-- numpy floor division --"
print "repr(sc // t):", repr(sc // t)
print "repr(ar2 // t):"; print repr(ar2 // t)

print "-- numpy true division --"
# Notice the "from __future__" statement in the beginning of the file.
print "repr(sc / t):", repr(sc / t)
print "repr(ar2 / t):"; print repr(ar2 / t)

print "-- numpy.conjugate() --"
print "numpy.conjugate(t):", numpy.conjugate(t)

# Equality and Inequality is not defined unambiguously.
#
# print "-- numpy equality --"
# print "ar == t:", ar == t
# print "repr(ar == t):", repr(ar == t)
# print "repr(ar2 == t):", repr(ar2 == t)
# # # Illustrate how the ndarray __eq__ method recourses to the numpy
# # # operator.
# # class AlwaysEq(object):
# #     def __eq__(self, o):
# #         return True
# # class NeverEq(object):
# #     def __eq__(self, o):
# #         return False
# # print "repr(sc.__eq__(AlwaysEq())):", repr(sc.__eq__(AlwaysEq()))
# # print "repr(sc.__eq__(NeverEq())):", repr(sc.__eq__(NeverEq()))
# # print "repr(er2.__eq__(AlwaysEq())):", repr(ar2.__eq__(AlwaysEq()))
# 
# print "-- numpy inequality --"
# print "repr(ar2 != t):", repr(ar2 != t)

print "-- numpy.negative() --"
print "numpy.negative(t):", numpy.negative(t)

print "-- numpy.power() --"
print "numpy.power(sc, t):", numpy.power(sc, t)
print "repr(numpy.power(sc, t)):", repr(numpy.power(sc, t))
print "repr(numpy.power(ar2, t)):", repr(numpy.power(ar2, t))

print "-- numpy power --"
print "repr(sc ** t):", repr(sc ** t)
print "repr(ar2 ** t):", repr(ar2 ** t)

print "-- numpy.reciprocal() --"
print "numpy.reciprocal(t):", numpy.reciprocal(t)

print "-- numpy.sqrt() --"
print "numpy.sqrt(t):", numpy.sqrt(t)

print "-- numpy.square() --"
print "numpy.square(t):", numpy.square(t)
