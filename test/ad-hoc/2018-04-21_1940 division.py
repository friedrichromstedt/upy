import numpy
import upy2
from upy2 import u, U, undarray
from upy2.typesetting import ScientificTypesetter

upy2.install_numpy_operators()
U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()

ua = 10 +- u(2)
print "ua =", ua

print "Testing uncertainty annihilation:"
print "(ua / ua).nominal =", (ua / ua).nominal
print "(ua / ua).stddev =", (ua / ua).stddev
# print ua / ua

print "Testing conservation of relative error on inversion:"
print "1 / ua =", 1 / ua

print "Testing behaviour with an empty undarray as first operand:"
uzero = undarray(2)
print "uzero =", uzero
print "uzero / ua =", uzero / ua

print "Testing addition of relative variances:"
ub = 2 +- u(0.5)
print "ub =", ub
rela = 2 * ua.stddev / ua.nominal
relb = 2 * ub.stddev / ub.nominal
print "rela =", rela
print "relb =", relb
uresult = ua / ub
relresult = 2 * uresult.stddev / uresult.nominal
print "relresult =", relresult
relexpected = numpy.sqrt(rela ** 2 + relb ** 2)
print "relexpected =", relexpected
