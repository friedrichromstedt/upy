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
            unit=None,
    ):
        Typesetter.__init__(self)

        self.nominal_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_value)

        self.precision = precision

        self.utypesetter = utypesetter
        self.unit = unit

    def typeset_element(self, element, rule):
        nominal = element.nominal

        uncertainty = self.utypesetter.typeset_element(
                element, rule=rule.uncertainty_rule)

        pos_leftmost_digit = get_position_of_leftmost_digit(nominal)

        if pos_leftmost_digit is not None:
            typeset_nominal = self.nominal_typesetter.typesetfp(
                    nominal, precision=\
                            (pos_leftmost_digit + self.precision - 1))
            return rule.apply(
                    nominal=typeset_nominal,
                    uncertainty=uncertainty)

        else:
            typeset_nominal = self.nominal_typesetter.typesetfp(
                    number=0, precision=0)
            return rule.apply(
                    nominal=typeset_nominal,
                    uncertainty=uncertainty)

    def deduce_rule(self):
        manager = convention_session.current()
        uncertainty_rule = self.utypesetter.deduce_rule()

        return RelativeFixedpointRule(
                uncertainty_rule=uncertainty_rule,
                padding=manager.get_padding(),
                unit=self.unit)
