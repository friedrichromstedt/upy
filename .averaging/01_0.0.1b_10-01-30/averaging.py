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
# File version: 0.0.1b

import undarray.core

"""Computes the mean or the representative of a SEQUENCE of undarrays.  When 
keeping the spread of the samples constant, the mean() will become more 
precise when the number of samples grows, while the representative will have 
for all sample numbers the same uncertainty.  Optionally the WEIGHTS can be 
given, overriding the weights derived from the sequence.  SEQUENCE may be an 
undarray, in this case it is treated as a list of sub-undarrays.  In fact, 
any object supporting the container protocol can be used.  If SEQUENCE 
consists of single undarrays, they are assumed to have equal shape.  Each 
element of SEQUENCE will be converted into an undarray first, i.e., if plain 
numbers of numpy.ndarrays are given, they will result in precise undarrays.  
The default weight for precise undarrays in the SEQUENCE is 1.0.  Note that 
this may result in unexpected behaviour if your SEQUENCE contains both 
uncertain and exact undarrays.  The default weight for uncertain undarrays in 
the SEQUENCE is 1.0 / ua.dispersion().
"""

def mean(sequence, weights = None):
	"""Calculates the mean of a SEQUENCE, with optional WEIGHTS.  See the
	__doc__ string of the undarray.averaging module for more information."""

	n = 
