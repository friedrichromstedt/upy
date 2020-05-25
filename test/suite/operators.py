# Developed since: May 2020

import random
import unittest
import numpy
import upy2
from upy2 import u, U, undarray


class TestOperators(unittest.TestCase):
    def __init__(self, name):
        unittest.TestCase.__init__(self, name)
        self.U = U(1)

    def setUp(self):
        self.U.register()

    def tearDown(self):
        self.U.unregister()

    # Providers for tuples ``(nominal value, uncertainty)``.  The
    # ``uncertainty`` is a normally distributed random variable
    # always; there are several options for the distribution of the
    # ``nominal value`` ...

    def gauss(self):
        return (random.gauss(0, 1), random.gauss(0, 1))

    def expo(self):
        return (random.expovariate(1), random.gauss(0, 1))

    def in01(self):
        return (random.random(), random.gauss(0, 1))

    def inpm01(self):
        return (random.choice([-1, 1]) * random.random(), random.gauss(0, 1))

    def above1(self):
        return (1 + random.expovariate(1), random.gauss(0, 1))

    # Custom Assertions ...

    def assertClose(self, a, b):
        if not numpy.allclose(a, b):
            raise AssertionError('{} not close to {}'.format(a, b))

    # Testing construction ...

    def test_construction(self):
        random.seed( 658)
        for i in xrange(10):
            nom, unc = self.gauss()

            ua1 = nom +- u(unc)
            ua2 = nom + u(unc)
            ua3 = nom - u(unc)
            ua4 = undarray(nominal=nom, stddev=unc)
            ua5 = undarray(nominal=nom, stddev=(-unc))

            self.assertClose(ua1.stddev, abs(unc))
            self.assertClose(ua2.stddev, abs(unc))
            self.assertClose(ua3.stddev, abs(unc))
            self.assertClose(ua4.stddev, abs(unc))
            self.assertClose(ua5.stddev, abs(unc))

    # Testing the operators ...

    def test_positive(self):
        random.seed( 646)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = +ua
            self.assertClose(ub.stddev, abs(unc))

    def test_unegative(self):
        random.seed(1)
        for i in xrange(0, 10):
            nom, unc = self.gauss()
            ua1 = nom +- u(unc)
            ua2 = -ua1

            self.assertClose(ua1.stddev, abs(unc))
            self.assertClose(ua2.stddev, abs(unc))

    def test_absolute(self):
        ua1 = 1 +- u(0.1)
        self.assertClose(abs(ua1).stddev, 0.1)

        ua2 = 1 +- u(0.1j)
        self.assertClose(abs(ua2).stddev, 0)

        ua3 = 1j +- u(0.1j)
        self.assertClose(numpy.abs(ua3).stddev, 0.1)

        ua4 = -1 +- u(0.1 + 0.1j)
        self.assertClose(abs(ua4).stddev, 0.1)

        ua5 = -1j +- u(0.1 - 0.1j)
        self.assertClose(abs(ua5).stddev, 0.1)

        ua6 = 1j +- u(0.1)
        self.assertClose(abs(ua6).stddev, 0)

    def test_sqrt(self):
        random.seed( 658)
        for i in xrange(10):
            nom, unc = self.expo()
            ua = nom +- u(unc)
            ub = numpy.sqrt(ua)

            self.assertClose(ub.stddev, abs(unc) * 0.5 * nom ** (-0.5))

    def test_square(self):
        random.seed( 700)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.square(ua)

            self.assertClose(ub.stddev, abs(unc) * 2 * abs(nom))

    def test_sin(self):
        random.seed(2)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua1 = undarray(nominal=nom, stddev=unc)
            ua2 = numpy.sin(ua1)

            self.assertClose(ua2.stddev, abs(unc * numpy.cos(nom)))

    def test_cos(self):
        random.seed(1632)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua1 = nom +- u(unc)
            ua2 = numpy.cos(ua1)

            self.assertClose(ua2.stddev, abs(-unc * numpy.sin(nom)))

    def test_tan(self):
        random.seed( 702)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.tan(ua)

            self.assertClose(ub.stddev, abs(unc) * (1 + numpy.tan(nom) ** 2))

    def test_arcsin(self):
        random.seed( 704)
        for i in xrange(10):
            nom, unc = self.inpm01()
            ua = nom +- u(unc)
            ub = numpy.arcsin(ua)

            self.assertClose(ub.stddev, abs(unc) / numpy.sqrt(1 - nom ** 2))

    def test_arccos(self):
        random.seed( 709)
        for i in xrange(10):
            nom, unc = self.inpm01()
            ua = nom +- u(unc)
            ub = numpy.arccos(ua)

            self.assertClose(ub.stddev, abs(unc) / numpy.sqrt(1 - nom ** 2))

    def test_arctan(self):
        random.seed( 710)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.arctan(ua)

            self.assertClose(ub.stddev, abs(unc) / (1 + nom ** 2))

    def test_sinh(self):
        random.seed( 712)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.sinh(ua)

            self.assertClose(ub.stddev, abs(unc * numpy.cosh(nom)))

    def test_cosh(self):
        random.seed( 715)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.cosh(ua)

            self.assertClose(ub.stddev, abs(unc * numpy.sinh(nom)))

    def test_tanh(self):
        random.seed( 716)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.tanh(ua)

            self.assertClose(ub.stddev, abs(unc) * (1 - numpy.tanh(nom) ** 2))

    def test_arcsinh(self):
        random.seed( 723)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.arcsinh(ua)

            self.assertClose(ub.stddev, abs(unc) / numpy.sqrt(nom ** 2 + 1))

    def test_arccosh(self):
        random.seed( 730)
        for i in xrange(10):
            nom, unc = self.above1()
            ua = nom +- u(unc)
            ub = numpy.arccosh(ua)

            self.assertClose(ub.stddev, abs(unc) / numpy.sqrt(nom ** 2 - 1))

    def test_arctanh(self):
        random.seed( 734)
        for i in xrange(10):
            nom, unc = self.inpm01()
            ua = nom +- u(unc)
            ub = numpy.arctanh(ua)

            self.assertClose(ub.stddev, abs(unc) / (1 - nom ** 2))

    def test_exp(self):
        random.seed(1638)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua1 = nom + u(unc)
            ua2 = numpy.exp(ua1)

            # y = exp(x) > 0
            # d_x y = exp(x)
            # u(y) = u(x) abs[d_x y] = u(x) * exp(x) = u(x) y
            # u(y) / y = u(x)
            # The absolute uncertainty of x turns out as the same as
            # the relative uncertainty of y.

            self.assertClose(ua2.stddev / ua2.nominal, abs(unc))

    def test_exp2(self):
        random.seed( 737)
        for i in xrange(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.exp2(ua)

            # y = 2 ** x = e ** (ln 2 * x)
            # d_x y = ln 2 * 2 ** x

            self.assertClose(ub.stddev, abs(unc) * numpy.log(2) * 2 ** nom)

    def test_log(self):
        random.seed(1648)
        for i in xrange(10):
            nom, unc = self.expo()
            ua1 = nom +- u(unc)
            ua2 = numpy.log(ua1)

            # y = ln x
            # d_x y = 1 / x
            # u(y) = u(x) / x
            # The relative uncertainty of x is the absolute
            # uncertainty of y.

            self.assertClose(ua2.stddev, ua1.stddev / ua1.nominal)

    def test_log2(self):
        random.seed(1653)
        for i in xrange(10):
            nom, unc = self.expo()
            ua1 = nom +- u(unc)
            ua2 = numpy.log2(ua1)

            # y = ln x / ln 2
            # u(y) = 1/ln 2 u(x) / x

            self.assertClose(ua2.stddev,
                    1/numpy.log(2) * ua1.stddev / ua1.nominal)

    def test_log10(self):
        random.seed(1655)
        for i in xrange(10):
            nom, unc = self.expo()
            ua1 = nom +- u(unc)
            ua2 = numpy.log10(ua1)

            # y = ln x / ln 10
            # u(y) = 1/ln 10 u(x) / x

            self.assertClose(ua2.stddev,
                    1/numpy.log(10) * ua1.stddev / ua1.nominal)

    def test_add(self):
        random.seed( 707)
        for i in xrange(10):
            nom1, unc1 = self.gauss()
            nom2, unc2 = self.gauss()
            ua1 = nom1 +- u(unc1)
            ua2 = nom2 +- u(unc2)

            uy = ua1 + ua2

            self.assertClose(uy.variance, ua1.variance + ua2.variance)

    def test_subtract(self):
        random.seed( 710)
        for i in xrange(10):
            nom1, unc1 = self.gauss()
            nom2, unc2 = self.gauss()
            ua1 = nom1 +- u(unc1)
            ua2 = nom2 +- u(unc2)

            uy = ua1 - ua2

            self.assertClose(uy.variance, ua1.variance + ua2.variance)

    def test_multiply(self):
        random.seed( 712)
        for i in xrange(10):
            nom1, unc1 = self.gauss()
            nom2, unc2 = self.gauss()
            ua1 = nom1 +- u(unc1)
            ua2 = nom2 +- u(unc2)

            uy = ua1 * ua2
            # y = x1 * x2
            #
            # d_x1 y = x2
            # d_x2 y = x1
            #
            # Var[y] = x2^2 Var[x1] + x1^2 Var[x2]
            #
            # u(y) = sqrt(x2^2 u(x1)^2 + x1^2 u(x2)^2)
            # u(y) / y = u(y) / (x1 x2)
            #   = sqrt([u(x1) / x1]^2 + [u(x2) / x2]^2)
            #
            # The relative uncertainties add in an rms. manner.
            # Furthermore:
            #
            # [u(y) / y]^2 = [u(x1) / x1]^2 + [u(x2) / x2]^2
            #
            # Var[y]/(y^2) = Var[x1]/(x1^2) + Var[x2]/(x2^2)

            self.assertClose(uy.variance,
                    nom2 ** 2 * ua1.variance + 
                    nom1 ** 2 * ua2.variance)
            self.assertClose((uy.stddev / uy.nominal) ** 2,
                        (ua1.stddev / ua1.nominal) ** 2 +
                        (ua2.stddev / ua2.nominal) ** 2)

    def test_divide(self):
        random.seed( 723)
        for i in xrange(10):
            nom1, unc1 = self.gauss()
            nom2, unc2 = self.gauss()
            ua1 = nom1 +- u(unc1)
            ua2 = nom2 +- u(unc2)

            uy = ua1 / ua2
            # y = x1 / x2
            #
            # d_x1 y = 1/x2 = y/x1
            # d_x2 y = -x1 / x2^2 = -y/x2
            #
            # Var[y] = Var[x1] [d_x1 y]^2 + Var[x2] [d_x2 y]^2
            #   = y^2 Var[x1]/(x1^2) + y^2 Var[x2]/(x2^2)
            #
            # Thus:
            #
            # Var[y]/(y^2) = Var[x1]/(x1^2) + Var[x2]/(x2^2)
            #
            # or:
            #
            # (u(y) / y)^2 = (u(x1) / x1)^2 + (u(x2) / x2)^2
            #
            # just as in the multiplication case.

            self.assertClose(uy.variance / uy.nominal ** 2,
                    ua1.variance / nom1 ** 2 +
                    ua2.variance / nom2 ** 2)

    def test_power(self):
        random.seed( 742)
        for i in xrange(10):
            nom1, unc1 = self.expo()
            nom2, unc2 = self.gauss()
            ua1 = nom1 +- u(unc1)
            ua2 = nom2 +- u(unc2)

            uy = ua1 ** ua2
            # y = x1 ** x2
            #
            # d_x1 y = x2 * x1 ** (x2 - 1)
            #
            # d_x2 y = d_x2 exp(ln x1) ** x2 = d_x2 exp(ln x1 * x2)
            #   = exp(ln x1 * x2) (ln x1)
            #   = ln x1 * x1 ** x2

            d1 = nom2 * nom1 ** (nom2 - 1)
            d2 = numpy.log(nom1) * nom1 ** nom2

            self.assertClose(uy.variance,
                    ua1.variance * d1 ** 2 + ua2.variance * d2 ** 2)

    def test_arctan2(self):
        random.seed( 740)
        for i in xrange(10):
            nomx, uncx = self.gauss()
            nomy, uncy = self.gauss()
            ux = nomx +- u(uncx)
            uy = nomy +- u(uncy)

            ub = upy2.uarctan2(uy, ux)

            dx = -nomy / (nomx ** 2 + nomy ** 2)
            dy = nomx / (nomx ** 2 + nomy ** 2)
            self.assertClose(ub.variance,
                    ux.variance * (dx ** 2) + uy.variance * (dy ** 2))
