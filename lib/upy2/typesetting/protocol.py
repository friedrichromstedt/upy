# Developed since: October 2016

""" Defines the Typesetter Protocol Class and registers a typesetter
Session at :mod:`upy2.sessions`. """

from upy2.sessions import define, Protocol


class Typesetter(Protocol):
    def typeset(self, uarray):
        raise RuntimeError('Virtual method called')

define(Typesetter)
