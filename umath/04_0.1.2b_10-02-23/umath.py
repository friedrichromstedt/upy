# Maintainer: Friedrich Romstedt <friedrichromstedt@gmail.com>
# Copyright 2010 Friedrich Romstedt
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
# $Last changed: 2010 Feb 23$
# Developed since: Jan 2010
# File version: 0.1.2b

import upy.core
import numpy

__all__ = ['pow', 'sqrt', 'log', 'log10', 'exp', 'sin', 'cos', 'tan', \
		'arcsin', 'arccos', 'arctan', 'arctan2']


#
# Power functions ...
#

def pow(a, b):
	a = upy.core.undarray(a)
	b = upy.core.undarray(b)
	return a ** b

def sqrt(a):
	a = upy.core.undarray(a)
	return a ** 0.5

#
# Logarithmic functions ...
#

def log(a):
	a = upy.core.undarray(a)
	return upy.core.undarray(
			object = numpy.log(a.value),
			derivatives = [(a, 1.0 / a.value)])

def log10(a):
	return log(a) / numpy.log(10)

def exp(a):
	a = upy.core.undarray(a)
	exp_a = numpy.exp(a.value)
	return upy.core.undarray(
			object = exp_a,
			derivatives = [(a, exp_a)])

#
# Trigonometric functions ...
#

def sin(a):
	a = upy.core.undarray(a)
	return upy.core.undarray(
			object = numpy.sin(a.value),
			derivatives = [(a, numpy.cos(a.value))])

def cos(a):
	a = upy.core.undarray(a)
	return upy.core.undarray(
			object = numpy.cos(a.value),
			derivatives = [(a, -numpy.sin(a.value))])

def tan(a):
	a = upy.core.undarray(a)
	tan_a = numpy.tan(a.value)
	return upy.core.undarray(
			object = tan_a,
			derivatives = [(a, 1 + tan_a ** 2)])

def arcsin(a):
	a = upy.core.undarray(a)
	return upy.core.undarray(
			object = numpy.arcsin(a.value),
			derivatives = [(a, 1.0 / numpy.sqrt(1 - a.value ** 2))])

def arccos(a):
	a = upy.core.undarray(a)
	return upy.core.undarray(
			object = numpy.arccos(a.value),
			derivatives = [(a, -1.0 / numpy.sqrt(1 - a.value ** 2))])

def arctan(a):
	a = upy.core.undarray(a)
	return upy.core.undarray(
			object = numpy.arctan(a.value),
			derivatives = [(a, 1.0 / (1 + a.value ** 2))])

def arctan2(y, x):
	
	#                    +-------------+
	# 3\           /1    |           / |
	#   3\   2   /1      |atan(x/y)/   |
	#     3\   /1        |       /     |
	#   3    x0   1     y|     /       |
	#     3/   \1        |   /         |
	#   3/   4   \1      | / atan(y/x) |
	# 3/           \1    +-------------+
	#                           x
	#
	# The numbers at the lines indicate to which set the respective line
	# belongs.  Note that there is a 0 in the center.  This set consists of
	# only one point.

	xabs = abs(x)
	yabs = abs(y)

	# Calculate masks coding the portions of the undarray which lie in section
	# 1, 2, 3, or 4.  A mask for the 0 set isn't needed, because the
	# corresponding angle is zero anyway ...

	mask1 = (x > 0) * (xabs >= yabs)
	mask2 = (y > 0) * (yabs > xabs)
	mask3 = (x < 0) * (xabs >= yabs)
	mask4 = (y < 0) * (yabs > xabs)

	# Calculate the angles with arctan assuming that each points lies in the
	# respective set ...
	#
	# Thereby add bogus data to the x and y arrays when one coordinate is
	# zero and would lead to NaNs.  NaNs are flags and are not eliminated by
	# the multiplication with the mask.  Thus they must be avoided from the
	# beginning.

	# When the point is in set 1, the angle fulfils the boundary condition
	# -numpy.pi < angle <= numpy.pi.
	angle1 = arctan(y / (x + (x == 0)))

	# When the point is in set 2, the angle fulfils the boundary condition.
	angle2 = numpy.pi / 2 - arctan(x / (y + (y == 0)))

	angle3 = angle1 + numpy.pi
	# Make shure that -numpy.pi < angle <= numpy.pi
	angle3 -= 2 * numpy.pi * (angle3 > numpy.pi)

	# When the point is in set 4, the angle fulfils the boundary condition.
	angle4 = angle2 - numpy.pi

	# Comprise the full set 0 + 1 + 2 + 3 + 4 from the masks ...
	#
	# We don't need to cover set 0, because the corresponding angle is zero.

	angle = mask1 * angle1 + mask2 * angle2 + \
			mask3 * angle3 + mask4 * angle4

	return angle
