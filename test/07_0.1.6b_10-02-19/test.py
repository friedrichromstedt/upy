# Maintainer: Friedrich Romstedt <friedrichromstedt@gmail.com>
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
# $Last changed: 2010 Feb 19$
# Developed since: Jan 2010
# File version: 0.1.6b

import unittest
import upy
import numpy

class Test(unittest.TestCase):
	"""The test suite for undarray."""

	def test_instantiation_scalar(self):
		"""Test the instantiation from scalars of various types."""

		ua1 = upy.undarray(numpy.asarray(1), numpy.asarray(0.1))

		self.assert_(ua1 == 1)
		self.assert_(ua1.error() == 0.1)
		self.assert_(str(ua1) == '(1.00 +- 0.10)e+000')

		ua2 = upy.undarray(numpy.float32(1), numpy.float32(0.1))

		self.assert_(ua2 == 1)
		# There is a slight difference between numpy.float32 and python float.
		self.assert_(ua2.error() == numpy.float32(0.1))

		ua3 = upy.undarray(1, 0.1)
		self.assert_(ua3 == 1)
		self.assert_(ua3.error() == 0.1)

		ua4 = upy.undarray(numpy.asarray(1))

		ua5 = upy.undarray(numpy.float32(1))

		ua6 = upy.undarray(1)

	def test_instantiation_mixedmode(self):
		"""Test the instantiation of a undarray from a mixedmode object."""

		ua1 = upy.undarray(1, 0.1)
		ua2 = upy.undarray(2, 0.2)
		ua3 = upy.undarray([3, 4], [0.3, 0.4])

		ua = upy.undarray([[ua1, ua2], ua3])
		self.assert_((ua == [[1, 2], [3, 4]]).all())
		self.assert_((ua.error() == [[0.1, 0.2], [0.3, 0.4]]).all())

		ua = upy.undarray([ua3, [ua1, ua2]])
		self.assert_((ua == [[3, 4], [1, 2]]).all())
		self.assert_((ua.error() == [[0.3, 0.4], [0.1, 0.2]]).all())

		ua = upy.undarray([ua3, [1.0, ua2]])
		self.assert_((ua == [[3, 4], [1, 2]]).all())
		self.assert_((ua.error() == [[0.3, 0.4], [0.0, 0.2]]).all())

	def test_instantiation_ndarrays(self):
		"""Test the instantiation from ndarrays."""

		ua = upy.undarray(numpy.asarray([1, 2]), numpy.asarray([0.1, 0.2]))

		self.assert_((ua == [1, 2]).all())
		self.assert_((ua.error() == [0.1, 0.2]).all())

		ua2 = upy.undarray(numpy.asarray([1, 2]))

	def test_instantiation_empty(self):
		"""Test the instantiation from SHAPE."""

		ua = upy.undarray(shape = (2, 2))

		self.assert_((ua == [[0, 0], [0, 0]]).all())
		self.assert_((ua.error() == 0).all())
	
	def test_multiplication_scalar(self):
		"""Test the multiplication of a scalar undarray."""

		en = upy.undarray(1, 0.5)

		self.assert_(str(en * 2) == '(2.0 +- 1.0)e+000')
		self.assert_(str(2 * en) == '(2.0 +- 1.0)e+000')

	def test_addition_scalar(self):
		"""Test scalar addition of independent error sources."""

		en1 = upy.undarray(1, 0.5)
		en2 = upy.undarray(1, 0.5)

		self.assert_(str(en1 + en2) == '(2.00 +- 0.71)e+000')
		self.assert_(str(en1 - en2) == '(0.0 +- 7.1)e-001')
		self.assert_(str(en1 + 1) == '(2.00 +- 0.50)e+000')
		self.assert_(str(1 + en1) == '(2.00 +- 0.50)e+000')

	def test_substraction_identical_scalar(self):
		"""Test substraction of idendical error sources."""

		en = upy.undarray(1, 0.5)
		zero = en - en

		self.assert_(zero.error() == 0.0)

	def test_multiplication_scalar(self):
		"""Test scalar multiplication."""

		en1 = upy.undarray(2, 0.1)
		en2 = upy.undarray(2, 0.1)

		self.assert_(str(en1 * en1) == '(4.00 +- 0.40)e+000')
		self.assert_(str(en1 ** 2) == '(4.00 +- 0.40)e+000')
		self.assert_(str(en1 * en2) == '(4.00 +- 0.29)e+000')

		one = en1 / en1

		self.assert_(one.error() == 0.0)

		self.assert_(str(en1 / en2) == '(1.000 +- 0.071)e+000')
		self.assert_(str(en1 * (1 / en2)) == '(0.0 +- 2.0)e-001')
		self.assert_(str(en1 * (1.0 / en2)) == '(1.000 +- 0.071)e+000')

		self.assert_(str(en1 * 2) == '(4.00 +- 0.20)e+000')
		self.assert_(str(2 * en1) == '(4.00 +- 0.20)e+000')

		self.assert_(str(en1 / 2) == '(1.000 +- 0.050)e+000')
		self.assert_(str(2 / en1) == '(1.00 +- 0.10)e+000')  # unintended
		self.assert_(str(2.0 / en1) == '(1.000 +- 0.050)e+000')

		en3 = upy.undarray(2.0, 0.1)

		self.assert_(str(2 / en3) == '(1.000 +- 0.050)e+000')
		self.assert_(str(2.0 / en3) == '(1.000 +- 0.050)e+000')
	
	def test_pow_scalar(self):
		"""Tests __rpow__()."""

		en1 = upy.undarray(2.0, 0.1)

		self.assert_(str(2 ** en1) == '(4.00 +- 0.28)e+000')
		self.assert_(str(10 ** en1) == '(1.00 +- 0.24)e+002')

	def test_scalar_neg(self):
		"""Test inversion."""

		en1 = upy.undarray(2.0, 0.1)

		self.assert_(str(-en1) == '(-2.00 +- 0.10)e+000')

	def test_scalar_comparison(self):
		"""Tests comparison operators."""

		en1 = upy.undarray(1.0, 0.1)
		en2 = upy.undarray(2.0, 0.1)

		self.assert_(en1 < en2)
		self.assert_(en1 <= en2)
		self.assert_(en1 <= en1)
		self.assert_(en2 > en1)
		self.assert_(en2 >= en1)
		self.assert_(en2 >= en2)
		self.assert_(en1 == en1)
		self.assert_(en1 != en2)

	def test_getitem(self):
		"""Test the itemget."""

		en1 = upy.undarray([2.0, 3.0], [0.1, 0.1])

		self.assert_(en1[0] == upy.undarray(2.0))

		en2 = upy.undarray([[1.0, 2.0], [3.0, 4.0]], 
				numpy.ones(shape = (2, 2)))

		self.assert_((en2[0] == upy.undarray([1.0, 2.0])).all())

	def test_setitem(self):
		"""Test the itemset."""

		en1 = upy.undarray([2.0, 3.0], [0.1, 0.2])
		en1[0] = en1[1]

		self.assert_((en1 == [3.0, 3.0]).all() and
				en1[0].error() == 0.2 and 
				en1[1].error() == 0.2)

		en2 = upy.undarray([[1.0, 2.0], [3.0, 4.0]],
				numpy.ones(shape = (2, 2)))
		en2[0] = en2[1]

		self.assert_((en2 == [[3.0, 4.0], [3.0, 4.0]]).all())

		en3 = upy.undarray([[1, 2], [3, 4]], [[0.1, 0.2], [0.3, 0.4]])
		en4 = upy.undarray([2.0, 3.0], [0.1, 0.2])
		en3[:, 0] = en4

		self.assert_((en3 == [[2, 2], [3, 4]]).all())
		self.assert_((en3.error() == [[0.1, 0.2], [0.2, 0.4]]).all())

		ua5 = upy.undarray([1, 2], [0.1, 0.1])
		ua5[0] = 10
		self.assert_((ua5 == [10, 2]).all())
		self.assert_((ua5.error() == [0, 0.1]).all())

	def test_exceptions(self):
		"""Test some exceptions."""

		try:
			en = upy.undarray([2.0, 3.0], 0.0)
			self.fail()
		except ValueError:
			pass

		en1 = upy.undarray([2.0, 3.0], [0.1, 0.2])

		self.assertRaises(ValueError, en1.get_precision)
		self.assertRaises(ValueError, en1.get_strings)
	
	def test_math(self):
		"""Test the math module."""

		a = upy.undarray(2.0, 0.1)
		b = upy.undarray(1.0, 0.1)
		c = upy.undarray(0.5, 0.1)
		
		self.assert_(str(upy.pow(a, b)) == '(2.00 +- 0.18)e+000')
		self.assert_(str(upy.sqrt(a)) == '(1.414 +- 0.036)e+000')
		self.assert_(str(upy.log(a)) == '(6.93 +- 0.50)e-001')
		self.assert_(str(upy.log10(a)) == '(3.01 +- 0.22)e-001')
		self.assert_(str(upy.exp(a)) == '(7.39 +- 0.74)e+000')
		self.assert_(str(upy.sin(a)) == '(9.09 +- 0.42)e-001')
		self.assert_(str(upy.cos(a)) == '(-4.16 +- 0.91)e-001')
		self.assert_(str(upy.tan(a)) == '(-2.19 +- 0.58)e+000')
		self.assert_(str(upy.arcsin(c)) == '(5.2 +- 1.2)e-001')
		self.assert_(str(upy.arccos(c)) == '(1.05 +- 0.12)e+000')
		self.assert_(str(upy.arctan(c)) == '(4.64 +- 0.81)e-001')
	
	def test_array_same_shape(self):
		"""Test the array functionality for equal-shaped undarrays."""
		
		a = upy.undarray([2.0, 1.0], [0.1, 0.1])
		b = upy.undarray([1.0, 0.5], [0.2, 0.01])

		sum = a + b
		self.assert_(str(sum[0]) == '(3.00 +- 0.23)e+000')
		self.assert_(str(sum[1]) == '(1.50 +- 0.11)e+000')

		diff = a - b  # No fail
		prod = a * b  # No fail
		quot = a / b  # No fail
		pow = a ** b  # No fail

	def test_array_same_shape_exact(self):
		"""Test the array functionality for one exact operand."""

		a = upy.undarray([2.0, 1.0], [0.1, 0.1])
		b = [1.0, 0.5]

		sum = a + b
		sum2 = b + a
		diff = a - b
		diff2 = b - a
		prod = a * b
		prod2 = b * a
		quot = a / b
		quot2 = b / a
		pow = a ** b
		pow2 = b ** a

	def test_array_inequal_shape(self):
		"""Test the array functionality for inequally shaped undarrays."""

		a = upy.undarray([[1.0, 2.0], [3.0, 4.0]], 
				[[0.1, 0.2], [0.3, 0.4]])
		b = upy.undarray([1.0, 2.0], [0.5, 1.0])

		sum = a + b
		self.assert_(str(sum[0, 0]) == '(2.00 +- 0.51)e+000')
		self.assert_(str(sum[0, 1]) == '(4.0 +- 1.1)e+000')
		self.assert_(str(sum[1, 0]) == '(4.00 +- 0.59)e+000')
		self.assert_(str(sum[1, 1]) == '(6.0 +- 1.1)e+000')

		b + a
		a * b
		b * a
		a / b
		b / a
		a ** b
		b ** a

	def test_array_inequal_shape_exact(self):
		"""Test the array functionality for one exact operand and inequally 
		shaped arrays."""

		a = upy.undarray([[1.0, 2.0], [3.0, 4.0]],
				[[0.1, 0.2], [0.3, 0.4]])
		b = [1.0, 2.0]

		a + b
		b + a
		a * b
		b * a
		a / b
		b / a
		a ** b
		b ** a

		c = [[1.0, 2.0], [3.0, 4.0]]
		d = upy.undarray([1.0, 2.0], [0.5, 1.0])

		c + d
		d + c
		c * d
		d * c
		c / d
		d / c
		c ** d
		d ** c
	
	def test_averaging(self):
		"""Test the averaging module."""

		l = [1, 2, 3, 4, 5]
		
		m = upy.mean(l)
		r = upy.representative(l)
		self.assert_(str(m) == '(3.0 +- 1.5)e+000')
		self.assert_(str(r) == '(3.0 +- 2.9)e+000')

		m = upy.mean(l, weights = l, dtype = numpy.float)
		r = upy.representative(l, weights = l, dtype = numpy.float)
		self.assert_(str(m) == '(3.7 +- 1.3)e+000')
		self.assert_(str(r) == '(3.7 +- 2.5)e+000')
		
		l = upy.undarray(range(1, 6), [0.1, 0.2, 0.3, 0.4, 0.5])
		
		m = upy.mean(l)
		r = upy.representative(l)
		self.assert_(str(m) == '(1.56 +- 1.00)e+000')
		self.assert_(str(r) == '(1.6 +- 2.0)e+000')

	def test_weight(self):
		"""Test the .weight() method."""

		ua = upy.undarray([1, 2], [0.0, 1.0])
		weight = ua.weight()

		self.assert_((weight == [1.0, 4.0]).all())

	def test_linear_regression(self):
		"""Test the linear_regression module."""

		# Test with unity-weighted plain numbers ...

		x = [0, 1, 2, 3]
		y = [0, 1, 2, 4]

		(alpha, beta) = upy.linear_regression(x, y)
		self.assert_(str(alpha) == '(-2.0 +- 6.5)e-001')
		self.assert_(str(beta) == '(1.30 +- 0.35)e+000')

		# Test with dynamically-weighted undarray as y ..

		y_ua = upy.undarray([0, 1, 2, 4], [0.1, 0.1, 0.1, 0.9])

		(alpha, beta) = upy.linear_regression(x, y_ua)
		self.assert_(str(alpha) == '(-0.1 +- 1.5)e-001')
		self.assert_(str(beta) == '(1.01 +- 0.11)e+000')

		# Test with static weights ...

		weights = [10, 1, 1, 10]

		(alpha, beta) = upy.linear_regression(x, y_ua, weights = weights, 
				dtype = numpy.float)
		self.assert_(str(alpha) == '(-0.4 +- 3.2)e-001')
		self.assert_(str(beta) == '(1.33 +- 0.15)e+000')
	
	def test_operators_numpyarray(self):
		"""Test the coercion of numpyarray OP upyarray."""

		a1 = numpy.asarray([1.0])
		a2 = numpy.asarray([2.0])
		b1 = upy.undarray([1.0], [0.1])
		b2 = upy.undarray([2.0], [0.1])
		
		# Test add.
		self.assert_(isinstance(a1 + b1, upy.undarray))
		self.assert_(((a1 + b1) == [2]).all())
		
		# Test sub.
		self.assert_(isinstance(a1 - b2, upy.undarray))
		self.assert_(((a1 - b2) == [-1]).all())

		# Test mul.
		self.assert_(isinstance(a1 * b1, upy.undarray))
		self.assert_(((a1 * b1) == [1]).all())

		# Test div.
		self.assert_(isinstance(a1 / b2, upy.undarray))
		self.assert_(((a1 / b2) == [0.5]).all())

		# Test pow.
		self.assert_(isinstance(a2 ** b2, upy.undarray))
		self.assert_(((a2 ** b2) == [4]).all())

		# Test less.
		self.assert_((a1 < b2).all())
		self.assert_(not (a1 < b1).all())

		# Test less_equal.
		self.assert_((a1 <= b2).all())
		self.assert_((a1 <= b1).all())

		# Test greater.
		self.assert_((a2 > b1).all())
		self.assert_(not (a2 > b2).all())

		# Test greater_equal.
		self.assert_((a2 >= b1).all())
		self.assert_((a2 >= b2).all())

		# Test equal.
		self.assert_((a1 == b1).all())

		# Test not_equal.
		self.assert_((a1 != b2).all())


if __name__ == '__main__':
	unittest.main()
