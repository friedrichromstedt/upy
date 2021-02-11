# Developed since: Feb 2021

from upy2.typesetting.numbers import \
        get_position_of_leftmost_digit, NumberTypesetter
from upy2.typesetting.rules import LeftRule, RightRule, TypesetNumberRule
from upy2.typesetting.protocol import Typesetter, Convention
import upy2.sessions


class EngineeringRule(object):
    def __init__(self, separator, padding):
        self.nominal_rule = TypesetNumberRule()
        self.uncertainty_rule = TypesetNumberRule()

        self.base_rule = LeftRule()
        self.exponent_rule = RightRule()
        self.unit_rule = RightRule()

        self.separator = separator
        self.padding = padding

    def apply(self, nominal, uncertainty, exponent=None, unit=None):
        """ *nominal* and *uncertainty* are instances of
        :class:`TypesetNumber`.  *exponent* and *unit*, if given, are
        strings. """

        if exponent is not None:
            typeset_power = self.base_rule.apply(' 10^') + \
                    self.exponent_rule.apply(exponent)
        else:
            typeset_power = self.base_rule.apply('') + \
                    self.exponent_rule.apply('')

        if unit is not None:
            typeset_unit = self.unit_rule.apply(' ' + unit)
        else:
            typeset_unit = self.unit_rule.apply('')

        typeset_nominal = self.nominal_rule.apply(nominal)
        typeset_uncertainty = self.uncertainty_rule.apply(uncertainty)

        return '(' + typeset_nominal + \
                self.separator + \
                typeset_uncertainty + ')' + \
                typeset_power + typeset_unit + \
                self.padding


convention_session = upy2.sessions.byprotocol(Convention)

class EngineeringTypesetter(Typesetter):
    def __init__(self,
            stddevs, precision,
            typeset_possign_value=None,
            typeset_possign_exponent=None,
            infinite_precision=None,
            unit=None, useprefixes=None,
    ):
        """ When provided with a *unit*, the ``EngineeringTypesetter``
        can be instructed to use *prefixes* to it instead of numerical
        powers of 10 by providing *useprefixes* as ``True``.  Without
        given a *unit*, *useprefixes* is ignored.  Powers which cannot
        be expressed by a prefix will always be put as powers of ten.
        """
        Typesetter.__init__(self)

        if typeset_possign_value is None:
            typeset_possign_value = False
        if typeset_possign_exponent is None:
            typeset_possign_exponent = False
        if infinite_precision is None:
            infinite_precision = 11
        if useprefixes is None:
            useprefixes = False

        self.nominal_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_value)
        self.uncertainty_typesetter = NumberTypesetter(ceil=True)
        self.exponent_typesetter = NumberTypesetter(
                typeset_positive_sign=typeset_possign_exponent)

        self.relative_precision = precision
        self.infinite_precision = infinite_precision
        self.stddevs = stddevs

        self.unit = unit
        self.useprefixes = useprefixes

    def typeset_element(self, element, rule):
        nominal = element.nominal
        uncertainty = element.stddev * self.stddevs

        pos_leftmost_digit_nominal = \
                get_position_of_leftmost_digit(nominal)
        pos_leftmost_digit_uncertainty = \
                get_position_of_leftmost_digit(uncertainty)

        if pos_leftmost_digit_nominal is not None \
        and pos_leftmost_digit_uncertainty is not None:
            # Both *nominal* as well as *uncertainty* have counting
            # digits.
            #
            # Take the exponent from the nominal value and the
            # precision from the uncertainty.

            exponent = 3 * (-pos_leftmost_digit_nominal // 3)
                # pos = 1 => exponent = -3, e.g. 0.12 => 120 10^-3
                # pos = -1 => exponent = 0, e.g. 12.3 => 12.3 10^0
            mantissa_nominal = nominal * 10 ** -exponent
            mantissa_uncertainty = uncertainty * 10 ** -exponent

            mantissa_precision = \
                    (pos_leftmost_digit_uncertainty + exponent) + \
                    (self.relative_precision - 1)
                # *pos_leftmost_digit_uncertainty + exponent* names
                # the position of the leftmost digit in
                # *mantissa_uncertainty*: with a large *exponent*, the
                # factor ``10 ** -exponent`` in ``uncertainty * 10 **
                # -exponent`` shifts the position of the leftmost
                # digit *to the right*.  *relative_precision - 1* is
                # the shift to maintain the requested precision.  The
                # result is the position of the last digit printed.

            typeset_nominal = self.nominal_typesetter.typesetfp(
                    mantissa_nominal, mantissa_precision)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                    mantissa_uncertainty, mantissa_precision)
            typeset_exponent = self.exponent_typesetter.typesetint(
                    exponent, precision=0)

        elif pos_leftmost_digit_nominal is not None \
        and pos_leftmost_digit_uncertainty is None:
            # There is no counting digit in the *uncertainty*, but
            # there is in *nominal*.
            #
            # Print with "infinite precision"

            exponent = 3 * (-pos_leftmost_digit_nominal // 3)
            mantissa_nominal = nominal * 10 ** -exponent
            # *mantissa_uncertainty* isn't needed.

            mantissa_precision = \
                    (pos_leftmost_digit_nominal + exponent) + \
                    self.infinite_precision

            typeset_nominal = self.nominal_typesetter.typesetfp(
                    mantissa_nominal, mantissa_precision)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                    number=0, precision=0)
            typeset_exponent = self.exponent_typesetter.typesetint(
                    exponent, precision=0)

        elif pos_leftmost_digit_nominal is None \
        and pos_leftmost_digit_uncertainty is not None:
            # Only the uncertainty features counting digits; the nominal
            # value does not.
            # 
            # Obtain the exponent and the precision from the uncertainty.

            exponent = 3 * (-pos_leftmost_digit_uncertainty // 3)
            # *mantissa_nominal* is not needed.
            mantissa_uncertainty = uncertainty * 10 ** -exponent

            mantissa_precision = \
                    (pos_leftmost_digit_uncertainty + exponent) + \
                    (self.relative_precision - 1)

            typeset_nominal = self.nominal_typesetter.typesetfp(
                    number=0, precision=mantissa_precision)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                    mantissa_uncertainty, mantissa_precision)
            typeset_exponent = self.exponent_typesetter.typesetint(
                    exponent, precision=0)

        elif pos_leftmost_digit_nominal is None \
        and pos_leftmost_digit_uncertainty is None:
            # None of both numbers exhibits counting digits.

            exponent = 0

            typeset_nominal = self.nominal_typesetter.typesetfp(
                    number=0, precision=0)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                    number=0, precision=0)
            typeset_exponent = self.exponent_typesetter.typesetint(
                    number=0, precision=0)

        if self.unit is not None and self.useprefixes \
                and -24 <= exponent <= 24:
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
                    nominal=typeset_nominal,
                    uncertainty=typeset_uncertainty,
                    unit=(prefix + self.unit),
            )
        elif self.unit is not None:
            # Append the unit as-is.

            return rule.apply(
                    nominal=typeset_nominal,
                    uncertainty=typeset_uncertainty,
                    exponent=typeset_exponent,
                    unit=self.unit,
            )
        else:
            # Do not append a unit.

            return rule.apply(
                    nominal=typeset_nominal,
                    uncertainty=typeset_uncertainty,
                    exponent=typeset_exponent,
            )

    def deduce_rule(self):
        manager = convention_session.current()
        return EngineeringRule(
                separator=manager.get_separator(),
                padding=manager.get_padding(),
        )
