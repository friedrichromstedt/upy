# Maintainer: Friedrich Romstedt <www.friedrichromstedt.org>
# Copyright 2008, 2009, 2010 Friedrich Romstedt
#    This file is part of upy.
#
#    upy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    upy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with upy.  If not, see <http://www.gnu.org/licenses/>.
# $Last changed: 2010 Feb 14$
# Developed since: Feb 2010
# File version: 0.1.0b

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
#	numpyarray * upyarray
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
