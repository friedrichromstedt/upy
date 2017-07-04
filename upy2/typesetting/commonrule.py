# Developed since: Jul 2017

from upy2.typesetting.protocol import Typesetter


class Element(object):
    def __init__(self, typesetter):
        self.typesetter = typesetter

    def __repr__(self):
        return self.typesetter.typeset_element(self)


class Typesetter(Typesetter):
    def __init__(self, stddevs):
        Typesetter.__init__(self)

        self.stddevs = stddevs

    def typeset_element(self, element):
        raise RuntimeError('Virtual method called')

    def typeset(self, uarray):
        nominal = uarray.nominal.flatten()
        uncertainty = self.stddevs * uarray.stddev.flatten()
        N = len(nominal)

        elements = numpy.zeros(N, dtype=numpy.object)
        for index in xrange(0, N):
            elements[index] = CommonRuleElement(
                nominal=nominal[index],
                uncertainty=uncertainty[index],
                typesetter=self,
                rule=rule,
            )

        ready = elements.reshape(uarray.shape)
        str(ready); return str(ready)


class CommonRuleElement(object):
    def __init__(self,
            nominal, uncertainty,
            typesetter, rule,
    ):
        """ *nominal* and *uncertainty* are numbers.  *typesetter* is
        the :class:`CommonRuleTypesetter` instance this
        ``CommonRuleElement` belongs to.  *rule* will be handed over
        to the *typesetter* on string conversion in ``__repr__``. """

        self.nominal = nominal
        self.uncertainty = uncertainty,
        self.typesetter = typesetter
        self.rule = rule

    def __repr__(self):
        result = self.typesetter.typeset_element(
            nominal=self.nominal, uncertainty=self.uncertainty,
            rule=self.rule,
        )
        return result


class CommonRuleTypesetter(Typesetter):
    def __init__(self, stddevs):
        Typesetter.__init__(self)

        self.stddevs = stddevs

    def _provide_common_rule(self):
        """ This method is supposed to provide a "rule" which will be
        shared by all CommonRuleElements resulting from one
        :class:`undarray` instance. """

        raise RuntimeError('Virtual method called')

    def typeset_element(self, nominal, uncertainty, rule):
        """ This method implements typesetting a ``(nominal,
        uncertainty)`` pair using the Common Rule *rule*. """

        raise RuntimeError('Virtual method called')

    def typeset(self, uarray):
        """ Typeset the ``undarray`` instance *uarray* using some
        *common rule* provided by the classes derived from
        :class:`CommonRuleTypesetter`. """

        nominal = uarray.nominal.flatten()
        uncertainty = self.stddevs * uarray.stddev.flatten()
        N = len(nominal)

        rule = self._provide_common_rule()

        elements = numpy.zeros(N, dtype=numpy.object)
        for index in xrange(0, N):
            elements[index] = CommonRuleElement(
                nominal=nominal[index],
                uncertainty=uncertainty[index],
                typesetter=self,
                rule=rule,
            )

        ready = elements.reshape(uarray.shape)
        str(ready); return str(ready)
