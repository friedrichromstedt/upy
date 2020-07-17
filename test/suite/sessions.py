# Developed since: Jul 2020

import unittest
import upy2.sessions as sessionsm

import sys
py3 = (sys.version_info >= (3,))
py2 = not py3


class ProtocolTest(sessionsm.Protocol):
    def add(self, a, b):
        return (a + b)

sessionsm.define(ProtocolTest)


class DerivedProtocolTest(ProtocolTest):
    def __init__(self, coefficient):
        self.coefficient = coefficient

    def add(self, a, b):
        return self.coefficient * ProtocolTest.add(self, a, b)


class Unrelated(object):
    pass


class Test_Sessions(unittest.TestCase):
    
    def assertRaisesRegex(self, *args, **kwargs):
        if py2:
            return unittest.TestCase.assertRaisesRegexp(self, *args, **kwargs)
        else:
            return unittest.TestCase.assertRaisesRegex(self, *args, **kwargs)

    def test_retrieval(self):
        session = sessionsm.byprotocol(ProtocolTest)
        self.assertIs(session, sessionsm.byprotocol(
            DerivedProtocolTest))

        self.assertIs(session, sessionsm.byprotocolobj(
            ProtocolTest()))
        self.assertIs(session, sessionsm.byprotocolobj(
            DerivedProtocolTest(42)))

        with self.assertRaisesRegex(KeyError,
                '^"No Session defined for protocol {}"$'.\
                        format(Unrelated)):
            sessionsm.byprotocol(Unrelated)

        protocolobj = Unrelated()
        with self.assertRaisesRegex(KeyError,
                "^'No Session defined for protocol object "
                "{}'$".format(protocolobj)):
            sessionsm.byprotocolobj(protocolobj)

    def test_instances(self):
        session = sessionsm.byprotocol(ProtocolTest)

        protocolobj = ProtocolTest()
        derivedprotocolobj = DerivedProtocolTest(42)


        protocolobj.default()
        self.assertIs(session.current(), protocolobj)

        derivedprotocolobj.default()
        self.assertIs(session.current(), derivedprotocolobj)

        with self.assertRaisesRegex(ValueError,
                '^Un-defaulting a session manager which is not the '
                'current default item$'):
            protocolobj.undefault()

        derivedprotocolobj.undefault()
        protocolobj.undefault()

        with self.assertRaisesRegex(LookupError,
                '^No applicable session manager found$'):
            session.current()

        with protocolobj:
            manager = session.current()
            self.assertEqual(manager.add(1, 2), 3)

            with derivedprotocolobj:
                manager2 = session.current()
                self.assertEqual(manager2.add(1, 2), 126)

            manager3 = session.current()
            self.assertEqual(manager3.add(1, 2), 3)

        with self.assertRaisesRegex(LookupError,
                '^No applicable session manager found$'):
            session.current()

        session.register(derivedprotocolobj)
        self.assertIs(session.current(), derivedprotocolobj)

        session.register(protocolobj)
        self.assertIs(session.current(), protocolobj)

        with self.assertRaisesRegex(ValueError,
                '^The session manager to be unregistered is not the '
                'topmost entry on the stack$'):
            session.unregister(derivedprotocolobj)

        session.unregister(protocolobj)
        self.assertIs(session.current(), derivedprotocolobj)
        session.unregister(derivedprotocolobj)

        with self.assertRaisesRegex(LookupError,
                '^No applicable session manager found$'):
            session.current()
