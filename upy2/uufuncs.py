from upy2.core import undarray

#
# uufunc classes ...
#

class Add(object):
    def __call__(self, a, b):
        derivatives = []

        if isinstance(a, undarray):
            A = a.nominal
            derivatives.append((a, 1.0))
        else:
            A = a

        if isinstance(b, undarray):
            B = b.nominal
            derivatives.append((b, 1.0))
        else:
            B = b

        return undarray(
            nominal=(A + B),
            derivatives=derivatives,
        )

#
# The actual uufuncs ...
#

uadd = Add()
