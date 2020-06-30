# Developed since: Jun 2020

import unittest
import numpy
from upy2.dependency import Dependency

import sys
py3 = (sys.version_info >= (3,))
py2 = not py3


class Test_Dependency(unittest.TestCase):

    def assertAllEqual(self, a, b):
        if not numpy.all(a == b):
            raise AssertionError(
                'Not all equal:\n{a}\nand\n{b}'.format(a=a, b=b))

    def assertRaisesRegex(self, *args, **kwargs):
        if py2:
            return unittest.TestCase.assertRaisesRegexp(self, *args, **kwargs)
        else:
            return unittest.TestCase.assertRaisesRegex(self, *args, **kwargs)

    def test_construction(self):
        # Test construction from *names* and *derivatives*:
        dep = Dependency(names=[1, 2], derivatives=[3, 4])
        self.assertEqual(dep.derivatives.dtype, numpy.int)
        self.assertEqual(dep.dtype, numpy.int)

        dep = Dependency(names=[1, 2], derivatives=[3.0, 4.0])
        self.assertEqual(dep.derivatives.dtype, numpy.float)
        self.assertEqual(dep.dtype, numpy.float)

        dep = Dependency(names=[1, 2], derivatives=[3, 4],
                dtype=numpy.float)
        self.assertEqual(dep.derivatives.dtype, numpy.float)
        self.assertEqual(dep.dtype, numpy.float)

        with self.assertRaises(ValueError):
            dep = Dependency(names=[1], derivatives=[10, -10])
            # ValueError: Shape mismatch in initialising a Dependency:
            # names.shape = (1,), derivatives.shape = (2,)

        with self.assertRaises(ValueError):
            dep = Dependency()
            # ValueError: Dependency: Unable to initialise from the
            # arguments provided
        with self.assertRaises(ValueError):
            dep = Dependency(names=[42])
        with self.assertRaises(ValueError):
            dep = Dependency(derivatives=[1.0])

        # Test construction from *shape*:
        dep = Dependency(shape=(2, 2))
        self.assertAllEqual(dep.names, [[0, 0], [0, 0]])
        self.assertEqual(dep.names.dtype, numpy.int)
        self.assertAllEqual(dep.derivatives, [[0, 0], [0, 0]])
        self.assertEqual(dep.derivatives.dtype, numpy.float)
        self.assertEqual(dep.dtype, numpy.float)

        dep = Dependency(shape=(2, 2), dtype=numpy.complex)
        self.assertEqual(dep.derivatives.dtype, numpy.complex)
        self.assertEqual(dep.dtype, numpy.complex)

    def test_emptiness(self):
        dep = Dependency(names=[0, 0], derivatives=[0, 0])
        self.assertTrue(dep.is_empty())
        self.assertFalse(dep.is_nonempty())

        dep = Dependency(names=[0, 1], derivatives=[0, 42])
        self.assertFalse(dep.is_empty())
        self.assertTrue(dep.is_nonempty())

    def test_variance(self):
        dep = Dependency(names=1, derivatives=(1 + 1j))
        with self.assertRaisesRegex(ValueError,
                "^Refusing to calculate variance of non-real Dependency$"):
            dep.variance

        dep1 = Dependency(names=1, derivatives=1.0)
        dep2 = Dependency(names=1, derivatives=1)
        dep3 = Dependency(names=1, derivatives=1.0, dtype=numpy.float32)
        dep4 = Dependency(names=1, derivatives=1, dtype=numpy.uint8)

        # These do not raise an Exception:
        dep1.variance
        dep2.variance
        dep3.variance
        dep4.variance

    def test_complex(self):
        dep = Dependency(names=[1, 0], derivatives=[(1 + 2j), 0])

        # Derive real, imag, conjugate Dependencies:
        dep_real = dep.real
        dep_imag = dep.imag
        dep_conj = dep.conj()

        # Modify the source Dependency:
        dep.names[1] = 42
        dep.derivatives[1] = 10 - 1j

        # Assert that the derived Depedencies are independent:
        self.assertAllEqual(dep_real.names, [1, 0])
        self.assertAllEqual(dep_imag.names, [1, 0])
        self.assertAllEqual(dep_conj.names, [1, 0])

        self.assertAllEqual(dep_real.derivatives, [1, 0])
        self.assertAllEqual(dep_imag.derivatives, [2, 0])
        self.assertAllEqual(dep_conj.derivatives, [1 - 2j, 0])

    def test_copy(self):
        dep1 = Dependency(names=[2, 3], derivatives=[3, 4])
        dep2 = dep1.copy()

        dep1.names[0] = 42
        dep1.derivatives[1] = 20

        self.assertAllEqual(dep2.names, [2, 3])
        self.assertAllEqual(dep2.derivatives, [3, 4])

    def test_add(self):
        # Target Dependencies:
        depA = Dependency(names=[1, 0], derivatives=[42, 0])
        depA2 = Dependency(
                names=[[1, 0], [0, 3]],
                derivatives=[[12, 0], [0, 4]])
        
        # Calling :meth:`add` *without* key and with a Dependency of
        # the same shape:
        depB = Dependency(names=[2, 3], derivatives=[1, 2])
        depA_ = depA.copy()
        depB_ = depA_.add(depB)
        
        self.assertAllEqual(depA_.names, [1, 3])
        self.assertAllEqual(depA_.derivatives, [42, 2])
        self.assertAllEqual(depB_.names, [2, 0])
        self.assertAllEqual(depB_.derivatives, [1, 0])

        # Calling :meth:`add` *with* a key:
        depB = Dependency(names=4, derivatives=20)
        depA_ = depA.copy()
        depB_ = depA_.add(depB, key=1)

        self.assertAllEqual(depA_.names, [1, 4])
        self.assertAllEqual(depA_.derivatives, [42, 20])
        self.assertAllEqual(depB_.names, 0)
        self.assertAllEqual(depB_.derivatives, 0)

        # Calling :meth:`add` without a key and with broadcasting:
        depB = Dependency(names=4, derivatives=20)
        depA_ = depA.copy()
        depB_ = depA_.add(depB)

        self.assertAllEqual(depA_.names, [1, 4])
        self.assertAllEqual(depA_.derivatives, [42, 20])
        self.assertAllEqual(depB_.names, [4, 0])
        self.assertAllEqual(depB_.derivatives, [20, 0])

        # Calling :meth:`add` again without a key and again with
        # broadcasting, this times with larger shapes:
        depB = Dependency(names=[50, 60], derivatives=[70, 80])
        depA_ = depA2.copy()
        depB_ = depA_.add(depB)

        self.assertAllEqual(depA_.names, [[1, 60], [50, 3]])
        self.assertAllEqual(depA_.derivatives, [[12, 80], [70, 4]])
        self.assertAllEqual(depB_.names, [[50, 0], [0, 60]])
        self.assertAllEqual(depB_.derivatives, [[70, 0], [0, 80]])

        # Calling :meth:`add` again with a key, this time with larger
        # shapes, without broadcasting:
        depB = Dependency(names=[100, 101], derivatives=[-10, -11])
        depA_ = depA2.copy()
        depB_ = depA_.add(depB, key=1)

        self.assertAllEqual(depA_.names, [[1, 0], [100, 3]])
        self.assertAllEqual(depA_.derivatives, [[12, 0], [-10, 4]])
        self.assertAllEqual(depB_.names, [0, 101])
        self.assertAllEqual(depB_.derivatives, [0, -11])

        # Calling :meth:`add` with a longer key:
        depB = Dependency(names=55, derivatives=-30)
        depA_ = depA2.copy()
        depB_ = depA_.add(depB, key=(0, 0))

        self.assertAllEqual(depA_.names, [[1, 0], [0, 3]])
        self.assertAllEqual(depA_.derivatives, [[12, 0], [0, 4]])
        self.assertAllEqual(depB_.names, 55)
        self.assertAllEqual(depB_.derivatives, -30)

        # Calling :meth:`add` with a key and with broadcasting:
        depB = Dependency(names=22, derivatives=222)
        depA_ = depA2.copy()
        depB_ = depA_.add(depB, key=(1,))

        self.assertAllEqual(depA_.names, [[1, 0], [22, 3]])
        self.assertAllEqual(depA_.derivatives, [[12, 0], [222, 4]])
        self.assertAllEqual(depB_.names, [0, 22])
        self.assertAllEqual(depB_.derivatives, [0, 222])

        # Letting :meth:`add` fail, without a key:
        depB = depA2.copy()
        depA_ = depA.copy()
        with self.assertRaises(ValueError):
            depB_ = depA_.add(depB)
            # ValueError: non-broadcastable output operand with shape
            # (2,) doesn't match the broadcast shape (2,2)

        # Letting :meth:`add` fail another time, this time *with* a
        # key:
        depB = depA.copy()
        depA_ = depA.copy()
        with self.assertRaises(ValueError):
            depB_ = depB.add(depA_, key=0)
            # ValueError: setting an array element with a sequence.

    def test_masking(self):
        dep = Dependency(names=[1, 2], derivatives=[10, 11])

        # Masking with an ndarray of the same shape:
        masked = dep & numpy.asarray([True, False])
        self.assertAllEqual(masked.names, [1, 0])
        self.assertAllEqual(masked.derivatives, [10, 0])

        # Masking with an ndarray of smaller shape:
        masked = dep & numpy.asarray(True)
        self.assertAllEqual(masked.names, [1, 2])
        self.assertAllEqual(masked.derivatives, [10, 11])

        # Masking with an ndarray of larger shape:
        masked = dep & numpy.asarray([[True, False], [False, True]])
        self.assertAllEqual(masked.names, [[1, 0], [0, 2]])
        self.assertAllEqual(masked.derivatives, [[10, 0], [0, 11]])

    def test_multiplication(self):
        dep = Dependency(names=[1, 2], derivatives=[10, 11])

        # Multiplying with an ndarray of the same shape:
        product = dep * numpy.asarray([1.5, 1])
        self.assertAllEqual(product.names, [1, 2])
        self.assertAllEqual(product.derivatives, [15, 11])

        # Multiplying with an ndarray of smaller shape:
        product = dep * numpy.asarray(2)
        self.assertAllEqual(product.names, [1, 2])
        self.assertAllEqual(product.derivatives, [20, 22])

        # Multiplying with an ndarray of larger shape:
        product = dep * numpy.asarray([[4, 5], [6, 7]])
        self.assertAllEqual(product.names, [[1, 2], [1, 2]])
        self.assertAllEqual(product.derivatives, [[40, 55], [60, 77]])

        with self.assertRaisesRegex(TypeError,
                "^unsupported operand type\(s\) for \*: "
                "'int' and 'Dependency'$"):
            product = numpy.asarray([4, 5]) * dep

            # With :meth:`Dependency.__rmul__` defined this would
            # return an object-dtype ndarray::
            #
            #   [Dependency(names=1, derivatives=40),
            #    Dependency(names=2, derivatives=55)]

        with self.assertRaisesRegex(TypeError,
                "^unsupported operand type\(s\) for \*: "
                "'int' and 'Dependency'$"):
            product = numpy.asarray(3) * dep

            # With :meth:`Dependency.__rmul__` defined this would
            # return an object-dtype ndarray::
            #
            #   [Dependency(names=1, derivatives=30),
            #    Dependency(names=2, derivatives=33)]

        with self.assertRaisesRegex(TypeError,
                "^unsupported operand type\(s\) for \*: "
                "'int' and 'Dependency'$"):
            product = numpy.asarray([[11, 22], [33, 44]]) * dep

            # With :meth:`Dependency.__rmul__` defined this would
            # return an object-dtype ndarray::
            #
            #   [[Dependency(names=1, derivatives=110),
            #     Dependency(names=2, derivatives=242)],
            #    [Dependency(names=1, derivatives=333),
            #     Dependency(names=2, derivatives=484)]]

        with self.assertRaisesRegex(TypeError,
                "^unsupported operand type\(s\) for \*: "
                "'int' and 'Dependency'$"):
            product = 3 * dep

            # With :meth:`Dependency.__rmul__` defined, this would
            # *work*; it would return a Depdendency::
            #
            #   Depdendency(names=[1, 2], derivatives=[30, 33])

        with self.assertRaisesRegex(TypeError,
                "^can't multiply sequence by non-int of type "
                "'Dependency'$"):
            product = [1, 2, 3] * dep

            # Also with :meth:`Dependency.__rmul__` defined, this
            # would fail with::
            #
            #   ValueError: operands could not be broadcast together
            #   with shapes (2,) (3,)
            #
            # However, ``product = [1, 42] * dep`` *would* work, with
            # result::
            #
            #   Dependency(names=[1, 2], derivatives=[10, 462])

    def test_getitem(self):
        a = Dependency(names=[1, 2], derivatives=[10, 11])
        b = a[1]

        a.names[1] = 22
        a.derivatives[1] = 111

        self.assertAllEqual(b.names, 2)
        self.assertAllEqual(b.derivatives, 11)

        self.assertAllEqual(a.names, [1, 22])
        self.assertAllEqual(a.derivatives, [10, 111])

        a = Dependency(
                names=[[1, 2], [3, 4]],
                derivatives=[[10, 11], [12, 13]])
        b = a[:, 0]

        self.assertAllEqual(b.names, [1, 3])
        self.assertAllEqual(b.derivatives, [10, 12])

        b.names[0] = 42
        b.derivatives[0] = 43

        self.assertAllEqual(b.names, [42, 3])
        self.assertAllEqual(b.derivatives, [43, 12])

        self.assertAllEqual(a.names, [[1, 2], [3, 4]])
        self.assertAllEqual(a.derivatives, [[10, 11], [12, 13]])

    def test_clear(self):
        dep = Dependency(
                names=[[1, 2], [3, 4]],
                derivatives=[[10, 11], [12, 13]])
        dep.clear((slice(0, 2), 0))

        self.assertAllEqual(dep.names, [[0, 2], [0, 4]])
        self.assertAllEqual(dep.derivatives, [[0, 11], [0, 13]])

    def test_len(self):
        dep = Dependency(
                names=[[1, 2], [3, 4]],
                derivatives=[[10, 11], [12, 13]])
        self.assertEqual(len(dep), 2)

        dep = Dependency(names=42, derivatives=12)
        with self.assertRaisesRegex(IndexError,
                '^tuple index out of range$'):
            len(dep)

    def test_compress(self):
        dep = Dependency(
                names=[[1, 2], [3, 4]],
                derivatives=[[10, 11], [12, 13]])
        result = numpy.compress(
                condition=[False, True],
                a=dep,
                axis=0)

        dep.names[1, 0] = 42
        dep.derivatives[1, 0] = 1

        self.assertAllEqual(result.names, [[3, 4]])
        self.assertAllEqual(result.derivatives, [[12, 13]])

    def test_flatten(self):
        dep = Dependency(
                names=numpy.asarray([[1, 3], [2, 4]]).T,
                derivatives=[[10, 11], [12, 13]])
        result = dep.flatten()
            # You cannot use :func:`numpy.ravel`.

        dep.names[0, 0] = 42
        dep.derivatives[0, 0] = 1

        self.assertAllEqual(result.names, [1, 2, 3, 4])
        self.assertAllEqual(result.derivatives, [10, 11, 12, 13])

    def test_repeat(self):
        dep = Dependency(
                names=[[1, 2], [3, 4]],
                derivatives=[[10, 11], [12, 13]])
        repeated = numpy.repeat(dep, [2, 3], axis=1)
        # It is obvious that *repeated* has copied elements.

        self.assertAllEqual(repeated.names,
                [[1, 1, 2, 2, 2], [3, 3, 4, 4, 4]])
        self.assertAllEqual(repeated.derivatives,
                [[10, 10, 11, 11, 11], [12, 12, 13, 13, 13]])

        dep = Dependency(names=[1], derivatives=[42])
        repeated = numpy.repeat(dep, [1], axis=0)

        dep.names[0] = 2
        dep.derivatives[0] = 43

        self.assertAllEqual(repeated.names, [1])
        self.assertAllEqual(repeated.derivatives, [42])

    def test_reshape(self):
        a = numpy.asarray([[1, 3], [2, 4]]).T
        b = numpy.asarray([[1, 2], [3, 4]])
        self.assertAllEqual(a, [[1, 2], [3, 4]])

        bx = numpy.reshape(b, (4,))
        self.assertAllEqual(bx, [1, 2, 3, 4])
        ax = numpy.reshape(a, (4,))
        self.assertAllEqual(ax, [1, 2, 3, 4])

        dep = Dependency(names=a, derivatives=b)
        reshaped = dep.reshape((4,))
            # :func:`numpy.reshape` cannot be used, it returns an
            # ``object``-dtype ndarray.
        a[0, 0] = 5
        b[0, 0] = 6
        self.assertAllEqual(dep.names, [[5, 2], [3, 4]])
        self.assertAllEqual(dep.derivatives, [[6, 2], [3, 4]])
        self.assertAllEqual(reshaped.names, [1, 2, 3, 4])
        self.assertAllEqual(reshaped.derivatives, [1, 2, 3, 4])

    def test_transpose(self):
        dep = Dependency(
                names=[[1, 2], [3, 4]],
                derivatives=[[10, 11], [12, 13]])
        transposed = numpy.transpose(dep)
        dep.names[0, 0] = 10
        dep.derivatives[0, 0] = 100
        self.assertAllEqual(transposed.names, [[1, 3], [2, 4]])
        self.assertAllEqual(transposed.derivatives, [[10, 12], [11, 13]])

        a = numpy.asarray([[[1], [2]], [[3], [4]]])
        self.assertAllEqual(a.T, [[[1, 3], [2, 4]]])
            # Notice that ``.T`` *reverses* the order of *all* axes.

        dep = Dependency(
                names=[[[1], [2]], [[3], [4]]],
                derivatives=[[[10], [11]], [[12], [13]]])
        transposed = numpy.transpose(dep)
        self.assertAllEqual(transposed.names,
                [[[1, 3], [2, 4]]])
        self.assertAllEqual(transposed.derivatives,
                [[[10, 12], [11, 13]]])

        transposed = numpy.transpose(dep, (0, 2, 1))
            # Reverses the two last axes.
        self.assertAllEqual(transposed.names,
                [[[1, 2]], [[3, 4]]])
        self.assertAllEqual(transposed.derivatives,
                [[[10, 11]], [[12, 13]]])

    def test_string_conversion(self):
        dep1 = Dependency(names=1, derivatives=42)
        dtype1 = numpy.dtype(numpy.int)
        self.assertEqual(str(dep1),
                "<()-shaped {}-typed Dependency>".format(dtype1))
            # The actual width of the default numpy int dtype might
            # depend on architecture, i.e., it might now everywhere be
            # equal to ``numpy.int64``.

        dep2 = Dependency(names=[1.0, 2.0], derivatives=[42.0, 100.0])
        dtype2 = numpy.dtype(numpy.float)
        self.assertEqual(repr(dep2),
                "<(2,)-shaped {}-typed Dependency>".format(dtype2))
