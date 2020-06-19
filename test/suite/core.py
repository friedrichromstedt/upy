# Developed since: Jun 2020

import threading
import unittest
import numpy
import upy2
from upy2 import undarray, U, u
import upy2.sessions


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

        # Test the session ...

        U_session = upy2.sessions.byprotocol(U)

        with self.assertRaisesRegexp(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test :meth:`{default, undefault}`:
        U_session.default(x)
        self.assertIs(U_session.current(), x)
        U_session.undefault(x)
        with self.assertRaisesRegexp(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test :meth:`{register, unregister}`:
        U_session.register(x)
        self.assertIs(U_session.current(), x)
        U_session.unregister(x)
        with self.assertRaisesRegexp(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test combination of :meth:`{register, unregister}` and
        # :meth:{default, undefault}`:
        y = U(stddevs=3)
        U_session.default(x)
        U_session.register(y)
        self.assertIs(U_session.current(), y)
        U_session.undefault(x)
        self.assertIs(U_session.current(), y)
        U_session.unregister(y)
        with self.assertRaisesRegexp(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test order check in :meth:`undefault`:
        U_session.default(x)
        U_session.default(y)
        with self.assertRaisesRegexp(ValueError,
                '^Un-defaulting a session manager which is not '
                'the current default item$'):
            U_session.undefault(x)
        self.assertIs(U_session.current(), y)
        U_session.undefault(y)
        self.assertIs(U_session.current(), x)
        U_session.undefault(x)
        with self.assertRaisesRegexp(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        # Test order check in :meth:`unregister`:
        U_session.register(x)
        U_session.register(y)
        with self.assertRaisesRegexp(ValueError,
                '^The session manager to be unregistered is not '
                'the topmost entry on the stack$'):
            U_session.unregister(x)
        self.assertIs(U_session.current(), y)
        U_session.unregister(y)
        self.assertIs(U_session.current(), x)
        U_session.unregister(x)
        with self.assertRaisesRegexp(LookupError,
                '^No applicable session manager found$'):
            mgr = U_session.current()

        thread1 = SessionTestThread1()

        with thread1.Rx:
            thread1.start()
            thread1.Rx.wait()


        thread1 = SessionTestThread1()
        thread1.handle.acquire()

        thread1.start()
        thread1.handle.release()

        with thread1.done:
            thread1.start()
            thread1.done.wait()

        with thread1.done:
            thread1.proceed.notify()
            thread1.done.wait()


class SessionTestThread1(thrading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        U_session = upy2.sessions.byprotocol(U)

        self.Rx = threading.Condition()
        self.Tx = threading.Condition()


        self.handle = threading.Semaphore()

        self.proceed = threading.Event()
        self.done = threading.Event()

    def run(self):
        self.Rx.acquire()

        self.Tx.acquire()
        self.Rx.notify()
        self.Rx.release()


        with self.Rx:
            self.Rx.notify()


        with self.handle:
            pass

        self.done.set()
        self.proceed.wait()
