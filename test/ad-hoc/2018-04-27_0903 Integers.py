import numpy
import upy2
from upy2 import u, U, undarray
from upy2.typesetting import ScientificTypesetter

upy2.install_numpy_operators()
U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()

ua = u(2)
print "ua =", ua
print "ua.nominal =", ua.nominal
print "ua.dependencies[0].derivatives =", ua.dependencies[0].derivatives
print "ua.dtype =", ua.dtype
print "ua.dependencies[0].dtype =", ua.dependencies[0].dtype
print "ua.stddev =", ua.stddev
print "ua.variance =", ua.variance
