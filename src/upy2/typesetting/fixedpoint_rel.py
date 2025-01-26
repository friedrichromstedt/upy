# Developed since: December 2021
# Based on work dating back to February 2010

from upy2.typesetting.rules import \
        TypesetNumberRule
from upy2.typesetting.numbers import \
        NumberTypesetter, get_position_of_leftmost_digit
from upy2.typesetting.protocol import Typesetter, Convention
import upy2.sessions


class RelativeFixedpointRule:
    def __init__(self, uncertainty_rule, padding, unit=None):
        self.uncertainty_rule = uncertainty_rule
        self.padding = padding

        self.nominal_rule = TypesetNumberRule()

        if unit is None:
            self.unitsuffix = ''
        else:
            self.unitsuffix = ' {}'.format(unit)

    def apply(self, nominal, uncertainty):
        """ *nominal* is a ``TypesetNumber``, *uncertainty* is a string.
        """

        return '{nominal} ({uncertainty}){unit}{padding}'.format(
                nominal=self.nominal_rule.apply(nominal),
                uncertainty=uncertainty,
                unit=self.unitsuffix, padding=self.padding,
        )


convention_session = upy2.sessions.byprotocol(Convention)

class RelativeFixedpointTypesetter(Typesetter):
    def __init__(self,
            precision, utypesetter,
            typeset_possign_value=None,
            infinite_precision=None,
            unit=None,
    ):
        Typesetter.__init__(self)

        if infinite_precision is None:
            infinite_precision = 11

        self.nominal_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_value)

        self.relative_precision = precision
        self.infinite_precision = infinite_precision

        self.utypesetter = utypesetter
        self.unit = unit

    def typeset_element(self, element, rule):
        nominal = element.nominal
        uncertainty = element.stddev * self.utypesetter.stddevs

        typeset_uncertainty = self.utypesetter.typeset_element(
                element, rule=rule.uncertainty_rule)

        pos_leftmost_digit_nominal = \
                get_position_of_leftmost_digit(nominal)
        pos_leftmost_digit_uncertainty = \
                get_position_of_leftmost_digit(uncertainty)

        if pos_leftmost_digit_uncertainty is not None:
            precision = pos_leftmost_digit_uncertainty + \
                    self.relative_precision - 1
            typeset_nominal = self.nominal_typesetter.typesetfp(
                    nominal, precision)

        elif pos_leftmost_digit_nominal is not None:
            precision = pos_leftmost_digit_nominal + \
                    self.infinite_precision
            typeset_nominal = self.nominal_typesetter.typesetfp(
                    nominal, precision)

        else:
            typeset_nominal = self.nominal_typesetter.typesetfp(
                    number=0, precision=0)

        return rule.apply(
                nominal=typeset_nominal,
                uncertainty=typeset_uncertainty)

    def deduce_rule(self):
        manager = convention_session.current()
        uncertainty_rule = self.utypesetter.deduce_rule()

        return RelativeFixedpointRule(
                uncertainty_rule=uncertainty_rule,
                padding=manager.get_padding(),
                unit=self.unit)
