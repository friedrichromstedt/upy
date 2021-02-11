# Developed since: Sep 2015
#
# Built using 'printable.py', part of upy v0.4.11b, developed since
# February 2010.

import numpy
from upy2.typesetting.numbers import \
    get_position_of_leftmost_digit, \
    NumberTypesetter
from upy2.typesetting.rules import \
    LeftRule, RightRule, CentreRule, TypesetNumberRule
from upy2.typesetting.protocol import Typesetter, Convention
import upy2.sessions


class ScientificRule(object):
    def __init__(self, separator, padding, unit=None):
        """ *separator* is the string separating the nominal value and
        the uncertainty.  *padding* is appended to the complete
        results, following the exponent.

        When *unit* is given, it will be separated from the exponent
        by a space. """

        self.nominal_rule = TypesetNumberRule()
        self.uncertainty_rule = TypesetNumberRule()
        self.exponent_rule = RightRule()

        self.separator = separator
        self.padding = padding

        if unit is None:
            self.unitsuffix = ''
        else:
            self.unitsuffix = ' {}'.format(unit)

    def apply(self, nominal, uncertainty, exponent):
        """ Applies the ``ScientificRule`` to the components of an
        uncertain number in scientific notation.  *nominal* and
        *uncertainty* are :class:`TypesetNumber` instances.
        *exponent* is a plain string. """

        return '(' + \
            self.nominal_rule.apply(nominal) + \
            self.separator + \
            self.uncertainty_rule.apply(uncertainty) + \
            ') 10^' + \
            self.exponent_rule.apply(exponent) + \
            self.unitsuffix + \
            self.padding


convention_session = upy2.sessions.byprotocol(Convention)

