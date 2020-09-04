import numpy
import upy2
from upy2 import u, U
from upy2.typesetting import ScientificTypesetter

U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()

ua = 1 +- u(0.1)

print(10 * ua)
print(ua * 10)

ub = 1 +- u(0.2)

with ScientificTypesetter(stddevs=2, precision=4):
    print(ua * ub)
    print(numpy.sqrt(0.2 ** 2 + 0.1 ** 2))
