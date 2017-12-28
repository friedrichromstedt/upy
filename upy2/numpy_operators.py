import numpy
from upy2.core import undarray, uadd


class BinaryOperator(object):
    def __init__(self, ufunc, uufunc):
        self.ufunc = ufunc
        self.uufunc = uufunc

    def __call__(self, a, b, *args, **kwargs):
        """ *args* and *kwargs* are only used when calling the numpy
        ufunc. """

        if not isinstance(a, undarray) and \
                not isinstance(b, undarray):
            return self.ufunc(a, b, *args, **kwargs)
        else:
            return self.uufunc(a, b)

    def __getattr__(self, name):
        """ Forwards the attribute request to the ufunc contained. """

        return getattr(self.ufunc, name)

    def __str__(self):
        return "<upy Binary operator for numpy %s and upy %s>" % \
            (self.ufunc, self.uufunc)

    def __repr__(self):
        return "<BinaryOperator(ufunc=%r, uufunc=%r)>" % \
            (self.ufunc, self.uufunc)


def install_numpy_operators():
    numpy_ops = numpy.set_numeric_ops()

    add = BinaryOperator(ufunc=numpy_ops['add'], uufunc=uadd)

    numpy.set_numeric_ops(
        add=add,
    )
