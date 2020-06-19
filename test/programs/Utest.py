# Developed since: Jun 2020

import threading
from upy2 import U
import upy2.sessions


echolock = threading.Lock()
def echo(message):
    with echolock:
        print message


class TestSuite(object):
    def __init__(self):
        self.ok = True
        self.assertions = 0
        self.oklock = threading.Lock()

    def assertIs(self, a, b, description):
        with self.oklock:
            if a is not b:
                self.ok = False
                echo("{2}: {0} is not {1}".format(a, b, description))
            self.assertions += 1

    def report(self):
        echo("asserted {} conditions.".format(self.assertions))
        if self.ok:
            echo("OK")
        else:
            echo("FAILED")

suite = TestSuite()


class SideThread(threading.Thread):
    def __init__(self, defaultU):
        threading.Thread.__init__(self)

        self.Cstart = threading.Condition()
        self.C1 = threading.Condition()
        self.C2 = threading.Condition()
        self.C3 = threading.Condition()
        self.C4 = threading.Condition()

        self.U_session = upy2.sessions.byprotocol(U)
        self.defaultU = defaultU

    def section1(self):
        pass
    def section2(self):
        pass
    def section3(self):
        pass

    def run(self):
        self.C1.acquire()
        with self.Cstart:
            self.Cstart.notify()

        self.C2.acquire()
        self.C1.wait()
        self.C1.release()

        self.section1()

        self.C3.acquire()
        self.C2.wait()
        self.C2.release()

        self.section2()

        self.C4.acquire()
        self.C3.wait()
        self.C3.notify()

        self.section3()

        self.C4.wait()
        self.C4.notify()


class SideThread1(SideThread):
    def section1(self):
        suite.assertIs(
                self.U_session.current(),
                self.defaultU,
                'side thread 1, section 1')

class SideThread2(SideThread):
    def section1(self):
        suite.assertIs(
                self.U_session.current(),
                self.defaultU,
                'side thread 2, section 1')


defaultU = U(2)
defaultU.default()

threadA = SideThread1(defaultU=defaultU)
threadB = SideThread2(defaultU=defaultU)
U_session = upy2.sessions.byprotocol(U)

with threadA.Cstart, threadB.Cstart:
    threadA.start()
    threadB.start()
    threadA.Cstart.wait()
    threadB.Cstart.wait()

with threadA.C1, threadB.C1:
    threadA.C1.notify()
    threadB.C1.notify()

# Section 1:
suite.assertIs(U_session.current(), defaultU,
        'main thread, section 1')

with threadA.C2, threadB.C2:
    defaultU.undefault()

    threadA.C2.notify()
    threadB.C2.notify()

# Section 2:

with threadA.C3, threadB.C3:
    threadA.C3.notify()
    threadB.C3.notify()

# Section 3:

with threadA.C4, threadB.C4:
    threadA.C4.notify()
    threadB.C4.notify()

suite.report()
