import numpy
from upy2.core import undarray, \
    unegative, uabsolute, \
    uadd, usubtract, umultiply, udivide, \
    upower


class UnaryOperator(object):
    def __init__(self, ufunc, uufunc):
        self.ufunc = ufunc
        self.uufunc = uufunc

    def __call__(self, x, *args, **kwargs):
        if not isinstance(x, undarray):
            return self.ufunc(x, *args, **kwargs)
        else:
            return self.uufunc(x)

    def __getattr__(self, name):
        return getattr(self.ufunc, name)

    def __str__(self):
        return "<upy Unary operator for numpy %s and upy %s>" % \
            (self.ufunc, self.uufunc)

    def __repr__(self):
        return "<UnaryOperator(ufunc=%r, uufunc=%r)>" % \
            (self.ufunc, self.uufunc)


class BinaryOperator(object):
    def __init__(self, ufunc, uufunc):
        self.ufunc = ufunc
        self.uufunc = uufunc

    def __call__(self, x1, x2, *args, **kwargs):
        """ *args* and *kwargs* are only used when calling the numpy
        ufunc. """

        if not isinstance(x1, undarray) and \
                not isinstance(x2, undarray):
            return self.ufunc(x1, x2, *args, **kwargs)
        else:
            return self.uufunc(x1, x2)

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

    negative = UnaryOperator(
            ufunc=numpy_ops['negative'],
            uufunc=unegative)
    absolute = UnaryOperator(
            ufunc=numpy_ops['absolute'],
            uufunc=uabsolute)

    add = BinaryOperator(
            ufunc=numpy_ops['add'],
            uufunc=uadd)
    subtract = BinaryOperator(
            ufunc=numpy_ops['subtract'],
            uufunc=usubtract)
    multiply = BinaryOperator(
            ufunc=numpy_ops['multiply'],
            uufunc=umultiply)
    divide = BinaryOperator(
            ufunc=numpy_ops['divide'],
            uufunc=udivide)
    true_divide = BinaryOperator(
            ufunc=numpy_ops['true_divide'],
            uufunc=udivide)
    power = BinaryOperator(
            ufunc=numpy_ops['power'],
            uufunc=upower)

    numpy.set_numeric_ops(
        negative=negative,
        absolute=absolute,
        add=add,
        subtract=subtract,
        multiply=multiply,
        divide=divide,
        true_divide=true_divide,
        power=power,
    )
