# Developed since: October 2016

""" Defines the Typesetter Protocol Class and registers a typesetter
Session at :mod:`upy2.sessions`. """

import numpy
from upy2.sessions import define, Protocol


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


class Typesetter(Protocol):
    def typeset_element(self, element, rule):
        """ This method should return a string corresponding to the
        scalar undarray *element*, ruled by *rule*.  """

        raise NotImplementedError("Virtual method called")

    def deduce_rule(self):
        """ Returns a Rule used to align the elements of a single
        undarray to be typeset. """

        raise NotImplementedError('Virtual method called')

    def typeset(self, uarray):
        """ Creates an object-dtype ndarray holding
        ElementTypesetters, one for each element of *uarray*, and
        typesets this object-dtype ndarray by string conversion. """

        element_typesetters = numpy.zeros(uarray.shape, dtype=object)
        rule = self.deduce_rule()

        for index in numpy.ndindex(uarray.shape):
            element_typesetters[index] = \
                    ElementTypesetter(
                            element=uarray[index],
                            typesetter=self,
                            rule=rule,
                    )

#        iterator = numpy.nditer([uarray.nominal],
#                flags=['multi_index'])
#        for nominal, stddev in iterator:
#            element_typesetters[iterator.multi_index] = \
#                    ElementTypesetter(
#                            nominal=nominal,
#                            stddev=stddev,
#                            typesetter=self,
#                            rule=rule,
#                    )

        str(element_typesetters); return str(element_typesetters)

define(Typesetter)
