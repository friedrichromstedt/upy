# Developed since: Feb 2010
""" Overloads the numpy operators in such a way, that the
implementations of binary operations in :class:`undarray` have highest
precedence. """


import numpy
from upy2.core import undarray

__all__ = ['add', 'subtract', 'multiply', 'divide', 'power', \
        'less', 'less_equal', 'greater', 'greater_equal', 'equal', \
        'not_equal']

# Arithmetic operators ...

# We store the original numpy settings and then create the callable
# objects, which take their .ufunc attribute from this array.
original_numpy_ops = numpy.set_numeric_ops()

class Shadow(object):
    """ :class:`Shadow` instances can be called to implement a binary
    operation originally implemented by a ``numpy`` ufunc.  This
    ``numpy`` ufunc will be shadowed by the implementation provided by
    an ``undarray`` instance given as the second operand. """

    def __init__(self, ufunc, shadow_by):
        """ *ufunc* is the name of the ``numpy`` ufunc to be shadowed.
        *shadow_by* is the name of the undarray method to be used to
        shadow the numpy ufunc. """

        self.ufunc_name = ufunc
        self.ufunc = original_numpy_ops[ufunc]
        self.shadow_by = shadow_by

    def __call__(self, a, b, *args, **kwargs):
        """ When *b* is an ``undarray`` instance, its shadowing method
        will be used to implement the call.  Otherwise, the original
        ufunc will be called.

        Optional positional and keyword arguments aside of *a* and *b*
        will be handed over to the original ufunc when it is called.
        
        When the shadowing method of the ``undarray`` instance *b* is
        used to implement the call, *a* will be the only argument; all
        optional positional and all keyword argument will be
        discarded. """

        if isinstance(b, undarray):
            return getattr(b, self.shadow_by)(a)
        else:
            return self.ufunc(a, b, *args, **kwargs)

    def __getattr__(self, attr):
        """Return getattr(.ufunc, ATTR)."""

        return getattr(self.ufunc, attr)
    
    def __str__(self):
        
        return "(ufunc wrapper for %s)" % self.ufunc
    
    def __repr__(self):
            
        return "Shadow(ufunc_name=%r, shadow=%r)" % \
                (self.ufunc_name, self.shadow)

class Add(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'add', '__radd__')

add = Add()

class Subtract(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'subtract', '__rsub__')

subtract = Subtract()

class Multiply(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'multiply', '__rmul__')

multiply = Multiply()

class Divide(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'divide', '__rdiv__')

divide = Divide()

class Power(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'power', '__rpow__')

power = Power()

# Comparison operators ...
#
# Note that for the antisymmetric operators the called operators are the 
# inverted of the original due to position swap.

class Less(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'less', '__gt__')

less = Less()

class LessEqual(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'less_equal', '__ge__')

less_equal = LessEqual()

class Greater(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'greater', '__lt__')

greater = Greater()

class GreaterEqual(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'greater_equal', '__le__')

greater_equal = GreaterEqual()

class Equal(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'equal', '__eq__')

    def __call__(self, a, b, *args, **kwargs):
        # numpy's calling mechanism of equal() seems to have a bug,
        # such that b is always a numpy.ndarray.  When b should be an undarray,
        # it is a numpy.ndarray(dtype = numpy.object, shape = ()) ...

        # Make the call also compatible with future, bug-fixed versions.
        if isinstance(b, numpy.ndarray):
            if b.ndim == 0:
                # Implement some conversion from scalar array to stored object.
                b = b.sum()
        
        return ufuncWrap.__call__(self, a, b, *args, **kwargs)

equal = Equal()

class NotEqual(ufuncWrap):
    def __init__(self):
        ufuncWrap.__init__(self, 'not_equal', '__ne__')

    def __call__(self, a, b, *args, **kwargs):
        # numpy's calling mechanism of not_equal() seems to have a bug,
        # such that b is always a numpy.ndarray.  When b should be an undarray,
        # it is a numpy.ndarray(dtype = numpy.object, shape = ()) ...

        # Make the call also compatible with future, bug-fixed versions.
        if isinstance(b, numpy.ndarray):
            if b.ndim == 0:
                # Implement some conversion from scalar array to stored object.
                b = b.sum()
        
        return ufuncWrap.__call__(self, a, b, *args, **kwargs)

not_equal = NotEqual()

# Register the operators in numpy ...

numpy.set_numeric_ops(
        add = add,
        subtract = subtract,
        multiply = multiply,
        divide = divide,
        power = power,
        less = less,
        less_equal = less_equal,
        greater = greater,
        greater_equal = greater_equal,
        equal = equal,
        not_equal = not_equal)
