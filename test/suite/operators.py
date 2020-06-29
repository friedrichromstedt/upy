# Developed since: May 2020

import random
import unittest
import numpy
import upy2
from upy2 import u, U, undarray


class NotCloseError(AssertionError):
    """ Some numbers are not close enough to each other. """

    pass

class DerivativeApproximationError(AssertionError):
    """ Calculating a derivative approximation numerically failed. """

    pass

class DerivativeVerificationError(AssertionError):
    """ The numerically aproximated derivative did not match the
    symbolical prediction. """

    pass


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

    # Providers for inspection positions during testing
    # differentiation ...

    def cgauss(self):
        return random.gauss(0, 1) + 1j * random.gauss(0, 1)

    # Custom Assertions ...

    def assertClose(self, a, b):
        if not numpy.allclose(a, b):
            raise NotCloseError('{} not close to {}'.format(a, b))

    def assertDerivative(self, specimen, position, prediction,
            epsilon, epsilonfactor=None):
        """ *specimen* is the function whose derivative is to be
        approximated numerically at position *position* using a small
        displacement *epsilon*.  *prediction* is the prediction of the
        derivative of *specimen* at *position* using symbolic
        differentiation.  To assess the precision of the numerical
        differentiation, it is carried out using *two* displacements,
        (a) with displacement ``epsilon`` and (b) with displacement
        ``epsilon * epsilonfactor``.  *epsilonfactor* defaults to
        ``1j``. """

        if epsilonfactor is None:
            epsilonfactor = 1j

        position0 = position
        position1 = position + epsilon
        position1j = position + epsilon * epsilonfactor

        value0 = specimen(position0)
        value1 = specimen(position1)
        value1j = specimen(position1j)

        approximation1 = (value1 - value0) / epsilon
        approximation1j = (value1j - value0) / (epsilon * epsilonfactor)

        mean_approximation = (approximation1 + approximation1j) / 2
        approximation_uncertainty = abs(approximation1j -
                approximation1) + 1e-10 * abs(mean_approximation)
            # The relative uncertainty accounts for the finite
            # resolution of floating point numbers.

        relative_approximation_uncertainty = \
                approximation_uncertainty / abs(mean_approximation)
        if relative_approximation_uncertainty > 0.01:
            raise DerivativeApproximationError(
                    ("The approximation of {specimen} "
                     "couln't be approximated successfully at "
                     "{position}.  Relative approximation uncertainty: "
                     "{rel:.3f}").\
                    format(specimen=specimen, position=position,
                        rel=relative_approximation_uncertainty)
            )

        difference = numpy.abs(prediction - mean_approximation)
        if difference > 2 * approximation_uncertainty:
            raise DerivativeVerificationError(
                ('Could not verify the derivative of '
                 '{specimen} at {position}.  Prediction: {prediction}, '
                 'approximation: {approximation} with uncertainty '
                 '{uncertainty}, Excess: {excess:.2f}').\
                format(specimen=specimen, position=position,
                    prediction=prediction,
                    approximation=mean_approximation,
                    uncertainty=approximation_uncertainty,
                    excess=(difference / approximation_uncertainty))
            )

    # Testing assertions ...

    def test_assertions(self):
        with self.assertRaises(NotCloseError):
            self.assertClose(1, 2)

        with self.assertRaises(DerivativeApproximationError):
            random.seed(1812)
            for i in range(100):
                z = self.cgauss()
                self.assertDerivative(
                    specimen=(lambda z:
                        numpy.sin(z.real) + numpy.cos(z.imag)),
                    position=z,
                    prediction=42,
                    epsilon=1e-4,
                )

        with self.assertRaises(DerivativeVerificationError):
            random.seed(1815)
            for i in range(100):
                z = self.cgauss()
                self.assertDerivative(
                    specimen=numpy.cos,
                    position=z,
                    prediction=42,
                    epsilon=1e-4,
                )

        # Test successful differentiation:
        random.seed(1819)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                specimen=numpy.cos,
                position=z,
                prediction=(-numpy.sin(z)),
                epsilon=1e-4,
            )

    # Testing construction ...

    def test_construction(self):
        random.seed( 658)
        for i in range(10):
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
        for i in range(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = +ua
            self.assertClose(ub.stddev, abs(unc))

    def test_unegative(self):
        random.seed(1)
        for i in range(0, 10):
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
        for i in range(10):
            nom, unc = self.expo()
            ua = nom +- u(unc)
            ub = numpy.sqrt(ua)

            self.assertClose(ub.stddev, abs(unc) * 0.5 * nom ** (-0.5))

        random.seed(1953)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.sqrt, position=z,
                    prediction=(0.5 * z ** (-0.5)),
                    epsilon=1e-4,
            )

    def test_square(self):
        random.seed( 700)
        for i in range(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.square(ua)

            self.assertClose(ub.stddev, abs(unc) * 2 * abs(nom))

        random.seed(1955)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.square, position=z,
                    prediction=(2 * z),
                    epsilon=1e-4,
            )

    def test_sin(self):
        random.seed(2)
        for i in range(10):
            nom, unc = self.gauss()
            ua1 = undarray(nominal=nom, stddev=unc)
            ua2 = numpy.sin(ua1)

            self.assertClose(ua2.stddev, abs(unc * numpy.cos(nom)))

        random.seed(1656)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.sin, position=z,
                    prediction=numpy.cos(z),
                    epsilon=1e-4,
            )

    def test_cos(self):
        random.seed(1632)
        for i in range(10):
            nom, unc = self.gauss()
            ua1 = nom +- u(unc)
            ua2 = numpy.cos(ua1)

            self.assertClose(ua2.stddev, abs(-unc * numpy.sin(nom)))

        random.seed(1957)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.cos, position=z,
                    prediction=(-numpy.sin(z)),
                    epsilon=1e-4,
            )

    def test_tan(self):
        random.seed( 702)
        for i in range(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.tan(ua)

            self.assertClose(ub.stddev, abs(unc) * (1 + numpy.tan(nom) ** 2))

        random.seed(1959)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.tan, position=z,
                    prediction=(1 + numpy.tan(z) ** 2),
                    epsilon=1e-4,
            )

    def test_arcsin(self):
        random.seed( 704)
        for i in range(10):
            nom, unc = self.inpm01()
            ua = nom +- u(unc)
            ub = numpy.arcsin(ua)

            self.assertClose(ub.stddev, abs(unc) / numpy.sqrt(1 - nom ** 2))

        random.seed(2001)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.arcsin, position=z,
                    prediction=(1 / numpy.sqrt(1 - z ** 2)),
                    epsilon=1e-4,
            )

    def test_arccos(self):
        random.seed( 709)
        for i in range(10):
            nom, unc = self.inpm01()
            ua = nom +- u(unc)
            ub = numpy.arccos(ua)

            self.assertClose(ub.stddev, abs(unc) / numpy.sqrt(1 - nom ** 2))

        random.seed(2002)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.arccos, position=z,
                    prediction=(-1 / numpy.sqrt(1 - z ** 2)),
                    epsilon=1e-4,
            )

    def test_arctan(self):
        random.seed( 710)
        for i in range(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.arctan(ua)

            self.assertClose(ub.stddev, abs(unc) / (1 + nom ** 2))

        random.seed(2004)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.arctan, position=z,
                    prediction=(1 / (1 + z ** 2)),
                    epsilon=1e-4,
            )

    def test_sinh(self):
        random.seed( 712)
        for i in range(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.sinh(ua)

            self.assertClose(ub.stddev, abs(unc * numpy.cosh(nom)))

        random.seed( 632)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.sinh, position=z,
                    prediction=numpy.cosh(z),
                    epsilon=1e-4,
            )

    def test_cosh(self):
        random.seed( 715)
        for i in range(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.cosh(ua)

            self.assertClose(ub.stddev, abs(unc * numpy.sinh(nom)))

        random.seed( 633)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.cosh, position=z,
                    prediction=numpy.sinh(z),
                    epsilon=1e-4,
            )

    def test_tanh(self):
        random.seed( 716)
        for i in range(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.tanh(ua)

            self.assertClose(ub.stddev, abs(unc) * (1 - numpy.tanh(nom) ** 2))

        random.seed( 636)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.tanh, position=z,
                    prediction=(1 - numpy.tanh(z) ** 2),
                    epsilon=1e-4,
            )

    def test_arcsinh(self):
        random.seed( 723)
        for i in range(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.arcsinh(ua)

            self.assertClose(ub.stddev, abs(unc) / numpy.sqrt(nom ** 2 + 1))

        random.seed( 637)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.arcsinh, position=z,
                    prediction=(1 / numpy.sqrt(z ** 2 + 1)),
                    epsilon=1e-4,
            )

    @unittest.expectedFailure
    def test_arccosh(self):
        random.seed( 730)
        for i in range(10):
            nom, unc = self.above1()
            ua = nom +- u(unc)
            ub = numpy.arccosh(ua)

            self.assertClose(ub.stddev, abs(unc) / numpy.sqrt(nom ** 2 - 1))

        # This succeeds:
        random.seed( 644)
        for i in range(100):
            x = 1 + random.expovariate(1)
            self.assertDerivative(
                    specimen=numpy.arccosh, position=x,
                    prediction=(1 / numpy.sqrt(x ** 2 - 1)),
                    epsilon=1e-4,
            )

        # This fails:
        random.seed( 656)
        for i in range(100):
            x = random.gauss(0, 1) + 0j
            self.assertDerivative(
                    specimen=numpy.arccosh, position=x,
                    prediction=(1 / numpy.sqrt(x ** 2 - 1)),
                    epsilon=1e-5,  # There is a case with x very close
                        # to 1.0, requiring this precision.  (With ``+
                        # 0j`` in the definition of *x*, an assertion
                        # is violated before reaching this case.)
            )

        # This fails:
        random.seed( 640)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.arccosh, position=z,
                    prediction=(1 / numpy.sqrt(z ** 2 - 1)),
                    #prediction=(1 / (z ** 2 - 1) ** 0.5),
                    epsilon=1e-4,
            )

    def test_arctanh(self):
        random.seed( 734)
        for i in range(10):
            nom, unc = self.inpm01()
            ua = nom +- u(unc)
            ub = numpy.arctanh(ua)

            self.assertClose(ub.stddev, abs(unc) / (1 - nom ** 2))

        random.seed(1346)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.arctanh, position=z,
                    prediction=(1 / (1 - z **2)),
                    epsilon=1e-4,
            )

    def test_exp(self):
        random.seed(1638)
        for i in range(10):
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

        random.seed(1348)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.exp, position=z,
                    prediction=(numpy.e ** z),
                    epsilon=1e-4,
            )

    def test_exp2(self):
        random.seed( 737)
        for i in range(10):
            nom, unc = self.gauss()
            ua = nom +- u(unc)
            ub = numpy.exp2(ua)

            # y = 2 ** x = e ** (ln 2 * x)
            # d_x y = ln 2 * 2 ** x

            self.assertClose(ub.stddev, abs(unc) * numpy.log(2) * 2 ** nom)

        random.seed(1349)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.exp2, position=z,
                    prediction=(numpy.log(2) * 2 ** z),
                    epsilon=1e-4,
            )

    def test_log(self):
        random.seed(1648)
        for i in range(10):
            nom, unc = self.expo()
            ua1 = nom +- u(unc)
            ua2 = numpy.log(ua1)

            # y = ln x
            # d_x y = 1 / x
            # u(y) = u(x) / x
            # The relative uncertainty of x is the absolute
            # uncertainty of y.

            self.assertClose(ua2.stddev, ua1.stddev / ua1.nominal)

        random.seed(1351)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.log, position=z,
                    prediction=(1 / z),
                    epsilon=1e-4,
            )

    def test_log2(self):
        random.seed(1653)
        for i in range(10):
            nom, unc = self.expo()
            ua1 = nom +- u(unc)
            ua2 = numpy.log2(ua1)

            # y = ln x / ln 2
            # u(y) = 1/ln 2 u(x) / x

            self.assertClose(ua2.stddev,
                    1/numpy.log(2) * ua1.stddev / ua1.nominal)

        random.seed(1352)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.log2, position=z,
                    prediction=(1 / numpy.log(2) / z),
                    epsilon=1e-4,
            )

    def test_log10(self):
        random.seed(1655)
        for i in range(10):
            nom, unc = self.expo()
            ua1 = nom +- u(unc)
            ua2 = numpy.log10(ua1)

            # y = ln x / ln 10
            # u(y) = 1/ln 10 u(x) / x

            self.assertClose(ua2.stddev,
                    1/numpy.log(10) * ua1.stddev / ua1.nominal)

        random.seed(1354)
        for i in range(100):
            z = self.cgauss()
            self.assertDerivative(
                    specimen=numpy.log10, position=z,
                    prediction=(1 / numpy.log(10) / z),
                    epsilon=1e-4,
            )

    def test_add(self):
        random.seed( 707)
        for i in range(10):
            nom1, unc1 = self.gauss()
            nom2, unc2 = self.gauss()
            ua1 = nom1 +- u(unc1)
            ua2 = nom2 +- u(unc2)

            uy = ua1 + ua2

            self.assertClose(uy.variance, ua1.variance + ua2.variance)

        random.seed(1406)
        for i in range(100):
            z1 = self.cgauss()
            z2 = self.cgauss()

            self.assertDerivative(
                    specimen=(lambda z: numpy.add(z, z2)), position=z1,
                    prediction=1,
                    epsilon=1e-4,
            )
            self.assertDerivative(
                    specimen=(lambda z: numpy.add(z1, z)), position=z2,
                    prediction=1,
                    epsilon=1e-4,
            )

    def test_subtract(self):
        random.seed( 710)
        for i in range(10):
            nom1, unc1 = self.gauss()
            nom2, unc2 = self.gauss()
            ua1 = nom1 +- u(unc1)
            ua2 = nom2 +- u(unc2)

            uy = ua1 - ua2

            self.assertClose(uy.variance, ua1.variance + ua2.variance)

        random.seed(1409)
        for i in range(100):
            z1 = self.cgauss()
            z2 = self.cgauss()

            self.assertDerivative(
                    specimen=(lambda z: numpy.subtract(z, z2)), position=z1,
                    prediction=1,
                    epsilon=1e-4,
            )
            self.assertDerivative(
                    specimen=(lambda z: numpy.subtract(z1, z)), position=z2,
                    prediction=-1,
                    epsilon=1e-4,
            )

    def test_multiply(self):
        random.seed( 712)
        for i in range(10):
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

        random.seed(1402)
        for i in range(100):
            z1 = self.cgauss()
            z2 = self.cgauss()

            self.assertDerivative(
                    specimen=(lambda z: numpy.multiply(z, z2)), position=z1,
                    prediction=z2,
                    epsilon=1e-4,
            )
            self.assertDerivative(
                    specimen=(lambda z: numpy.multiply(z1, z)), position=z2,
                    prediction=z1,
                    epsilon=1e-4,
            )

    def test_divide(self):
        random.seed( 723)
        for i in range(10):
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

        random.seed(1413)
        for i in range(100):
            z1 = self.cgauss()
            z2 = self.cgauss()

            self.assertDerivative(
                    specimen=(lambda z: numpy.divide(z, z2)), position=z1,
                    prediction=(1 / z2),
                    epsilon=1e-4,
            )
            self.assertDerivative(
                    specimen=(lambda z: numpy.divide(z1, z)), position=z2,
                    prediction=(-z1 / (z2 ** 2)),
                    epsilon=1e-4,
            )

    def test_power(self):
        random.seed( 742)
        for i in range(10):
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

        random.seed(1416)
        for i in range(100):
            z1 = self.cgauss()
            z2 = self.cgauss()

            self.assertDerivative(
                    specimen=(lambda z: numpy.power(z, z2)), position=z1,
                    prediction=(z2 * (z1 ** (z2 - 1))),
                    epsilon=1e-4,
            )
            self.assertDerivative(
                    specimen=(lambda z: numpy.power(z1, z)), position=z2,
                    prediction=(numpy.log(z1) * (z1 ** z2)),
                    epsilon=1e-4,
            )

    def test_arctan2(self):
        random.seed( 740)
        for i in range(10):
            nomx, uncx = self.gauss()
            nomy, uncy = self.gauss()
            ux = nomx +- u(uncx)
            uy = nomy +- u(uncy)

            ub = upy2.uarctan2(uy, ux)

            dx = -nomy / (nomx ** 2 + nomy ** 2)
            dy = nomx / (nomx ** 2 + nomy ** 2)
            self.assertClose(ub.variance,
                    ux.variance * (dx ** 2) + uy.variance * (dy ** 2))

        random.seed(1419)
        for i in range(100):
            x = random.gauss(0, 1)
            y = random.gauss(0, 1)
            # ``numpy.arctan2`` is supported only for real-valued
            # arguments.

            self.assertDerivative(
                    specimen=(lambda x: numpy.arctan2(y, x)), position=x,
                    prediction=(-y / (x ** 2 + y ** 2)),
                    epsilon=1e-4, epsilonfactor=-1,
            )
            self.assertDerivative(
                    specimen=(lambda y: numpy.arctan2(y, x)), position=y,
                    prediction=(x / (x ** 2 + y ** 2)),
                    epsilon=1e-4, epsilonfactor=-1,
            )
