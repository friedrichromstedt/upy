import numpy
import upy2
from upy2 import u, U
from upy2.typesetting import ScientificTypesetter

upy2.install_numpy_operators()
U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()

ua = 10 +- u(1)
print "nominal", (ua / ua).nominal
print "stddev", (ua / ua).stddev
# print ua / ua
