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

import upy.core
import numpy
import warnings

__all__ = ['representative', 'mean']

"""Calculates the mean or the representative of a SEQUENCE of undarrays.  When 
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

# Reference:
#	Siegfried Gottwald, Herbert K"astner, Helmut Rudolph (Hg.):
#	Meyers kleine Enzyklop"adie Mathematik
#	14., neu bearbeitete und erweiterte Aufl. -
#		Mannheim, Leipzig, Wien, Z"urich: Meyers Lexikonverlag, 1995
#	Abschn. 28.2. Ausgleichsrechnung, S. 659 ff.
#	- Konstante Regression S. 663 f.


def representative(sequence, weights = None, dtype = None):
	"""Calculates the representative of a SEQUENCE, with optional WEIGHTS.  
	See the __doc__ string of the upy.averaging module for more 
	information.  DTYPE is the dtype of the arrays used during conversion."""

	warnings.warn("upy.averaging.representative is alpha and experimental.")

	# Convert the sequence's elements to undarrays, if necessary ...

	sequence_ua = map(
			lambda element: upy.core.undarray(element, dtype = dtype), 
			sequence)
	N = len(sequence_ua)

	# Extract the nominal values ...

	a_s = [element.value for element in sequence_ua]

	# Extract the weights ...

	if weights is None:
		# Derive the weights from sequence_ua.
		p_s = [ua.weight() for ua in sequence_ua]

	else:
		# Use the given weigths.
		p_s = weights
	
	# Convert a_s and p_s to numpy.ndarrays for speed.

	a_s = numpy.asarray(a_s)
	p_s = numpy.asarray(p_s)

	# Perform calculation ...

	pa = (p_s * a_s).sum(axis = 0)
	p = p_s.sum(axis = 0)
	y = pa / p

	peps2 = (p_s * (a_s - y) ** 2).sum(axis = 0)
	m_y = numpy.sqrt(peps2 / p)

	return upy.core.undarray(
			object = y,
			uncertainty = m_y,
			sigmas = 1)

def mean(sequence, weights = None, dtype = None):
	"""Calculates the mean of a SEQUENCE, with optional WEIGHTS.  See the
	__doc__ string of the upy.averaging module for more information. 
	DTYPE is the dtype of the arrays used during conversion."""
		
	warnings.warn("upy.averaging.mean is alpha and experimental.")

	N = len(sequence)
	
	repr = representative(sequence, weights = weights, dtype = dtype)

	return upy.core.undarray(
			object = repr.value,
			uncertainty = repr.sigma() / numpy.sqrt(N - 1),
			sigmas = 1)
