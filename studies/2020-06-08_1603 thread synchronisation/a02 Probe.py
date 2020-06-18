# Developed since: Jun 2020

import time
import threading


class SideThread(threading.Thread):
    def __init__(self, printlock):
        threading.Thread.__init__(self)

        self.Cstart = threading.Condition()
        self.C1 = threading.Condition()
        self.C2 = threading.Condition()
        self.C3 = threading.Condition()
        self.C4 = threading.Condition()

        self.printlock = printlock

    def echo(self, message):
        with self.printlock:
            print message

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
        self.echo("thread1: Entering section 1")
        self.echo("thread1: Leaving section 1")

    def section2(self):
        self.echo("thread1: Entering section 2")
        self.echo("thread1: sleep 1")
        time.sleep(1)
        self.echo("thread2: Leaving section2")

    def section3(self):
        self.echo("thread1: Entering section 3")
        self.echo("thread1: sleep 1")
        time.sleep(1)
        self.echo("thread1: Leaving section 3")


class SideThread2(SideThread):

    def section1(self):
        self.echo("thread2: Entering section 1")
        self.echo("thread2: Leaving section 1")

    def section2(self):
        self.echo("thread2: Entering section 2")
        self.echo("thread2: Leaving section 2")

    def section3(self):
        self.echo("thread2: Entering section 3")
        self.echo("thread2: sleep 2")
        time.sleep(2)
        self.echo("thread2: Leaving section 3")


printlock = threading.Lock()
threadA = SideThread1(printlock=printlock)
threadB = SideThread2(printlock=printlock)

def echo(message):
    with printlock:
        print message

with threadA.Cstart, threadB.Cstart:
    threadA.start()
    threadB.start()
    threadA.Cstart.wait()
    threadB.Cstart.wait()

with threadA.C1, threadB.C1:
    print "Passing initial barrier"
    print
    threadA.C1.notify()
    threadB.C1.notify()

# Section 1:
echo("main thread: Entering section 1")
echo("main thread: sleep 1")
time.sleep(1)
echo("main thread: Leaving section 1")

with threadA.C2, threadB.C2:
    print
    print "Passing barrier between section 1 and 2"
    print
    threadA.C2.notify()
    threadB.C2.notify()

# Section 2:
echo("main thread: Entering section 2")
echo("main thread: Leving section 2")

with threadA.C3, threadB.C3:
    print
    print "Passing barrier between section 2 and 3"
    print
    threadA.C3.notify()
    threadB.C3.notify()

# Section 3:
echo("main thread: Entering section 3")
echo("main thread: Leaving section 3")

with threadA.C4, threadB.C4:
    print
    print "Passing final barrier"
    threadA.C4.notify()
    threadB.C4.notify()
