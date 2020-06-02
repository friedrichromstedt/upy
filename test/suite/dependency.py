# Developed since: Jun 2020

import unittest
import numpy
from upy2.dependency import Dependency


class Test_Dependency(unittest.TestCase):

    def assertAllEqual(self, a, b):
        if not numpy.all(a == b):
            raise AssertionError(
                'Not all equal:\n{a}\nand\n{b}'.format(a=a, b=b))

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
        with self.assertRaisesRegexp(ValueError,
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

        with self.assertRaisesRegexp(TypeError,
                "^unsupported operand type\(s\) for \*: "
                "'int' and 'Dependency'$"):
            product = numpy.asarray([4, 5]) * dep

            # With :meth:`Dependency.__rmul__` defined this would
            # return an object-dtype ndarray::
            #
            #   [Dependency(names=1, derivatives=40),
            #    Dependency(names=2, derivatives=55)]

        with self.assertRaisesRegexp(TypeError,
                "^unsupported operand type\(s\) for \*: "
                "'int' and 'Dependency'$"):
            product = numpy.asarray(3) * dep

            # With :meth:`Dependency.__rmul__` defined this would
            # return an object-dtype ndarray::
            #
            #   [Dependency(names=1, derivatives=30),
            #    Dependency(names=2, derivatives=33)]

        with self.assertRaisesRegexp(TypeError,
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

        with self.assertRaisesRegexp(TypeError,
                "^unsupported operand type\(s\) for \*: "
                "'int' and 'Dependency'$"):
            product = 3 * dep

            # With :meth:`Dependency.__rmul__` defined, this would
            # *work*; it would return a Depdendency::
            #
            #   Depdendency(names=[1, 2], derivatives=[30, 33])

        with self.assertRaisesRegexp(TypeError,
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
