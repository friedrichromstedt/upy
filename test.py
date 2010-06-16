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

# Developed since: Jan 2010

import unittest
import numpy
import upy
import upy.decimal2
import upy.printable

class TestDecimal2(unittest.TestCase):
	"""Test suite for upy.decimal2."""

	def test_get_leftmost_digit(self):
		"""Test upy.decimal2.DecimalNumber.get_leftmost_digit()."""

		dc1 = upy.decimal2.DecimalNumber(10)
		self.assert_(dc1.get_leftmost_digit().z == 1)

		dc2 = upy.decimal2.DecimalNumber(100)
		self.assert_(dc2.get_leftmost_digit().z == 2)

		dc3 = upy.decimal2.DecimalNumber(0.01)
		self.assert_(dc3.get_leftmost_digit().z == -2)

	def test_str(self):
		"""Test upy.decimal.DecimalNumber.__str__()."""

		dn1 = upy.decimal2.DecimalNumber(1.23, precision = -3)
		self.assert_(str(dn1) == '1.230')

		dn2 = upy.decimal2.DecimalNumber(1.23, precision = 0)
		self.assert_(str(dn2) == '1')

		dn3 = upy.decimal2.DecimalNumber(1.23, precision = -1, ceil = True)
		self.assert_(str(dn3) == '1.3')

		dn4 = upy.decimal2.DecimalNumber(1.23, exponent = 1, precision = -3)
		self.assert_(str(dn4) == '0.123')

		dn5 = upy.decimal2.DecimalNumber(1.23, enforce_sign = True,
				precision = -3)
		self.assert_(str(dn5) == '+1.230')

		dn6 = upy.decimal2.DecimalNumber(1.23, width_sign = 1, precision = -3)
		self.assert_(str(dn6) == ' 1.230')

		dn7 = upy.decimal2.DecimalNumber(1.23, width_left = 2, precision = -3)
		self.assert_(str(dn7) == ' 1.230')

		dn8 = upy.decimal2.DecimalNumber(1, width_point = 1, precision = 0)
		self.assert_(str(dn8) == '1 ')

		dn9 = upy.decimal2.DecimalNumber(1.23, width_right = 5, precision = -3)
		self.assert_(str(dn9) == '1.230  ')

