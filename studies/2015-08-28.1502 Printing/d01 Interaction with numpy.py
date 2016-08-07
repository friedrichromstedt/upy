import numpy


class mstrA(str):
    def __init__(self, replacement):
        self.replacement = replacement

    def __new__(cls, replacement):
        return str.__new__(cls)

objar = numpy.asarray([mstrA('Hello world!')])

# >>> objar
# array([''], 
#       dtype='|S1')

objar2 = numpy.asarray([mstrA('Hello world!')], dtype=numpy.object)

# >>> objar2
# array([''], dtype=object)
# >>> objar2[0].replacement
# 'Hello world!
# >>> print objar2
# ['']


class mstrB(str):
    def __init__(self, replacement):
        self.replacement = replacement

    def __new__(cls, replacement):
        return str.__new__(cls)

    def get(self):
        return self.replacement

    def __add__(self, o):
        return self
    def __radd__(self, o):
        return self

# >>> m1 = mstrB('halo')
# >>> m1
# ''
# >>> m1.get()
# 'halo'
# >>> (m1 + 'world')
# ''
# >>> (m1 + 'world').get()
# 'halo'

mstrB_ar = numpy.asarray([mstrB('hello')], dtype=numpy.object)

# neither ``str(mstrB_ar)`` nor ``repr(mstrB_ar)`` feature '.get()'.

class mstrC(mstrB):
    def __str__(self):
        return "__str__"
    def __repr__(self):
        return "__repr__"

mstrC_ar = numpy.asarray([mstrC('hello')], dtype=numpy.object)

# >>> print mstrC_ar
# [__repr__]

class mstrC2(mstrB):
    def __str__(self):
        return self
    def __repr__(self):
        return self

mstrC2_ar = numpy.asarray([mstrC2('hello')], dtype=numpy.object)

# str(mstrC2_ar) does not feature '.get'.  str(mstrC2_ar[0]) does feature '.get'.
