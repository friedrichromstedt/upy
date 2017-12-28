import numpy
import upy2
from upy2 import u, U
from upy2.typesetting import ScientificTypesetter

U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()

wavelength = 420 +- u(10)
print wavelength
print wavelength ** 0.5

print "-----"

compound = numpy.asarray([10, 11]) +- u([1, 2])
print compound

print "-----"
upy2.install_numpy_operators()

compound2 = numpy.asarray([[100], [42]]) +- u([[1], [1.5]])
print compound2