class TestUndarray(unittest.TestCase):
	"""The test suite for undarray."""

	def test_instantiation_scalar(self):
		"""Test the instantiation from scalars of various types."""

		ua1 = upy.undarray(numpy.asarray(1.0), numpy.asarray(0.1))

		self.assert_(ua1 == 1)
		self.assert_(ua1.error() == 0.1)
		self.assert_(str(ua1) == '(1.00 +- 0.10) 10^0 ')

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

		ua = upy.undarray([[1.0, ua2], ua3])
		self.assert_((ua == [[1.0, 2.0], [3.0, 4.0]]).all())
		self.assert_((ua.error() == [[0.0, 0.2], [0.3, 0.4]]).all())

		ua = upy.undarray([[1, ua2], ua3])
		self.assert_((ua == [[1, 2], [3, 4]]).all())
		self.assert_((ua.error() == [[0, 0.2], [0.3, 0.4]]).all())

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

		self.assert_(str(en * 2) == '(2.0 +- 1.0) 10^0 ')
		self.assert_(str(2 * en) == '(2.0 +- 1.0) 10^0 ')

	def test_addition_scalar(self):
		"""Test scalar addition of independent error sources."""

		en1 = upy.undarray(1.0, 0.5)
		en2 = upy.undarray(1.0, 0.5)

		self.assert_(str(en1 + en2) == '(2.00 +- 0.71) 10^0 ')
		self.assert_(str(en1 - en2) == '(0.0 +- 7.1) 10^-1 ')
		self.assert_(str(en1 + 1) == '(2.00 +- 0.50) 10^0 ')
		self.assert_(str(1 + en1) == '(2.00 +- 0.50) 10^0 ')

	def test_substraction_identical_scalar(self):
		"""Test substraction of idendical error sources."""

		en = upy.undarray(1, 0.5)
		zero = en - en

		self.assert_(zero.error() == 0.0)

	def test_multiplication_scalar(self):
		"""Test scalar multiplication."""

		en1 = upy.undarray(2.0, 0.1)
		en2 = upy.undarray(2.0, 0.1)

		self.assert_(str(en1 * en1) == '(4.00 +- 0.40) 10^0 ')
		self.assert_(str(en1 ** 2) == '(4.00 +- 0.40) 10^0 ')
		self.assert_(str(en1 * en2) == '(4.00 +- 0.29) 10^0 ')

		one = en1 / en1

		self.assert_(one.error() == 0.0)

		self.assert_(str(en1 / en2) == '(1.000 +- 0.071) 10^0 ')
		self.assert_(str(en1 * (1 / en2)) == '(1.000 +- 0.071) 10^0 ')
		self.assert_(str(en1 * (1.0 / en2)) == '(1.000 +- 0.071) 10^0 ')

		self.assert_(str(en1 * 2) == '(4.00 +- 0.20) 10^0 ')
		self.assert_(str(2 * en1) == '(4.00 +- 0.20) 10^0 ')

		self.assert_(str(en1 / 2) == '(1.000 +- 0.050) 10^0 ')
		self.assert_(str(2 / en1) == '(1.000 +- 0.050) 10^0 ')
		self.assert_(str(2.0 / en1) == '(1.000 +- 0.050) 10^0 ')

		en3 = upy.undarray(2.0, 0.1)

		self.assert_(str(2 / en3) == '(1.000 +- 0.050) 10^0 ')
		self.assert_(str(2.0 / en3) == '(1.000 +- 0.050) 10^0 ')
	
	def test_pow_scalar(self):
		"""Tests __rpow__()."""

		en1 = upy.undarray(2.0, 0.1)

		self.assert_(str(2 ** en1) == '(4.00 +- 0.28) 10^0 ')
		self.assert_(str(10 ** en1) == '(1.00 +- 0.24) 10^2 ')

	def test_scalar_neg(self):
		"""Test inversion."""

		en1 = upy.undarray(2.0, 0.1)

		self.assert_(str(-en1) == '(-2.00 +- 0.10) 10^0 ')

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

	def test_math(self):
		"""Test the math module."""

		a = upy.undarray(2.0, 0.1)
		b = upy.undarray(1.0, 0.1)
		c = upy.undarray(0.5, 0.1)
		
		self.assert_(str(upy.pow(a, b)) == '(2.00 +- 0.18) 10^0 ')
		self.assert_(str(upy.sqrt(a)) == '(1.414 +- 0.036) 10^0 ')
		self.assert_(str(upy.log(a)) == '(6.93 +- 0.50) 10^-1 ')
		self.assert_(str(upy.log10(a)) == '(3.01 +- 0.22) 10^-1 ')
		self.assert_(str(upy.exp(a)) == '(7.39 +- 0.74) 10^0 ')
		self.assert_(str(upy.sin(a)) == '(9.09 +- 0.42) 10^-1 ')
		self.assert_(str(upy.cos(a)) == '(-4.16 +- 0.91) 10^-1 ')
		self.assert_(str(upy.tan(a)) == '(-2.19 +- 0.58) 10^0 ')
		self.assert_(str(upy.arcsin(c)) == '(5.2 +- 1.2) 10^-1 ')
		self.assert_(str(upy.arccos(c)) == '(1.05 +- 0.12) 10^0 ')
		self.assert_(str(upy.arctan(c)) == '(4.64 +- 0.81) 10^-1 ')

		x = upy.undarray([1, 1, 0, -1, -1, -1,  0,  1], [0.1] * 8)
		y = upy.undarray([0, 1, 1,  1,  0, -1, -1, -1], [0.1] * 8)

		angle = upy.arctan2(y, x)
		self.assert_(str(angle.printable(format = 'float')) == """\
[ 0.00  +- 0.10    0.785 +- 0.071   1.57  +- 0.10    2.356 +- 0.071
  3.14  +- 0.10   -2.356 +- 0.071  -1.57  +- 0.10   -0.785 +- 0.071 ]""")
	
	def test_array_same_shape(self):
		"""Test the array functionality for equal-shaped undarrays."""
		
		a = upy.undarray([2.0, 1.0], [0.1, 0.1])
		b = upy.undarray([1.0, 0.5], [0.2, 0.01])

		sum = a + b
		self.assert_(str(sum[0]) == '(3.00 +- 0.23) 10^0 ')
		self.assert_(str(sum[1]) == '(1.50 +- 0.11) 10^0 ')

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
		self.assert_(str(sum[0, 0]) == '(2.00 +- 0.51) 10^0 ')
		self.assert_(str(sum[0, 1]) == '(4.0 +- 1.1) 10^0 ')
		self.assert_(str(sum[1, 0]) == '(4.00 +- 0.59) 10^0 ')
		self.assert_(str(sum[1, 1]) == '(6.0 +- 1.1) 10^0 ')

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
		self.assert_(str(m) == '(3.0 +- 1.5) 10^0 ')
		self.assert_(str(r) == '(3.0 +- 2.9) 10^0 ')

		m = upy.mean(l, weights = l, dtype = numpy.float)
		r = upy.representative(l, weights = l, dtype = numpy.float)
		self.assert_(str(m) == '(3.7 +- 1.3) 10^0 ')
		self.assert_(str(r) == '(3.7 +- 2.5) 10^0 ')
		
		l = upy.undarray(range(1, 6), [0.1, 0.2, 0.3, 0.4, 0.5])
		
		m = upy.mean(l)
		r = upy.representative(l)
		self.assert_(str(m) == '(1.56 +- 1.00) 10^0 ')
		self.assert_(str(r) == '(1.6 +- 2.0) 10^0 ')

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
		self.assert_(str(alpha) == '(-2.0 +- 6.5) 10^-1 ')
		self.assert_(str(beta) == '(1.30 +- 0.35) 10^0 ')

		# Test with dynamically-weighted undarray as y ..

		y_ua = upy.undarray([0, 1, 2, 4], [0.1, 0.1, 0.1, 0.9])

		(alpha, beta) = upy.linear_regression(x, y_ua)
		self.assert_(str(alpha) == '(-10 +- 150) 10^-3 ')
		self.assert_(str(beta) == '(1.01 +- 0.11) 10^0 ')

		# Test with static weights ...

		weights = [10, 1, 1, 10]

		(alpha, beta) = upy.linear_regression(x, y_ua, weights = weights, 
				dtype = numpy.float)
		self.assert_(str(alpha) == '(-4 +- 32) 10^-2 ')
		self.assert_(str(beta) == '(1.33 +- 0.15) 10^0 ')
	
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

	def test_bugsfixes_reproduction(self):
		"""Tries to reproduce unsorted bugs."""

		# But with "Shape mismatch", due to shape stored as [3] in 
		# Characterstic instead as (3,) ...

		ua1 = upy.undarray([1, 2, 3])
		ua1 ** 2

