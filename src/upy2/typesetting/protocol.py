# Developed since: October 2016

""" Defines the Typesetter Protocol Class and registers a typesetter
Session at :mod:`upy2.sessions`. """

import numpy
import upy2.sessions


class ElementTypesetter:
    """ Instances of :class:`ElementTypesetter` will be used to
    populate object-dtype ndarrays corresponding to an ``undarray``
    subject to typesetting. """

    def __init__(self, element, typesetter, rule):
        """ *element* is a scalar ``undarray``; *typesetter* is the
        :class:`Typesetter` instance responsible for this Element
        Typesetter and *rule* is used to align all elements output.

        The *rule* will be shared by all Element Typesetters
        corresponding to elements of the same ``undarray``; the
        *typesetter* is the Typesetter Session Manager used. """

        self.element = element
        self.typesetter = typesetter
        self.rule = rule

    def __repr__(self):
        """ Notice that ``str`` conversion of an object-dtype ndarray
        prefers :meth:`__repr__` of the ndarray's elements. """

        return self.typesetter.typeset_element(
                element=self.element, rule=self.rule)


class Typesetter(upy2.sessions.Protocol):
    def typeset_element(self, element, rule):
        """ This method should return a string corresponding to the
        scalar undarray *element*, ruled by *rule*.  """

        raise NotImplementedError("Virtual method called")

    def deduce_rule(self):
        """ Returns a Rule used to align the elements of a single
        undarray to be typeset. """

        raise NotImplementedError('Virtual method called')

    def element_typesetters(self, uarray):
        """ Creates an object-dtype ndarray holding
        ElementTypesetters, one for each element of *uarray*."""

        element_typesetters = numpy.zeros(uarray.shape, dtype=object)
        rule = self.deduce_rule()

        for index in numpy.ndindex(uarray.shape):
            element_typesetters[index] = \
                    ElementTypesetter(
                            element=uarray[index],
                            typesetter=self,
                            rule=rule,
                    )
        return element_typesetters

    def typeset(self, uarray):
        """ Typeseys *uarray* by passing the results of
        ``self.element_typesetters(uarray)`` twice through ``str``. """

        element_typesetters = self.element_typesetters(uarray)

        str(element_typesetters); return str(element_typesetters)

upy2.sessions.define(Typesetter)


class Convention(upy2.sessions.Protocol):
    def __init__(self,
            plusminus=None, separator=None,
            negative=None,
            infinity=None,
            padding=None,
            inherit=None):
        if separator is not None:
            self.separator = separator
        elif plusminus is not None:
            self.separator = u' {} '.format(plusminus)
        elif inherit is not None:
            self.separator = inherit.separator
        else:
            self.separator = ' +- '

        if negative is not None:
            self.negative = negative
        elif inherit is not None:
            self.negative = inherit.negative
        else:
            self.negative = '-'

        if padding is not None:
            self.padding = padding
        elif inherit is not None:
            self.padding = inherit.padding
        else:
            self.padding = ' '

        if infinity is not None:
            self.infinity = infinity
        elif inherit is not None:
            self.infinity = inherit.infinity
        else:
            self.infinity = 'oo'

    def get_separator(self):
        return self.separator

    def get_negative(self):
        return self.negative

    def get_infinity(self):
        return self.infinity

    def get_padding(self):
        return self.padding

upy2.sessions.define(Convention)
Convention().default()
