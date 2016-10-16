# Developed since: October 2016

""" Defines the Typesetter Protocol Class and registers a typesetter
Context at :mod:`upy2.context`. """

from upy2.context import define, ContextProvider


class Typesetter(ContextProvider):
    def typeset(self, uarray):
        raise RuntimeError('Virtual method called')

define(Typesetter)