class TestPrintableElement(unittest.TestCase):
	"""Test the printable element."""

	def test_print(self):
		"""Test the printing engine's precision and exponent determination."""

		p1 = upy.printable.PrintableElement(0.0, 0.0)
		self.assert_(str(p1) == '(0 +- 0) 10^0 ')

		p2 = upy.printable.PrintableElement(0.0, 0.12)
		self.assert_(str(p2) == '(0.0 +- 1.2) 10^-1 ')

		p3 = upy.printable.PrintableElement(0.12, 0)
		self.assert_(str(p3) == \
				'(1.200000000000000 +- 0.000000000000000) 10^-1 ')

		p4 = upy.printable.PrintableElement(0.12, 1.2)
		self.assert_(str(p4) == '(1 +- 12) 10^-1 ')

		p5 = upy.printable.PrintableElement(0.12, 0.12)
		self.assert_(str(p5) == '(1.2 +- 1.2) 10^-1 ')
		
		p6 = upy.printable.PrintableElement(0.12, 0.012)
		self.assert_(str(p6) == '(1.20 +- 0.12) 10^-1 ')

		p7 = upy.printable.PrintableElement(0, 0, format = 'float')
		self.assert_(str(p7) == '0 +- 0 ')

		p8 = upy.printable.PrintableElement(0.12, 0, format = 'float')
		self.assert_(str(p8) == '1.2 +- 0.0 ')

		p9 = upy.printable.PrintableElement(0.12, 1.2, format = 'float')
		self.assert_(str(p9) == '0.1 +- 1.2 ')

		p10 = upy.printable.PrintableElement(0.12, 0.12, format = 'float')
		self.assert_(str(p10) == '0.12 +- 0.12 ')

		p11 = upy.printable.PrintableElement(0, 0)
		self.assert_(str(p11) == '0 +- 0 ')

		p12 = upy.printable.PrintableElement(1, 0)
		self.assert_(str(p12) == '1 +- 0 ')

		p13 = upy.printable.PrintableElement(1234, 0)
		self.assert_(str(p13) == '1234 +- 0 ')

		p14 = upy.printable.PrintableElement(1234, 560)
		self.assert_(str(p14) == '1230 +- 560 ')

		p15 = upy.printable.PrintableElement(1, 1)
		self.assert_(str(p15) == '1 +- 1 ')
		
		# Test autodetermination of format ...

		p16 = upy.printable.PrintableElement(10, 1)
		self.assert_(str(p16) == '10 +- 1 ')

		p17 = upy.printable.PrintableElement(10, 1.0)
		self.assert_(str(p17) == '(1.00 +- 0.10) 10^1 ')

		p18 = upy.printable.PrintableElement(10.0, 1)
		self.assert_(str(p18) == '(1.00 +- 0.10) 10^1 ')

		p19 = upy.printable.PrintableElement(10.0, 1.0)
		self.assert_(str(p19) == '(1.00 +- 0.10) 10^1 ')

		p20 = upy.printable.PrintableElement(10, 0)
		self.assert_(str(p20) == '10 +- 0 ')
		
		p21 = upy.printable.PrintableElement(10.0, 0)
		self.assert_(str(p21) == 
				'(1.000000000000000 +- 0.000000000000000) 10^1 ')

		p22 = upy.printable.PrintableElement(0, 0)
		self.assert_(str(p22) == '0 +- 0 ')

		p23 = upy.printable.PrintableElement(0.0, 0)
		self.assert_(str(p23) == '(0 +- 0) 10^0 ')

		p24 = upy.printable.PrintableElement(0, 1)
		self.assert_(str(p24) == '0 +- 1 ')

		p25 = upy.printable.PrintableElement(0, 1.0)
		self.assert_(str(p25) == '(0.0 +- 1.0) 10^0 ')

		p26 = upy.printable.PrintableElement(0.0, 1)
		self.assert_(str(p26) == '(0.0 +- 1.0) 10^0 ')

		p27 = upy.printable.PrintableElement(0.0, 1.0)
		self.assert_(str(p27) == '(0.0 +- 1.0) 10^0 ')
	
	def test_sign_print(self):
		"""Test the sign printing."""

		p1 = upy.printable.PrintableElement(-0.12, 0.12)
		self.assert_(str(p1) == '(-1.2 +- 1.2) 10^-1 ')

		p2 = upy.printable.PrintableElement(-0.12, 0.12, format = 'float')
		self.assert_(str(p2) == '-0.12 +- 0.12 ')

		p3 = upy.printable.PrintableElement(0.12, 0.12, 
				enforce_sign_value = True)
		self.assert_(str(p3) == '(+1.2 +- 1.2) 10^-1 ')

		p4 = upy.printable.PrintableElement(0.12, 0.12, format = 'float',
				enforce_sign_value = True)
		self.assert_(str(p4) == '+0.12 +- 0.12 ')

		p5 = upy.printable.PrintableElement(12, 0.12,
				enforce_sign_exponent = True)
		self.assert_(str(p5) == '(1.200 +- 0.012) 10^+1 ')

		p6 = upy.printable.PrintableElement(12, 0.12, format = 'float',
				enforce_sign_exponent = True)
		self.assert_(str(p6) == '12.00 +- 0.12 ')


