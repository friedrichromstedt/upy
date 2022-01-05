# Developed since: December 2021
# Based on work dating back to February 2020

from upy2.typesetting.numbers import \
        get_position_of_leftmost_digit, NumberTypesetter
from upy2.typesetting.rules import \
        LeftRule, RightRule, TypesetNumberRule
from upy2.typesetting.protocol import Typesetter, Convention
import upy2.sessions


class RelativeEngineeringRule:
    def __init__(self, uncertainty_rule, padding):
        self.uncertainty_rule = uncertainty_rule
        self.padding = padding

        self.nominal_rule = TypesetNumberRule()
        self.base_rule = LeftRule()
        self.exponent_rule = RightRule()
        self.unit_rule = RightRule()

    def apply(self, nominal, uncertainty, exponent=None, unit=None):
        """ *nominal* is a ``TypesetNumber``.  *uncertainty*, *exponent*
        and *unit* are, if given, strings. """

        if exponent is not None:
            typeset_power = '{base}{exponent}'.format(
                    base=self.base_rule.apply(' 10^'),
                    exponent=self.exponent_rule.apply(exponent))
        else:
            typeset_power = '{base}{exponent}'.format(
                    base='', exponent='')

        if unit is not None:
            typeset_unit = self.unit_rule.apply(' {}'.format(unit))
        else:
            typeset_unit = self.unit_rule.apply('')

        typeset_nominal = self.nominal_rule.apply(nominal)

        return '{nominal}{power} ({uncertainty}){unit}{padding}'.format(
                nominal=typeset_nominal,
                power=typeset_power,
                uncertainty=uncertainty,
                unit=typeset_unit,
                padding=self.padding,
        )


convention_session = upy2.sessions.byprotocol(Convention)

class RelativeEngineeringTypesetter(Typesetter):
    def __init__(self,
            precision, utypesetter,
            typeset_possign_value=None, typeset_possign_exponent=None,
            unit=None, useprefixes=None,
    ):
        Typesetter.__init__(self)
        self.utypesetter = utypesetter

        if typeset_possign_value is None:
            typeset_possign_value = False
        if typeset_possign_exponent is None:
            typeset_possign_exponent = False
        if useprefixes is None:
            useprefixes = False

        self.nominal_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_value)
        self.exponent_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_exponent)

        self.relative_precision = precision
        self.unit = unit
        self.useprefixes = useprefixes

    def typeset_element(self, element, rule):
        nominal = element.nominal

        typeset_uncertainty = self.utypesetter.typeset_element(
                element, rule=rule.uncertainty_rule)

        pos_leftmost_digit = \
                get_position_of_leftmost_digit(nominal)

        # Compare also to :class:`EngineeringTypesetter`.

        if pos_leftmost_digit is not None:
            exponent = 3 * (-pos_leftmost_digit // 3)
            mantissa = nominal * 10 ** (-exponent)
            precision = \
                    (pos_leftmost_digit + exponent) + \
                    (self.relative_precision - 1)

            typeset_mantissa = self.nominal_typesetter.typesetfp(
                    mantissa, precision)
            typeset_exponent = self.exponent_typesetter.typesetint(
                    exponent, precision=0)

        else:
            exponent = 0

            typeset_mantissa = self.nominal_typesetter.typesetfp(
                    number=0, precision=0)
            typeset_exponent = self.exponent_typesetter.typesetint(
                    number=0, precision=0)

        if self.unit is not None and self.useprefixes and \
                -24 <= exponent <= 24:
            # Express the exponent by means of a prefix.
            if exponent == -24:  # Yokto
                prefix = 'y'
            elif exponent == -21:  # Zepto
                prefix = 'z'
            elif exponent == -18:  # Atto
                prefix = 'a'
            elif exponent == -15:  # Femto
                prefix = 'f'
            elif exponent == -12:  # Piko
                prefix = 'p'
            elif exponent == -9:  # Nano
                prefix = 'n'
            elif exponent == -6:  # Mikro
                prefix = 'u'
            elif exponent == -3:  # Milli
                prefix = 'm'
            elif exponent == 0:
                prefix = ''
            elif exponent == 3:  # Kilo
                prefix = 'k'
            elif exponent == 6:  # Mega
                prefix = 'M'
            elif exponent == 9:  # Giga
                prefix = 'G'
            elif exponent == 12:  # Tera
                prefix = 'T'
            elif exponent == 15:  # Peta
                prefix = 'P'
            elif exponent == 18:  # Exa
                prefix = 'E'
            elif exponent == 21:  # Zetta
                prefix = 'Z'
            elif exponent == 24:  # Yotta
                prefix = 'Y'

            return rule.apply(
                    nominal=typeset_mantissa,
                    uncertainty=typeset_uncertainty,
                    unit='{prefix}{base}'.format(prefix, self.unit),
            )
        elif self.unit is not None:
            # Append the unit as-is.
            return rule.apply(
                    nominal=typeset_mantissa,
                    uncertainty=typeset_uncertainty,
                    exponent=typeset_exponent,
                    unit=self.unit,
            )
        else:
            # Do not append a unit.
            return rule.apply(
                    nominal=typeset_mantissa,
                    uncertainty=typeset_uncertainty,
                    exponent=typeset_exponent,
            )

    def deduce_rule(self):
        manager = convention_session.current()
        uncertainty_rule = self.utypesetter.deduce_rule()

        return RelativeEngineeringRule(
                uncertainty_rule=uncertainty_rule,
                padding=manager.get_padding(),
        )
