import numpy
import upy2
from upy2 import u, U
from upy2.typesetting import ScientificTypesetter

upy2.install_numpy_operators()
U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()

def absolute(x):
    return (x * x.conjugate()) ** 0.5
        # This is possibly complex (but the imaginary component
        # vanishes in all cases covered by this test).

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

numpy.random.seed(0)
def r():
    """ Return a random number from (-1, +1). """
    return(numpy.random.random() - numpy.random.random())
def zr():
    """ Return a complex number with real and imag given by ``r()``. """
    return(r() + 1j * r())
ue = zr() +- u(zr())
UE = absolute(ue)
print "absolute(zrandom +- zrandom), real and imag ="
print UE.real, UE.imag
uf = zr() +- u(zr()) +- u(zr())
UF = absolute(uf)
print "absolute(zrandom +- zrandom +- zrandom), real and imag ="
print UF.real, UF.imag
ug = zr() +- u(zr()) +- u(zr()) +- u(zr())
UG = absolute(ug)
print "absolute(zrandom +- zrandom +- zrandom +- zrandom), real and imag ="
print UG.real, UG.imag

uh = u(1)
UH = absolute(uh)
# This yields RuntimeWarnings.  The following then fails:
# print "absolute(0 +- 1), real and imag ="
# print UH.real, UH.imag
print "nominal and stddev of absolute(0 +- 1).real ="
print UH.real.nominal, UH.real.stddev
    # The stddev is nan

print "absolute(1j) =", absolute(1j)
print "absolute(1) =", absolute(1)

ui = 0.001 +- u(1)
UI = absolute(ui)
print "absolute(0.001 +- 1), real and imag ="
print UI.real, UI.imag

def absolute2(x):
    return x ** 0.5 * x.conjugate() ** 0.5

uj = 1 +- u(0.1)
UJ = absolute2(uj)
print "absolute2(1 +- 0.1), real and imag ="
print UJ.real, UJ.imag

uk = 10 +- u(0.1)
UK = absolute2(uk)
print "absolute2(10 +- 0.1), real and imag ="
print UK.real, UK.imag

uk = zr() +- u(zr()) +- u(zr())
UK = absolute2(uk) 
print "absolute2(zrandom +- zrandom +- zrandom), real and imag ="
print UK.real, UK.imag

ul = 0 +- u(1)
UL = absolute2(ul)
print "nominal and stddev of absolute2(0 +- 1).real ="
print UL.real.nominal, UL.real.stddev
print "nominal and stddev of absolute2(0 +- 1).imag ="
print UL.imag.nominal, UL.imag.stddev
