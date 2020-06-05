# Developed since: Jun 2020

import unittest
import numpy
import upy2
from upy2 import undarray, U, u


class Test_Core(unittest.TestCase):

    def assertAllEqual(self, a, b):
        if not numpy.all(a == b):
            raise AssertionError(
                'Not all equal:\n{a}\nand\n{b}'.format(a=a, b=b))

    def assertClose(self, a, b):
        if not numpy.allclose(a, b):
            raise NotCloseError('{} not close to {}'.format(a, b))

    def test_uzeros(self):
        ua = upy2.uzeros((10, 10))
        self.assertEqual(ua.dtype, numpy.float)
        self.assertEqual(ua.nominal.dtype, numpy.float)
        self.assertEqual(len(ua.dependencies), 0)
        self.assertEqual(ua.nominal.shape, (10, 10))

    def test_asuarray(self):
        a = upy2.uzeros((3, 3))
        b = numpy.asarray([10, 11])
        c = [[100, 101]]

        ua = upy2.asuarray(a)
        ub = upy2.asuarray(b)
        uc = upy2.asuarray(c)

        self.assertIs(a, ua)
        self.assertAllEqual(ub.nominal, [10, 11])
        self.assertAllEqual(uc.nominal, [[100, 101]])

    def test_ucopy(self):
        a = upy2.uzeros((2, 2))
        b = numpy.asarray([numpy.pi, 0])

        ua = upy2.ucopy(a)
        ub = upy2.ucopy(b)

        a.nominal[0, 0] = 42
        b[0] = -1

        self.assertAllEqual(ua.nominal, [[0, 0], [0, 0]])
        self.assertAllEqual(ub.nominal, [numpy.pi, 0])

        c = undarray(nominal=[1.0, 5.0], stddev=[0.1, 0.3])
        uc = upy2.ucopy(c)

        c.nominal[1] = 6
        c.dependencies[0].names[0] = 101
        c.dependencies[0].derivatives[0] = 20

        self.assertClose(uc.nominal, [1.0, 5.0])
        self.assertClose(uc.stddev, [0.1, 0.3])

    def test_U(self):
        x = U(stddevs=2)

        y1 = x.provide([1, 2])
        self.assertAllEqual(y1.nominal, [0, 0])
        self.assertClose(y1.stddev, [0.5, 1])

        y2 = x([0.5, 5])
        self.assertClose(y2.stddev, [0.25, 2.5])
