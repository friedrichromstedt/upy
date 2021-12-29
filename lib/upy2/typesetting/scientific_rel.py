# Develoded since: December 2021
# Based on work dating back to February 2010

from upy2.typesetting.numbers import \
        get_position_of_leftmost_digit, NumberTypesetter
from upy2.typesetting.rules import \
        RightRule, LeftRule, TypesetNumberRule
from upy2.typesetting.protocol import Typesetter, Convention
import upy2.sessions


class RelativeScientificRule:
    def __init__(self, uncertainty_rule, padding, unit=None):
        self.uncertainty_rule = uncertainty_rule
        self.padding = padding

        self.mantissa_rule = TypesetNumberRule()
        self.exponent_rule = RightRule()

        if unit is None:
            self.unitsuffix = ''
        else:
            self.unitsuffix = ' {}'.format(unit)

    def apply(self,
            nominal_mantissa, nominal_exponent,
            uncertainty):
        """ *nominal_mantissa* is a ``TypesetNumber``, *exponent* and
        *uncertainty* are strings. """
        mantissa = self.mantissa_rule.apply(nominal_mantissa)
        exponent = self.exponent_rule.apply(nominal_exponent)

        return '{mantissa} 10^{exponent} ({uncertainty}){unit}{padding}'.\
                format(
                    mantissa=mantissa, exponent=exponent,
                    uncertainty=uncertainty, unit=self.unitsuffix,
                    padding=self.padding,
                )


convention_session = upy2.sessions.byprotocol(Convention)

class RelativeScientificTypesetter(Typesetter):
    def __init__(self,
            precision, utypesetter,
            typeset_possign_value=None, typeset_possign_exponent=None,
            unit=None,
    ):
        Typesetter.__init__(self)

        self.mantissa_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_value)
        self.exponent_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_exponent)

        self.mantissa_precision = precision

        self.utypesetter = utypesetter
        self.unit = unit

    def typeset_element(self, element, rule):
        nominal = element.nominal

        uncertainty = self.utypesetter.typeset_element(
                element, rule=rule.uncertainty_rule)

        pos_leftmost_digit = \
                get_position_of_leftmost_digit(nominal)

        if pos_leftmost_digit is not None:
            exponent = -pos_leftmost_digit
            mantissa = nominal * 10 ** (-exponent)

            typeset_mantissa = self.mantissa_typesetter.typesetfp(
                    mantissa, precision=(self.mantissa_precision - 1))
            typeset_exponent = self.exponent_typesetter.typesetint(
                    exponent, precision=0)

            return rule.apply(
                    nominal_mantissa=typeset_mantissa,
                    nominal_exponent=typeset_exponent,
                    uncertainty=uncertainty)

        else:
            typeset_mantissa = self.mantissa_typesetter.typesetfp(
                    number=0, precision=0)
            typeset_exponent = self.exponent_typesetter.typesetint(
                    number=0, precision=0)
            return rule.apply(
                    nominal_mantissa=typeset_mantissa,
                    nominal_exponent=typeset_exponent,
                    uncertainty=uncertainty)

    def deduce_rule(self):
        manager = convention_session.current()
        uncertainty_rule = self.utypesetter.deduce_rule()

        return RelativeScientificRule(
                uncertainty_rule=uncertainty_rule,
                padding=manager.get_padding(),
                unit=self.unit)
