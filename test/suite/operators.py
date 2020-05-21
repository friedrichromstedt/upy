# Developed since: May 2020

import random
import unittest
import numpy
from upy2 import u, U, undarray


class TestOperators(unittest.TestCase):
    def __init__(self, name):
        unittest.TestCase.__init__(self, name)
        self.U = U(1)

    def setUp(self):
        self.U.register()

    def tearDown(self):
        self.U.unregister()

    def gauss(self):
        return (random.gauss(0, 1), random.gauss(0, 1))

    def expo(self):
        return (random.expovariate(1), random.gauss(0, 1))


    def assertClose(self, a, b):
        if not numpy.allclose(a, b):
            raise AssertionError('{} not close to {}'.format(a, b))

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
