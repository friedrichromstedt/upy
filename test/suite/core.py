# Developed since: Jun 2020

import threading
import operator
import unittest
import numpy
import upy2
from upy2 import undarray, U, u
from upy2.dependency import Dependency
import upy2.sessions

import sys
py3 = (sys.version_info >= (3,))
py2 = not py3

class Test_Core(unittest.TestCase):

    def assertAllEqual(self, a, b):
        if not numpy.all(a == b):
            raise AssertionError(
                'Not all equal:\n{a}\nand\n{b}'.format(a=a, b=b))

    def assertClose(self, a, b):
        if not numpy.allclose(a, b):
            raise NotCloseError('{} not close to {}'.format(a, b))

    def assertRaisesRegex(self, *args, **kwargs):
        if py2:
            return unittest.TestCase.assertRaisesRegexp(self, *args, **kwargs)
        else:
            return unittest.TestCase.assertRaisesRegex(self, *args, **kwargs)

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

        # Test the session ...

        U_session = upy2.sessions.byprotocol(U)

        with self.assertRaisesRegex(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test :meth:`{default, undefault}`:
        U_session.default(x)
        self.assertIs(U_session.current(), x)
        U_session.undefault(x)
        with self.assertRaisesRegex(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test :meth:`{register, unregister}`:
        U_session.register(x)
        self.assertIs(U_session.current(), x)
        U_session.unregister(x)
        with self.assertRaisesRegex(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test combination of :meth:`{register, unregister}` and
        # :meth:{default, undefault}`:
        y = U(stddevs=3)
        x.default()
        y.register()
        self.assertIs(U_session.current(), y)
        x.undefault()
        self.assertIs(U_session.current(), y)
        y.unregister()
        with self.assertRaisesRegex(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test order check in :meth:`undefault`:
        U_session.default(x)
        U_session.default(y)
        with self.assertRaisesRegex(ValueError,
                '^Un-defaulting a session manager which is not '
                'the current default item$'):
            U_session.undefault(x)
        self.assertIs(U_session.current(), y)
        U_session.undefault(y)
        self.assertIs(U_session.current(), x)
        U_session.undefault(x)
        with self.assertRaisesRegex(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test order check in :meth:`unregister`:
        U_session.register(x)
        with y:
            with self.assertRaisesRegex(ValueError,
                    '^The session manager to be unregistered is not '
                    'the topmost entry on the stack$'):
                U_session.unregister(x)
            self.assertIs(U_session.current(), y)
        self.assertIs(U_session.current(), x)
        U_session.unregister(x)
        with self.assertRaisesRegex(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

    def test_string_conversion(self):
        self.assertEqual(str(upy2.uadd), "<<ufunc 'add'> uufunc>")
        self.assertEqual(repr(upy2.uadd), "<<ufunc 'add'> uufunc>")


class Test_undarray(unittest.TestCase):

    def assertAllEqual(self, a, b):
        if not numpy.all(a == b):
            raise AssertionError(
                'Not all equal:\n{a}\nand\n{b}'.format(a=a, b=b))

    def assertClose(self, a, b):
        if not numpy.allclose(a, b):
            raise NotCloseError('{} not close to {}'.format(a, b))

    def assertIsundarray(self, obj):
        self.assertIsInstance(obj, undarray)

    def assertRaisesRegex(self, *args, **kwargs):
        if py2:
            return unittest.TestCase.assertRaisesRegexp(self, *args, **kwargs)
        else:
            return unittest.TestCase.assertRaisesRegex(self, *args, **kwargs)

    def test_creation(self):
        # Test *nominal* and *dtype* arguments:

        ua = undarray(nominal=[10, 11])
        self.assertAllEqual(ua.nominal, [10, 11])
        self.assertEqual(ua.nominal.dtype, numpy.int)
        self.assertEqual(ua.dtype, numpy.int)

        ua = undarray(nominal=[10, 11], dtype=numpy.float)
        self.assertAllEqual(ua.nominal, [10.0, 11.0])
        self.assertEqual(ua.nominal.dtype, numpy.float)
        self.assertEqual(ua.dtype, numpy.float)

        ua = undarray(nominal=[10.5, 11.4], dtype=numpy.int)
        self.assertAllEqual(ua.nominal, [10, 11])
        self.assertEqual(ua.nominal.dtype, numpy.int)
        self.assertEqual(ua.dtype, numpy.int)

        # Test *shape* argument:

        ua = undarray(shape=(2, 2))
        self.assertAllEqual(ua.nominal, [[0, 0], [0, 0]])
        self.assertEqual(ua.nominal.dtype, numpy.float)
        self.assertEqual(ua.dtype, numpy.float)

        ua = undarray(shape=(2, 2), dtype=numpy.int)
        self.assertAllEqual(ua.nominal, [[0, 0], [0, 0]])
        self.assertEqual(ua.nominal.dtype, numpy.int)
        self.assertEqual(ua.dtype, numpy.int)

        ua = undarray(nominal=[20, 30], shape=(2, 2))
            # *nominal* overrides *shape*.
        self.assertAllEqual(ua.nominal, [20, 30])

        # Test *stddev* argument:

        ua = undarray(nominal=[1.0, 2.0], stddev=[0.1, 0.1])
        self.assertAllEqual(ua.stddev, [0.1, 0.1])

        with self.assertRaises(ValueError):
            # Cannot append a Dependency of dtype float64 to a
            # int64-dtyped undarray
            # - ``float64`` and ``int64`` might be machine-dependent.
            ua = undarray(nominal=[10, 11], stddev=[0.1, 0.1])

        ua = undarray(nominal=[10, 11], stddev=[0.1, 0.1],
                dtype=numpy.float)
        self.assertAllEqual(ua.stddev, [0.1, 0.1])

        ua = undarray(nominal=[42, 43], stddev=[1.1, 1.9],
                dtype=numpy.int)
        self.assertAllEqual(ua.stddev, [1, 1])

        # Test *shape* and *stddev* argument:

        ua = undarray(shape=(2, 2), stddev=[[0.5, 0.6], [0.7, 0.8]])
        self.assertAllEqual(ua.nominal, [[0, 0], [0, 0]])
        self.assertAllEqual(ua.stddev, [[0.5, 0.6], [0.7, 0.8]])

    def test_append(self):
        ua = undarray(nominal=[-10, 10])

        dependency = Dependency(shape=(2,), dtype=numpy.int)
        ua.append(dependency)

        dependency = Dependency(shape=(2,))
        with self.assertRaises(ValueError):
            # Cannot append a Dependency of dtype float64 to a
            # int64-dtyped undarray
            ua.append(dependency)

        dependency = Dependency(shape=(2, 2), dtype=numpy.int)
        with self.assertRaises(ValueError):
            # Cannot append a Dependency of shape (2, 2) to a
            # (2,)-shaped undarray
            ua.append(dependency)

        dependency = Dependency(shape=(2,), dtype=numpy.int16)
        with self.assertRaises(ValueError):
            # Cannot append a Dependency of dtype int16 to a
            # int64-dtyped undarray
            ua.append(dependency)

    def test_clear(self):
        ua = undarray(nominal=[[1.0, 2.0], [3.0, 4.0]])

        ua.append(Dependency(
            names=upy2.guid_generator.get_idarray((2, 2)),
            derivatives=[[0.1, 0.1], [0.1, 0.1]]))
        ua.append(Dependency(
            names=upy2.guid_generator.get_idarray((2, 2)),
            derivatives=[[0.2, 0.2], [0.2, 0.2]]))

        ua.clear((1, 0))

        self.assertAllEqual(ua.dependencies[0].names == 0,
                [[False, False], [True, False]])
        self.assertAllEqual(ua.dependencies[1].names == 0,
                [[False, False], [True, False]])

        self.assertAllEqual(ua.dependencies[0].derivatives == 0,
                [[False, False], [True, False]])
        self.assertAllEqual(ua.dependencies[1].derivatives == 0,
                [[False, False], [True, False]])

    def test_scaled(self):
        ua = undarray(nominal=[1.0, 2.0], stddev=[0.1, 0.1])
        ub = ua.scaled(2)
        self.assertAllEqual(ub.nominal, [2.0, 4.0])
        self.assertAllEqual(ub.stddev, [0.2, 0.2])

        ua = undarray(nominal=[100, 101], stddev=[1, 2])
        ub = ua.scaled(2)
        uc = ua.scaled(0.5)

        self.assertEqual(ub.dtype, numpy.int)
        self.assertEqual(uc.dtype, numpy.float)

        self.assertAllEqual(ub.nominal, [200, 202])
        self.assertAllEqual(ub.stddev, [2, 4])
        self.assertAllEqual(uc.nominal, [50.0, 50.5])
        self.assertAllEqual(uc.stddev, [0.5, 1.0])

    def test_copy_dependencies(self):
        utarget = undarray(shape=(2, 2))
        usource1 = undarray(shape=(2, 2), stddev=[[0.1, 0.2], [0.3, 0.4]])
        usource2 = undarray(shape=(2,), stddev=[0.5, 0.6])

        utarget.copy_dependencies(usource1)
        self.assertAllEqual(utarget.dependencies[0].derivatives,
                [[0.1, 0.2], [0.3, 0.4]])

        utarget.clear((0, 0))
        utarget.copy_dependencies(usource2, key=(0,))
        self.assertAllEqual(utarget.dependencies[0].derivatives,
                [[0.5, 0.2], [0.3, 0.4]])
        self.assertAllEqual(utarget.dependencies[1].derivatives,
                [[0.0, 0.6], [0.0, 0.0]])

        # Test independence:

        usource1.clear((0, 0))
        usource2.clear((0,))

        self.assertAllEqual(utarget.dependencies[0].derivatives,
                [[0.5, 0.2], [0.3, 0.4]])
        self.assertAllEqual(utarget.dependencies[1].derivatives,
                [[0.0, 0.6], [0.0, 0.0]])

    def test_complex(self):
        ua = undarray(
                nominal=[1 + 2j, 2 + 3j],
                stddev=[0.1 + 0.2j, 0.2 + 0.3j])
        real = ua.real
        imag = ua.imag
        conj = ua.conj()

        ua[0] = 42
        self.assertAllEqual(ua.nominal, [42, 2 + 3j])
        self.assertAllEqual(ua.dependencies[0].derivatives,
                [0, 0.2 + 0.3j])

        self.assertAllEqual(real.nominal, [1, 2])
        self.assertAllEqual(real.stddev, [0.1, 0.2])

        self.assertAllEqual(imag.nominal, [2, 3])
        self.assertAllEqual(imag.stddev, [0.2, 0.3])

        self.assertAllEqual(conj.nominal, [1 - 2j, 2 - 3j])
        self.assertAllEqual(conj.dependencies[0].derivatives,
                [0.1 - 0.2j, 0.2 - 0.3j])

    def test_variance_and_stddev(self):
        ua = undarray(nominal=[40], stddev=[2])
        ub = undarray(nominal=[1 + 1j], stddev=[1j])

        self.assertAllEqual(ua.variance, [4])
        with self.assertRaisesRegex(ValueError,
                '^Refusing to calculate variance of non-real Dependency$'):
            ub.variance

        self.assertAllEqual(ua.stddev, [2])
        with self.assertRaisesRegex(ValueError,
                '^Refusing to calculate variance of non-real Dependency$'):
            ub.stddev

    def test_binary_operators(self):
        with U(1):
            ua = [10, 11.5] +- u([1.5, 1.0])
            ux = undarray(nominal=[40, 41], stddev=[1, 2])
                # *ux* is used in testing the augmented arithmetics,
                # since these aren't covered by the :mod:`operators`
                # test module.

        b = [1, 2]
        c = numpy.asarray([1, 2])

        self.assertIsundarray(ua + b)
        self.assertIsundarray(b + ua)
        self.assertIsundarray(ua + c)
        self.assertIsundarray(c + ua)

        self.assertIsundarray(ua - b)
        self.assertIsundarray(b - ua)
        self.assertIsundarray(ua - c)
        self.assertIsundarray(c - ua)

        self.assertIsundarray(ua * b)
        self.assertIsundarray(b * ua)
        self.assertIsundarray(ua * c)
        self.assertIsundarray(c * ua)

        self.assertIsundarray(ua / b)
        self.assertIsundarray(b / ua)
        self.assertIsundarray(ua / c)
        self.assertIsundarray(c / ua)

        if py2:
            self.assertIsundarray(operator.div(ua, b))
            self.assertIsundarray(operator.div(b, ua))
            self.assertIsundarray(operator.div(ua, c))
            self.assertIsundarray(operator.div(c, ua))

        self.assertIsundarray(operator.truediv(ua, b))
        self.assertIsundarray(operator.truediv(b, ua))
        self.assertIsundarray(operator.truediv(ua, c))
        self.assertIsundarray(operator.truediv(c, ua))

        self.assertIsundarray(ua ** b)
        self.assertIsundarray(b ** ua)
        self.assertIsundarray(ua ** c)
        self.assertIsundarray(c ** ua)

        ub = ua; ub += b; self.assertIsundarray(ub)
        self.assertAllEqual(ua.nominal, [10, 11.5])
        ub = ua; ub += c; self.assertIsundarray(ub)
        ub = ua; ub += ux; self.assertIsundarray(ub)

        ub = ua; ub -= b; self.assertIsundarray(ub)
        ub = ua; ub -= c; self.assertIsundarray(ub)
        ub = ua; ub -= ux; self.assertIsundarray(ub)

        ub = ua; ub *= b; self.assertIsundarray(ub)
        ub = ua; ub *= c; self.assertIsundarray(ub)
        ub = ua; ub *= ux; self.assertIsundarray(ub)

        if py2:
            ub = ua; ub = operator.idiv(ua, b); self.assertIsundarray(ub)
            ub = ua; ub = operator.idiv(ua, c); self.assertIsundarray(ub)
            ub = ua; ub = operator.idiv(ua, ux); self.assertIsundarray(ub)

        ub = ua; ub = operator.itruediv(ua, b); self.assertIsundarray(ub)
        ub = ua; ub = operator.itruediv(ua, c); self.assertIsundarray(ub)
        ub = ua; ub = operator.itruediv(ua, ux); self.assertIsundarray(ub)

        ub = ua; ub **= b; self.assertIsundarray(ub)
        ub = ua; ub **= c; self.assertIsundarray(ub)
        ub = ua; ub **= ux; self.assertIsundarray(ub)

    def test_getitem_setitem_len(self):
        with U(1):
            ua = [[1.0, 2.0], [3.0, 4.0]] +- u([[0.1, 0.2], [0.3, 0.4]])

        ub = ua[1]

        with U(1):
            ua[1, 0] = 10.0 +- u(1.0)

        self.assertAllEqual(ub.nominal, [3.0, 4.0])
        self.assertAllEqual(ub.stddev, [0.3, 0.4])

        self.assertAllEqual(ua.nominal, [[1.0, 2.0], [10.0, 4.0]])
        self.assertAllEqual(ua.stddev, [[0.1, 0.2], [1.0, 0.4]])

        self.assertEqual(len(ua), 2)

    def test_compress(self):
        with U(1):
            ua = [[10, 11], [12, 13]] +- u([[1, 2], [3, 4]])

        ub = numpy.compress(
                condition=[False, True],
                a=ua, axis=0)
        ua[1, 0] = 42

        self.assertAllEqual(ub.nominal, [12, 13])
        self.assertAllEqual(ub.stddev, [3, 4])

    def test_copy(self):
        with U(1):
            ua = [10, 11] +- u([1, 2])

        ub = ua.copy()
        ua[0] = 42

        self.assertAllEqual(ub.nominal, [10, 11])
        self.assertAllEqual(ub.stddev, [1, 2])

    def test_flatten(self):
        ua = undarray(
                nominal=numpy.asarray([[10, 12], [11, 13]]).T,
                stddev=[[1, 2], [3, 4]])

        ub = ua.flatten()

        self.assertAllEqual(ub.nominal, [10, 11, 12, 13])
        self.assertAllEqual(ub.stddev, [1, 2, 3, 4])

    def test_repeat(self):
        with U(1):
            ua = [[10, 11], [12, 13]] +- u([[1, 2], [3, 4]])

        ub = numpy.repeat(ua, [2, 3], axis=1)

        self.assertAllEqual(ub.nominal,
                [[10, 10, 11, 11, 11], [12, 12, 13, 13, 13]])
        self.assertAllEqual(ub.stddev,
                [[1, 1, 2, 2, 2], [3, 3, 4, 4, 4]])

    def test_reshape(self):
        ua = undarray(
                nominal=numpy.asarray([[10, 12], [11, 13]]).T,
                stddev=[[1, 2], [3, 4]])

        ub = ua.reshape((4,))
        ua[0, 1] = 0

        self.assertAllEqual(ub.nominal, [10, 11, 12, 13])
        self.assertAllEqual(ub.stddev, [1, 2, 3, 4])

    def test_transpose(self):
        ua = undarray(
                nominal=numpy.asarray([[10, 12], [11, 13]]).T,
                stddev=[[1, 2], [3, 4]])

        ub = numpy.transpose(ua)
        ua[0, 0] = 0
        self.assertAllEqual(ub.nominal, [[10, 12], [11, 13]])
        self.assertAllEqual(ub.stddev, [[1, 3], [2, 4]])

        with U(1):
            nominal = numpy.asarray([[[10], [11]], [[12], [13]]])
            stddev = numpy.asarray([[[1], [2]], [[3], [4]]])

            ua = nominal +- u(stddev)

        ub = numpy.transpose(ua)
        self.assertAllEqual(ub.nominal, numpy.transpose(nominal))
        self.assertAllEqual(ub.stddev, numpy.transpose(stddev))

        ub = numpy.transpose(ua, (0, 2, 1))
            # Swaps the last two axes.
        self.assertAllEqual(ub.nominal, numpy.transpose(nominal, (0, 2, 1)))
        self.assertAllEqual(ub.stddev, numpy.transpose(stddev, (0, 2, 1)))
