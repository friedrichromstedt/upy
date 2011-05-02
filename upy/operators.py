# Copyright (c) 2010 Friedrich Romstedt <friedrichromstedt@gmail.com>
# See also <www.friedrichromstedt.org> (if e-mail has changed)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Developed since: Feb 2010

import numpy
import upy.core

__all__ = ['add', 'subtract', 'multiply', 'divide', 'power', \
        'less', 'less_equal', 'greater', 'greater_equal', 'equal', \
        'not_equal']

"""Overloads the numpy operators in such a way, that in expressions
undarrays have the highest precedence."""

#
# Explicit operators ...
#
# Consider the expression:
#
#   numpyarray * upyarray
#
# When executing this, NUMPYARRAY.__mul__() is called, or, equivalently,
# numpy.multiply().  This function checkes whether the other operand is an
# numpy.ndarray, and if not, it treats it as scalar and applies the operation
# to all elements of the numpy.ndararray NUMPYARRAY.  This is not what was
# expected.  The call executes properly if upyarray.__rmul__() is being 
# called, which is done by the wrapper functions below.  The wrapper
# functions only handle this special case, all other cases are handed over to
# numpy functions.  The wrapper functions are registered in numpy via
# numpy.set_arithmetic_ops().

# Arithmetic operators ...

# We store the original numpy settings, then create the callable objects,
# which take their .ufunc attribute from this array.
original_numpy_ops = numpy.set_numeric_ops()

class ufuncWrap:
    """Wraps numpy ufuncs.  Behaves like the original, with the exception
    that __call__() will be overloaded."""

    def __init__(self, ufunc_name, overload):
        """UFUNC is the ufunc to be wrapped.  OVERLOAD is the name (string)
        of the undarray method to be used in overloading __call__()."""

        self.ufunc_name = ufunc_name
        self.ufunc = original_numpy_ops[ufunc_name]
        self.overload = overload

    def __call__(self, a, b, *args, **kwargs):
        """When B is an undarray, call B.overload(a), else .ufunc(a, b)."""

        if isinstance(b, upy.core.undarray):
            return getattr(b, self.overload)(a)
        else:
            return self.ufunc(a, b, *args, **kwargs)

    def __getattr__(self, attr):
        """Return getattr(.ufunc, ATTR)."""

        return getattr(self.ufunc, attr)
    
    def __str__(self):
        
        return "(ufunc wrapper for %s)" % self.ufunc
    
    def __repr__(self):
            
        return "ufuncWrap(ufunc_name = %r, overload = %r)" % \
                (self.ufunc_name, self.overload)

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
