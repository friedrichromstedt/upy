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
# $Last changed: 2010 Feb 2$
# Developed since: Feb 2010
# File version: 0.1.0b

import upy.core
import numpy

# Reference:
#	Siegfried Gottwald, Herbert K"astner, Helmut Rudolph (Hg.):
#	Meyers kleine Enzyklop"adie Mathematik
#	14., neu bearbeitete und erweiterte Aufl. -
#		Mannheim, Leipzig, Wien, Z"urich: Meyers Lexikonverlag, 1995
#	Abschn. 28.2. Ausgleichsrechnung, S. 659 ff.
#	- Lineare Regression S. 667

__all__ = ['linear_regression']


def linear_regression(x, y, weights = None, dtype = None):
	"""Calculates the linear regression of values Y at positions X.  X is
	assumed to be an iterable of arrays of an numeric type, and will be 
	converted into an array of type DTYPE.  Y can be either an iterable of 
	undarrays, or also an iterable of ordinary arrays.  Y will be converted
	into a sequence of upy.undarrays first.  When WEIGHTS is not given, the 
	weights will be derived from the dispersion of the Y.  If the dispersion 
	of an Y element is zero, the weight will be set to unity.  WEIGHTS, if 
	given, override the weights derived from dispersions.  The weights are 
	calculated from dispersion by 1.0 / ua.dispersion().  Also, DTYPE can be 
	given, specifying the dtype of X and Y after conversion."""
	
	# Convert x's elements to a single numpy.ndarrays, if necessary ...

	sequence_x = numpy.asarray(x, dtype = dtype)

	# Convert y's elements to upy.undarrays, if necessary ...

	sequence_y = map(
			lambda element: upy.core.undarray(element, dtype = dtype), y)

	# Extract the number of elements ...
	
	N = len(sequence_y)

	# Do a simple-minded check.  If the shape of the sub-arrays doesn't match,
	# some future call will probably fail to execute.
	assert(len(sequence_x) == len(sequence_y))

	# Extract the nominal values ...

	x_s = sequence_x  # Already ready to be used.
	a_s = numpy.asarray([element.value for element in sequence_y])

	# Extract the weights ...

	if weights is None:
		# Derive the weights from sequence_ua.
		p_s = [ua.weight() for ua in sequence_y]

	else:
		# Use the given weigths.
		p_s = weights
	
	# Convert p_s into a numpy.ndarray for speed ...

	p_s = numpy.asarray(p_s)
	
	# Perform calculation ...

	pa = (p_s * a_s).sum(axis = 0)
	px2 = (p_s * x_s ** 2).sum(axis = 0)
	pax = (p_s * a_s * x_s).sum(axis = 0)
	px = (p_s * x_s).sum(axis = 0)
	p = p_s.sum(axis = 0)

	alpha = (pa * px2 - pax * px) / (p * px2 - px ** 2)
	beta = (pax * p - pa * px) / (p * px2 - px ** 2)

	peps2 = (p_s * (a_s - alpha - beta * x_s) ** 2).sum(axis = 0)

	m = numpy.sqrt(peps2 / float(N - 2))
	m_alpha = m * numpy.sqrt(px2 / (p * px2 - px ** 2))
	m_beta = m * numpy.sqrt(p / (p * px2 - px ** 2))

	return (upy.undarray(alpha, sigma = m_alpha),
			upy.undarray(beta, sigma = m_beta))
