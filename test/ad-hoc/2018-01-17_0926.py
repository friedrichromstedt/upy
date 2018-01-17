import numpy
import upy2
from upy2 import u, U
from upy2.typesetting import ScientificTypesetter

upy2.install_numpy_operators()
U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()

ua = numpy.asarray([10, 11]) +- u([1, 1.5])
print ua

ub = numpy.asarray([[10], [11]]) +- u([[1], [0.15]])
print ub

print upy2.uadd
