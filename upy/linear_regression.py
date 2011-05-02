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

import upy.core
import numpy

# Reference:
#   Siegfried Gottwald, Herbert K"astner, Helmut Rudolph (Hg.):
#   Meyers kleine Enzyklop"adie Mathematik
#   14., neu bearbeitete und erweiterte Aufl. -
#       Mannheim, Leipzig, Wien, Z"urich: Meyers Lexikonverlag, 1995
#   Abschn. 28.2. Ausgleichsrechnung, S. 659 ff.
#   - Lineare Regression S. 667

__all__ = ['linear_regression']


def linear_regression(x, y, weights = None, dtype = None):
    """Calculates the linear regression of values Y at positions X.  X is
    assumed to be an iterable of arrays of an numeric type, and will be 
    converted into an array of type DTYPE.  Y can be either an iterable of 
    undarrays, or also an iterable of ordinary arrays.  Y will be converted
    into a sequence of upy.undarrays first.  When WEIGHTS is not given, the 
    weights will be derived from the variances of the Y.  If the variance 
    of an Y element is zero, the weight will be set to unity.  WEIGHTS, if 
    given, override the weights derived from variances.  The weights are 
    calculated from variances by 1.0 / ua.variance().  Also, DTYPE can be 
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

    return (upy.undarray(alpha, m_alpha, sigmas = 1),
            upy.undarray(beta, m_beta, sigmas = 1))
