# Maintainer: Friedrich Romstedt <friedrichromstedt@gmail.com>
# Copyright 2010 Friedrich Romstedt
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
# File version: 0.1.0b

import undarray.core
import numpy

__all__ = ['pow', 'sqrt', 'log', 'log10', 'exp', 'sin', 'cos', 'tan', \
		'arcsin', 'arccos', 'arctan']


#
# Power functions ...
#

def pow(a, b):
	a = undarray.core.undarray(a)
	b = undarray.core.undarray(b)
	return a ** b

def sqrt(a):
	a = undarray.core.undarray(a)
	return a ** 0.5

#
# Logarithmic functions ...
#

def log(a):
	a = undarray.core.undarray(a)
	return undarray.core.undarray(
			object = numpy.log(a.value),
			derivatives = [(a, 1.0 / a.value)])

def log10(a):
	return log(a) / numpy.log(10)

def exp(a):
	a = undarray.core.undarray(a)
	exp_a = numpy.exp(a.value)
	return undarray.core.undarray(
			object = exp_a,
			derivatives = [(a, exp_a)])

#
# Trigonometric functions ...
#

def sin(a):
	a = undarray.core.undarray(a)
	return undarray.core.undarray(
			object = numpy.sin(a.value),
			derivatives = [(a, numpy.cos(a.value))])

def cos(a):
	a = undarray.core.undarray(a)
	return undarray.core.undarray(
			object = numpy.cos(a.value),
			derivatives = [(a, -numpy.sin(a.value))])

def tan(a):
	a = undarray.core.undarray(a)
	tan_a = numpy.tan(a.value)
	return undarray.core.undarray(
			object = tan_a,
			derivatives = [(a, 1 + tan_a ** 2)])

def arcsin(a):
	a = undarray.core.undarray(a)
	return undarray.core.undarray(
			object = numpy.arcsin(a.value),
			derivatives = [(a, 1.0 / numpy.sqrt(1 - a.value ** 2))])

def arccos(a):
	a = undarray.core.undarray(a)
	return undarray.core.undarray(
			object = numpy.arccos(a.value),
			derivatives = [(a, -1.0 / numpy.sqrt(1 - a.value ** 2))])

def arctan(a):
	a = undarray.core.undarray(a)
	return undarray.core.undarray(
			object = numpy.arctan(a.value),
			derivatives = [(a, 1.0 / (1 + a.value ** 2))])
