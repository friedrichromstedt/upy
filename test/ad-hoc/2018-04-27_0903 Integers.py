import numpy
import upy2
from upy2 import u, U, undarray
from upy2.typesetting import ScientificTypesetter

U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()

# This script ceases to produce integer errors since b35d02b77c8.  This
# is not a bug, but a feature.

ua = u(2)
print("ua =", ua)
print("ua.nominal =", ua.nominal)
print("ua.dependencies[0].derivatives =", ua.dependencies[0].derivatives)
print("ua.dtype =", ua.dtype)
print("ua.dependencies[0].dtype =", ua.dependencies[0].dtype)
print("ua.stddev =", ua.stddev)
print("ua.variance =", ua.variance)
