# Developed since: Feb 2021

from upy2.typesetting.numbers import \
        get_position_of_leftmost_digit, NumberTypesetter
from upy2.typesetting.rules import TypesetNumberRule
from upy2.typesetting.protocol import Typesetter, Convention
import upy2.sessions


class FixedpointRule(object):
    """ Fixed-point rule. """

    def __init__(self, separator, padding, unit=None):
        self.nominal_rule = TypesetNumberRule()
        self.uncertainty_rule = TypesetNumberRule()

        self.separator = separator
        self.padding = padding

        if unit is None:
            self.unitsuffix = ''
        else:
            self.unitsuffix = ' {}'.format(unit)

    def apply(self, nominal, uncertainty):
        return '(' + \
                self.nominal_rule.apply(nominal) + \
                self.separator + \
                self.uncertainty_rule.apply(uncertainty) + \
                ')' + self.unitsuffix + self.padding


convention_session = upy2.sessions.byprotocol(Convention)

class FixedpointTypesetter(Typesetter):
    def __init__(self,
            stddevs, precision,
            typeset_possign_value=None,
            infinite_precision=None,
            unit=None,
    ):
        Typesetter.__init__(self)

        if typeset_possign_value is None:
            typeset_possign_value = False
        if infinite_precision is None:
            infinite_precision = 11

        self.nominal_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_value)
        self.uncertainty_typesetter = NumberTypesetter(
                ceil=True)

        self.relative_precision = precision
        self.infinite_precision = infinite_precision
        self.stddevs = stddevs

        self.unit = unit

    def typeset_element(self, element, rule):
        nominal = element.nominal
        uncertainty = element.stddev * self.stddevs

        pos_leftmost_digit_nominal = \
                get_position_of_leftmost_digit(nominal)
        pos_leftmost_digit_uncertainty = \
                get_position_of_leftmost_digit(uncertainty)

        if pos_leftmost_digit_uncertainty is not None:
            # Take the precision from the uncertainty and print both
            # figures using it.

            precision = pos_leftmost_digit_uncertainty + \
                    (self.relative_precision - 1)

            typeset_nominal = self.nominal_typesetter.typesetfp(
                    nominal, precision)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                    uncertainty, precision)

        elif pos_leftmost_digit_nominal is not None:
            # There is no counting digit in the *uncertainty*, but
            # there is in *nominal*.
            #
            # Print the nominal value with "infinite" precision,
            # anchored at the leftmost digit in *nominal*, and print
            # just ``0`` for the uncertainty.

            precision = pos_leftmost_digit_nominal + \
                    self.infinite_precision

            typeset_nominal = self.nominal_typesetter.typesetfp(
                    nominal, precision)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                    number=0, precision=0)

        else:
            # None of both numbers exhibits counting digits.

            typeset_nominal = self.nominal_typesetter.typesetfp(
                    number=0, precision=0)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                    number=0, precision=0)

        return rule.apply(
                nominal=typeset_nominal,
                uncertainty=typeset_uncertainty,
        )

    def deduce_rule(self):
        manager = convention_session.current()
        return FixedpointRule(
                separator=manager.get_separator(),
                padding=manager.get_padding(),
                unit=self.unit,
        )
