import numpy
import upy2
from upy2 import u, U
from upy2.typesetting import ScientificTypesetter

upy2.install_numpy_operators()
U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()

def absolute(x):
    return (x * x.conj()) ** 0.5

print "absolute(1 +- u(0.2)) ="
print absolute(1 +- u(0.2))
print "absolute(-1 +- u(0.2)) ="
print absolute(-1 +- u(0.2))

ua = -1 +- u(0.2)
print "ua + absolute(ua) ="
print ua + absolute(ua)

ub = 1j +- u(0.2j)
UB = absolute(ub)
print "absolute(1j +- 0.2j), real and imag ="
print UB.real, UB.imag

uc = 1j +- u(0.2)
UC = absolute(uc)
print "absolute(1j +- 0.2), real and imag ="
print UC.real, UC.imag

ud1 = 1 + 1j +- u(0.2)
ud2 = 1 + 1j +- u(0.2j)
UD1 = absolute(ud1)
UD2 = absolute(ud2)
print "absolute(1 + 1j +- u(0.2), real and imag ="
print UD1.real, UD1.imag
print "absolute(1 + 1j +- u(0.2j), real and imag ="
print UD2.real, UD2.imag
