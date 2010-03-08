# Maintainer: Friedrich Romstedt <friedrichromstedt@gmail.com>
# Copyright 2008, 2009, 2010 Friedrich Romstedt
#    This file is part of undarray.
#
#    undarray is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    undarray is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with undarray.  If not, see <http://www.gnu.org/licenses/>.
# $Last changed: 2010 Jan 30$
# Developed since: Jan 2010
# File version: 0.1.1b

import unittest
import undarray
import numpy

class Test(unittest.TestCase):
	"""The test suite for undarray."""

	def test_instantiation_scalar(self):
		"""Test the instantiation of a scalar undarray."""

		en = undarray.undarray(1, 0.5)

		self.assert_(str(en) == '(1.00 +- 0.50)e+000')

		en = undarray.undarray([1.0, 2.0])

		self.assert_(str(en) == '(1-dimensional undarray with shape (2,))')

	def test_multiplication_scalar(self):
		"""Test the multiplication of a scalar undarray."""

		en = undarray.undarray(1, 0.5)

		self.assert_(str(en * 2) == '(2.0 +- 1.0)e+000')
		self.assert_(str(2 * en) == '(2.0 +- 1.0)e+000')

	def test_addition_scalar(self):
		"""Test scalar addition of independent error sources."""

		en1 = undarray.undarray(1, 0.5)
		en2 = undarray.undarray(1, 0.5)

		self.assert_(str(en1 + en2) == '(2.00 +- 0.71)e+000')
		self.assert_(str(en1 - en2) == '(0.0 +- 7.1)e-001')
		self.assert_(str(en1 + 1) == '(2.00 +- 0.50)e+000')
		self.assert_(str(1 + en1) == '(2.00 +- 0.50)e+000')

	def test_substraction_identical_scalar(self):
		"""Test substraction of idendical error sources."""

		en = undarray.undarray(1, 0.5)
		zero = en - en

		self.assert_(zero.error() == 0.0)

	def test_multiplication_scalar(self):
		"""Test scalar multiplication."""

		en1 = undarray.undarray(2, 0.1)
		en2 = undarray.undarray(2, 0.1)

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

		en3 = undarray.undarray(2.0, 0.1)

		self.assert_(str(2 / en3) == '(1.000 +- 0.050)e+000')
		self.assert_(str(2.0 / en3) == '(1.000 +- 0.050)e+000')
	
	def test_pow_scalar(self):
		"""Tests __rpow__()."""

		en1 = undarray.undarray(2.0, 0.1)

		self.assert_(str(2 ** en1) == '(4.00 +- 0.28)e+000')
		self.assert_(str(10 ** en1) == '(1.00 +- 0.24)e+002')

	def test_scalar_neg(self):
		"""Test inversion."""

		en1 = undarray.undarray(2.0, 0.1)

		self.assert_(str(-en1) == '(-2.00 +- 0.10)e+000')

	def test_scalar_comparison(self):
		"""Tests comparison operators."""

		en1 = undarray.undarray(1.0, 0.1)
		en2 = undarray.undarray(2.0, 0.1)

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

		en1 = undarray.undarray([2.0, 3.0], [0.1, 0.1])

		self.assert_(en1[0] == undarray.undarray(2.0))

		en2 = undarray.undarray([[1.0, 2.0], [3.0, 4.0]], 
				numpy.ones(shape = (2, 2)))

		self.assert_((en2[0] == undarray.undarray([1.0, 2.0])).all())

	def test_setitem(self):
		"""Test the itemset."""

		en1 = undarray.undarray([2.0, 3.0], [0.1, 0.2])
		en1[0] = en1[1]

		self.assert_((en1 == [3.0, 3.0]).all() and
				en1[0].error() == 0.2 and 
				en1[1].error() == 0.2)

		en2 = undarray.undarray([[1.0, 2.0], [3.0, 4.0]],
				numpy.ones(shape = (2, 2)))
		en2[0] = en2[1]

		self.assert_((en2 == [[3.0, 4.0], [3.0, 4.0]]).all())

	def test_exceptions(self):
		"""Test some exceptions."""

		try:
			en = undarray.undarray([2.0, 3.0], 0.0)
			self.fail()
		except ValueError:
			pass

		en1 = undarray.undarray([2.0, 3.0], [0.1, 0.2])

		self.assertRaises(ValueError, en1.get_precision)
		self.assertRaises(ValueError, en1.get_strings)
	
	def test_math(self):
		"""Test the math module."""

		a = undarray.undarray(2.0, 0.1)
		b = undarray.undarray(1.0, 0.1)
		c = undarray.undarray(0.5, 0.1)
		
		self.assert_(str(undarray.pow(a, b)) == '(2.00 +- 0.18)e+000')
		self.assert_(str(undarray.sqrt(a)) == '(1.414 +- 0.036)e+000')
		self.assert_(str(undarray.log(a)) == '(6.93 +- 0.50)e-001')
		self.assert_(str(undarray.log10(a)) == '(3.01 +- 0.22)e-001')
		self.assert_(str(undarray.exp(a)) == '(7.39 +- 0.74)e+000')
		self.assert_(str(undarray.sin(a)) == '(9.09 +- 0.42)e-001')
		self.assert_(str(undarray.cos(a)) == '(-4.16 +- 0.91)e-001')
		self.assert_(str(undarray.tan(a)) == '(-2.19 +- 0.58)e+000')
		self.assert_(str(undarray.arcsin(c)) == '(5.2 +- 1.2)e-001')
		self.assert_(str(undarray.arccos(c)) == '(1.05 +- 0.12)e+000')
		self.assert_(str(undarray.arctan(c)) == '(4.64 +- 0.81)e-001')
	
	def test_array_same_shape(self):
		"""Test the array functionality for equal-shaped undarrays."""
		
		a = undarray.undarray([2.0, 1.0], [0.1, 0.1])
		b = undarray.undarray([1.0, 0.5], [0.2, 0.01])

		sum = a + b
		self.assert_(str(sum[0]) == '(3.00 +- 0.23)e+000')
		self.assert_(str(sum[1]) == '(1.50 +- 0.11)e+000')

		diff = a - b  # No fail
		prod = a * b  # No fail
		quot = a / b  # No fail
		pow = a ** b  # No fail

	def test_array_same_shape_exact(self):
		"""Test the array functionality for one exact operand."""

		a = undarray.undarray([2.0, 1.0], [0.1, 0.1])
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

		a = undarray.undarray([[1.0, 2.0], [3.0, 4.0]], 
				[[0.1, 0.2], [0.3, 0.4]])
		b = undarray.undarray([1.0, 2.0], [0.5, 1.0])

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

		a = undarray.undarray([[1.0, 2.0], [3.0, 4.0]],
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
		d = undarray.undarray([1.0, 2.0], [0.5, 1.0])

		c + d
		d + c
		c * d
		d * c
		c / d
		d / c
		c ** d
		d ** c


if __name__ == '__main__':
	unittest.main()
