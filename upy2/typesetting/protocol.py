# Developed since: October 2016

""" Defines the Typesetter Protocol Class and registers a typesetter
Context at :mod:`upy2.context`. """

from upy2.context import define, Protocol


class Typesetter(Protocol):
    def typeset(self, uarray):
        raise RuntimeError('Virtual method called')

define(Typesetter)