class ScientificTypesetter(Typesetter):
    def __init__(self,
        stddevs,
        precision,
        typeset_possign_value=None,
        typeset_possign_exponent=None,
        infinite_precision=None,
        unit=None,
    ):
        """ *unit* is an optional string. """
        Typesetter.__init__(self)

        if typeset_possign_value is None:
            typeset_possign_value = False
        if typeset_possign_exponent is None:
            typeset_possign_exponent = False
        if infinite_precision is None:
            infinite_precision = 11
            # >>> len(str(math.pi))
            # 13
            # >>> len(str(math.pi).split('.')[1])
            # 11
            # ( same holds for numpy.pi )

        self.nominal_typesetter = NumberTypesetter(
            typeset_positive_sign=typeset_possign_value)
        self.uncertainty_typesetter = NumberTypesetter(
            ceil=True)
            # Uncertainties are always positive, hence the sign is
            # never to be printed.
        self.exponent_typesetter = NumberTypesetter(
            typeset_positive_sign=typeset_possign_exponent)

        self.relative_precision = precision
        self.infinite_precision = infinite_precision
        self.stddevs = stddevs

        self.unit = unit
    
    def typeset_element(self, element, rule):
        """ Typesetting results::

        -   (1.2345 +- 0.0067) 10^-5
        -   (1.234567...5678 +- 0) 10^-1
        -   (0 +- 1.2) 10^2
        -   (0 +- 0) 10^0

        based on the *nominal value* and the *stddev* of *element*.
        The *uncertainty* is a multiple of the *stddev* as defined by
        the *stddevs* given at initialisation time.

        When both the nominal value and the uncertainty are != 0, the
        exponent is extracted from the nominal value, and the
        precision is extracted from the uncertainty.

        When the nominal value is != 0, and the uncertainty is
        zero, the exponent is extracted from *nominal*, but the
        uncertainty is printed as "0" plain, while the precision is
        the "infinite precision" handed over on initialisation time.

        When the nominal value is zero, and the uncertainty is not,
        the exponent is extracted from the uncertainty, the
        uncertainty is printed with the precision handed over on
        initialisation time, and the nominal value is printed as "0".

        When both *nominal* as well as *uncertainty* are zero, plain
        zeros "0" are printed for both of them, and the exponent is
        set to 0 as well.
        """

        nominal = element.nominal
        uncertainty = element.stddev * self.stddevs

        pos_leftmost_digit_nominal = \
            get_position_of_leftmost_digit(nominal)
        pos_leftmost_digit_uncertainty = \
            get_position_of_leftmost_digit(uncertainty)

        if pos_leftmost_digit_nominal is not None \
        and pos_leftmost_digit_uncertainty is not None:
            # Both *value* as well as *uncertainty* have counting
            # digits.
            #
            # Print full-featured.

            # For pos = 1, exp = -1, e.g. 0.12 => 1.2 10^-1.
            exponent = -pos_leftmost_digit_nominal
            # Calculate mantissa values.
            # For pos=1, multiply by 10^1.
            mantissa_nominal = nominal * \
                10 ** pos_leftmost_digit_nominal
            mantissa_uncertainty = uncertainty * \
                10 ** pos_leftmost_digit_nominal

            # Extract the precision for both *mantissa_nominal* as
            # well as *mantissa_uncertainty* from the uncertainty.
            mantissa_precision = (pos_leftmost_digit_uncertainty -
                pos_leftmost_digit_nominal + self.relative_precision -
                1)
                # For pos_leftmost_digit_uncertainty ==
                # pos_leftmost_digit_nominal, the precision for
                # printout is (relative_precision - 1), e.g.
                # relative_precision = 2:
                #
                #   (9.0 +- 1.2) 10^-2   (precision = 1)
                #
                # The precision names the last digit printed.
            
            typeset_nominal = self.nominal_typesetter.typesetfp(
                mantissa_nominal, mantissa_precision)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                mantissa_uncertainty, mantissa_precision)
            typeset_exponent = self.exponent_typesetter.typesetint(
                exponent, precision=0)

            return rule.apply(
                nominal=typeset_nominal,
                uncertainty=typeset_uncertainty,
                exponent=typeset_exponent,
            )

        elif pos_leftmost_digit_nominal is not None \
        and pos_leftmost_digit_uncertainty is None:
            # There is no counting digit in *uncertainty*, but there
            # is in *nominal*.
            #
            # Print with "infinite precision".

            exponent = -pos_leftmost_digit_nominal
            mantissa_nominal = nominal * \
                10 ** pos_leftmost_digit_nominal

            mantissa_precision = self.infinite_precision

            typeset_nominal = self.nominal_typesetter.typesetfp(
                mantissa_nominal, mantissa_precision)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                number=0, precision=0)
            typeset_exponent = self.exponent_typesetter.typesetint(
                exponent, precision=0)

            return rule.apply(
                nominal=typeset_nominal,
                uncertainty=typeset_uncertainty,
                exponent=typeset_exponent,
            )

        elif pos_leftmost_digit_nominal is None \
        and pos_leftmost_digit_uncertainty is not None:
            # Only the uncertainty features counting digits; the
            # nominal value does not.
            # 
            # Obtain the exponent and the precision from the
            # uncertainty.

            exponent = -pos_leftmost_digit_uncertainty
            # *mantissa_nominal* is not needed.
            mantissa_uncertainty = uncertainty * \
                10 ** pos_leftmost_digit_uncertainty

            mantissa_precision = (self.relative_precision - 1)
            # The exponent is extracted from the uncertainty, s.t. the
            # precision is fixed to (self.relative_precision - 1).
            # E.g., for relative_precision == 2, two counting digits
            # of the uncertainty shall be printed, which is
            # accomplished by setting the printing precision to 1.
            # The printing precision gives the position of the last
            # printed digit.

            typeset_nominal = self.nominal_typesetter.typesetfp(
                number=0, precision=mantissa_precision)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                mantissa_uncertainty, mantissa_precision)
            typeset_exponent = self.exponent_typesetter.typesetint(
                exponent, precision=0)

            return rule.apply(
                nominal=typeset_nominal,
                uncertainty=typeset_uncertainty,
                exponent=typeset_exponent,
            )

        elif pos_leftmost_digit_nominal is None \
        and pos_leftmost_digit_uncertainty is None:
            # None of both numbers exhibits counting digits.

            # We pass "0" through the typesetters to allow for
            # typesetting of e.g. a positive sign character '+'.
            # Furthermore, it is more clean to use the regular
            # typesetters.
            typeset_nominal = self.nominal_typesetter.typesetfp(
                number=0, precision=0)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                number=0, precision=0)
            typeset_exponent = self.exponent_typesetter.typesetint(
                number=0, precision=0)

            return rule.apply(
                nominal=typeset_nominal,
                uncertainty=typeset_uncertainty,
                exponent=typeset_exponent,
            )

    def deduce_rule(self):
        manager = convention_session.current()
        return ScientificRule(
                separator=manager.get_separator(),
                padding=manager.get_padding(),
                unit=self.unit)