class TestPrintableUndarray(unittest.TestCase):
	"""Tests the upy.printable.PrintableUndarray class."""

	def test_print(self):
		"""Test printing ndim = 2 undarrays."""

		ua = upy.undarray([[10, 0.1], [0.01, 1]], [[0.1, 1], [0.01, 10]])

		self.assert_(str(ua) == \
"""\
[[(1.000 +-  0.011) 10^ 1  (1     +- 10    ) 10^-1 ]
 [(1.0   +-  1.0  ) 10^-2  (1     +- 10    ) 10^ 0 ]]""")
 		
		self.assert_(str(ua.printable(format = 'float')) == \
"""\
[[10.00  +-  0.10    0.1   +-  1.0   ]
 [ 0.010 +-  0.010   1     +- 10     ]]""")

 		self.assert_(str(ua.printable(enforce_sign_exponent = True)) == \
"""\
[[(1.000 +-  0.011) 10^+1  (1     +- 10    ) 10^-1 ]
 [(1.0   +-  1.0  ) 10^-2  (1     +- 10    ) 10^+0 ]]""")
 		
		self.assert_(str(ua.printable(enforce_sign_value = True)) == \
"""\
[[(+1.000 +-  0.011) 10^ 1  (+1     +- 10    ) 10^-1 ]
 [(+1.0   +-  1.0  ) 10^-2  (+1     +- 10    ) 10^ 0 ]]""")

		self.assert_(str(ua.printable(precision = 1)) == """\
[[( 1.00 +-  0.02) 10^ 1  (00    +- 10   ) 10^-1 ]
 [( 1    +-  1   ) 10^-2  (00    +- 10   ) 10^ 0 ]]""")

		ua2 = upy.undarray(1.23456789, 0)

		self.assert_(str(ua2.printable(infinite_precision = 4)) == \
				"(1.2346 +- 0.0000) 10^0 ")

		self.assert_(str(ua2) == \
				"(1.234567890000000 +- 0.000000000000000) 10^0 ")

		ua3 = upy.undarray(1234, 560)
		self.assert_(str(ua3.printable(format = 'int')) == '1230 +- 560 ')

		ua4 = upy.undarray(1234, 0)
		self.assert_(str(ua4.printable(format = 'int')) == '1234 +- 0 ')

if __name__ == '__main__':
	unittest.main()
