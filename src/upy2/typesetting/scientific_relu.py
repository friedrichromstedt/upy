# Developed since: December 2021
# Based on work dating back to February 2010

from upy2.typesetting.numbers import \
        get_position_of_leftmost_digit, NumberTypesetter, TypesetNumber
from upy2.typesetting.rules import \
        LeftRule, RightRule, TypesetNumberRule
from upy2.typesetting.protocol import Typesetter, Convention
import upy2.sessions


class ScientificRelativeURule:
    """ Produces aligned representations of a *mantissa* and an *exponent*
    defining the relative uncertainty, e.g. ``1 +- 4.2 10^-2``, and
    produces representations of *infinite* relative uncertainty. """

    def __init__(self, separator, infinity):
        self.separator = separator
        self.infinity = infinity

        self.mantissa_rule = TypesetNumberRule()
        self.exponent_rule = RightRule()
        self.output_rule = LeftRule()

    def apply(self, mantissa, exponent):
        """ *mantissa* is a ``TypesetNumber``, *exponent* is a plain
        string. """

        representation = '1{sep}{mantissa} 10^{exp}'.format(
                sep=self.separator,
                mantissa=self.mantissa_rule.apply(mantissa),
                exp=self.exponent_rule.apply(exponent),
        )
        return self.output_rule.apply(representation)

    def apply_infinity(self):
        infinity = TypesetNumber(left=self.infinity, point='', right='')
        representation = '1{sep}{infinity}'.format(
                sep=self.separator,
                infinity=self.mantissa_rule.apply(infinity),
        )
        return self.output_rule.apply(representation)


convention_session = upy2.sessions.byprotocol(Convention)

class ScientificRelativeUTypesetter(Typesetter):
    def __init__(self, stddevs, precision, typeset_possign_exponent=None):
        Typesetter.__init__(self)

        if typeset_possign_exponent is None:
            typeset_possign_exponent = False

        self.mantissa_typesetter = NumberTypesetter(ceil=True)
        self.exponent_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_exponent)

        self.stddevs = stddevs
        self.mantissa_precision = precision

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
                exponent = -pos_leftmost_digit
                mantissa = relative_uncertainty * 10 ** (-exponent)

                typeset_mantissa = self.mantissa_typesetter.typesetfp(
                    mantissa, precision=(self.mantissa_precision - 1))
                typeset_exponent = self.exponent_typesetter.typesetint(
                    exponent, precision=0)

                return rule.apply(
                        mantissa=typeset_mantissa,
                        exponent=typeset_exponent,
                )

            else:
                # The relative uncertainty is zero.
                typeset_mantissa = self.mantissa_typesetter.typesetfp(
                        number=0, precision=0)
                typeset_exponent = self.exponent_typesetter.typesetint(
                        number=0, precision=0)

                return rule.apply(
                        mantissa=typeset_mantissa,
                        exponent=typeset_exponent,
                )

        elif uncertainty != 0:
            # The nominal value is zero, and the uncertainty is not.
            return rule.apply_infinity()

        else:
            # Both nominal value as well as uncertainty are zero.
            typeset_mantissa = self.mantissa_typesetter.typesetfp(
                    number=0, precision=0)
            typeset_exponent = self.exponent_typesetter.typesetint(
                    number=0, precision=0)

            return rule.apply(
                    mantissa=typeset_mantissa,
                    exponent=typeset_exponent,
            )

    def deduce_rule(self):
        manager = convention_session.current()
        return ScientificRelativeURule(
                separator=manager.get_separator(),
                infinity=manager.get_infinity(),
        )
