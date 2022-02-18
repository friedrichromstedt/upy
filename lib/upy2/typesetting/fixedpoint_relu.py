# Developed since: December 2021
# Based on work dating back to Feburary 2010

from upy2.typesetting.rules import TypesetNumberRule, LeftRule
from upy2.typesetting.numbers import \
        TypesetNumber, get_position_of_leftmost_digit, NumberTypesetter
from upy2.typesetting.protocol import Typesetter, Convention
import upy2.sessions


class FixedpointRelativeURule:
    """ Formats relative uncertainties using fixed-point notation. """

    def __init__(self, separator, infinity):
        self.separator = separator
        self.infinity = infinity

        self.uncertainty_rule = TypesetNumberRule()

    def apply(self, uncertainty):
        representation = '1{sep}{uncertainty}'.format(
                sep=self.separator,
                uncertainty=self.uncertainty_rule.apply(uncertainty),
        )
        return representation

    def apply_infinity(self):
        infinity = TypesetNumber(left=self.infinity, point='', right='')
        representation = '1{sep}{infinity}'.format(
                sep=self.separator,
                infinity=self.uncertainty_rule.apply(infinity),
        )
        return representation


convention_session = upy2.sessions.byprotocol(Convention)

class FixedpointRelativeUTypesetter(Typesetter):
    def __init__(self, stddevs, precision):
        Typesetter.__init__(self)

        self.uncertainty_typesetter = NumberTypesetter(ceil=True)

        self.stddevs = stddevs
        self.precision = precision

    def typeset_element(self, element, rule):
        nominal = element.nominal
        uncertainty = self.stddevs * element.stddev

        if nominal != 0:
            # The nominal value is nonzero.
            relative_uncertainty = uncertainty / abs(nominal)
            pos_leftmost_digit = \
                    get_position_of_leftmost_digit(relative_uncertainty)

            if pos_leftmost_digit is not None:
                # The relative uncertainty is nonzero.
                precision = pos_leftmost_digit + (self.precision - 1)
                typeset_uncertainty = \
                        self.uncertainty_typesetter.typesetfp(
                                relative_uncertainty, precision)
                return rule.apply(typeset_uncertainty)

            else:
                # The relative uncertainty is zero.
                typeset_uncertainty = \
                        self.uncertainty_typesetter.typesetfp(
                                number=0, precision=0)
                return rule.apply(typeset_uncertainty)

        elif uncertainty != 0:
            # The nominal value is zero, and the uncertainty is not.
            return rule.apply_infinity()

        else:
            # Both nominal value as well as uncertainty are zero.
            typeset_uncertainty = \
                    self.uncertainty_typesetter.typesetfp(
                            number=0, precision=0)
            return rule.apply(typeset_uncertainty)

    def deduce_rule(self):
        manager = convention_session.current()
        return FixedpointRelativeURule(
                separator=manager.get_separator(),
                infinity=manager.get_infinity(),
        )
