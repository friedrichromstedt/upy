import numpy
from upy2.core import undarray, \
    upositive, unegative, uabsolute, \
    usqrt, usquare, \
    uadd, usubtract, umultiply, udivide, \
    upower


class UnaryOperator(object):
    def __init__(self, ufunc, uufunc):
        self.ufunc = ufunc
        self.uufunc = uufunc

    def __call__(self, x, *args, **kwargs):
        """ *args* nad **kwargs** are used only when calling the numpy
        ufunc. """

        if not isinstance(x, undarray):
            return self.ufunc(x, *args, **kwargs)
        else:
            return self.uufunc(x)

    def __getattr__(self, name):
        """ Forwards the attribute request to the ufunc contained. """

        return getattr(self.ufunc, name)

    def __str__(self):
        return "<upy unary operator for numpy {0} and upy {1}>".\
                format(self.ufunc, self.uufunc)

    def __repr__(self):
        return "<UnaryOperator(ufunc={0!r}, uufunc={1!r})>".\
                format(self.ufunc, self.uufunc)


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
        return "<upy binary operator for numpy {0} and upy {1}>".\
                format(self.ufunc, self.uufunc)

    def __repr__(self):
        return "<BinaryOperator(ufunc={0!r}, uufunc={1!r})>".\
                format(self.ufunc, self.uufunc)


def install_numpy_operators():
    numpy_ops = numpy.set_numeric_ops()

    positive = UnaryOperator(
            ufunc=numpy_ops['positive'],
            uufunc=upositive)
    negative = UnaryOperator(
            ufunc=numpy_ops['negative'],
            uufunc=unegative)
    absolute = UnaryOperator(
            ufunc=numpy_ops['absolute'],
            uufunc=uabsolute)

    sqrt = UnaryOperator(
            ufunc=numpy_ops['sqrt'],
            uufunc=usqrt)
    square = UnaryOperator(
            ufunc=numpy_ops['square'],
            uufunc=usquare)

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
        positive=positive,
        negative=negative,
        absolute=absolute,
        sqrt=sqrt,
        square=square,
        add=add,
        subtract=subtract,
        multiply=multiply,
        divide=divide,
        true_divide=true_divide,
        power=power,
    )
