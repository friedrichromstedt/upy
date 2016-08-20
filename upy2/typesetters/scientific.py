# Developed since: Sep 2015
#
# Built using 'printable.py', part of upy v0.4.11b, developed since
# February 2010.

import numpy
from upy2.typesetters.numbers import \
    get_position_of_leftmost_digit, \
    NumberTypesetter


class WidthRule(object):
    def __init__(self):
        self.width = 0

    def format(self, string):
        raise NotImplementedError('virtual method called')

    def apply(self, string):
        self.width = max(len(string), self.width)
        return self.format(string)


class LeftRule(WidthRule):
    def format(self, string):
        return string.ljust(self.width)

class RightRule(WidthRule):
    def format(self, string):
        return string.rjust(self.width)

class CentreRule(WidthRule):
    def format(self, string):
        return string.center(self.width)


class TypesetNumberRule(object):
    def __init__(self):
        self.left_rule = RightRule()
        self.point_rule = CentreRule()
        self.right_rule = LeftRule()

    def apply(self, typeset_number):
        left = self.left_rule.apply(typeset_number.left)
        point = self.point_rule.apply(typeset_number.point)
        right = self.right_rule.apply(typeset_number.right)

        return left + point + right

class ScientificRule(object):
    def __init__(self):
        self.nominal_rule = TypesetNumberRule()
        self.uncertainty_rule = TypesetNumberRule()
        self.exponent_rule = RightRule()

    def apply(self, nominal, uncertainty, exponent):
        """ Applies the ``ScientificRule`` to the components of an
        uncertain number in scientific notation.  *nominal* and
        *uncertainty* are :class:`TypesetNumber` instances.
        *exponent* is a plain string. """

        return '(' + \
            self.nominal_rule.apply(nominal) + \
            ' +- ' + \
            self.uncertainty_rule.apply(uncertainty) + \
            ') 10^' + \
            self.exponent_rule.apply(exponent) + \
            ' '


class ScientificElement:
    def __init__(self, 
            nominal, uncertainty,
            typesetter, rule,
    ):
        self.nominal = nominal
        self.uncertainty = uncertainty
        self.typesetter = typesetter
        self.rule = rule

    def __repr__(self):
        result = self.typesetter.typeset_element(
            nominal=self.nominal, uncertainty=self.uncertainty,
            rule=self.rule,
        )
        return result


class ScientificTypesetter:
    def __init__(self,
        stddevs,
        relative_precision,
        typeset_possign_value=None,
        typeset_possign_exponent=None,
        infinite_precision=None,
    ):
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

        self.relative_precision = relative_precision
        self.infinite_precision = infinite_precision
        self.stddevs = stddevs
    
    def typeset_element(self, nominal, uncertainty, rule):
        """ Typesetting results::

        -   (1.2345 +- 0.0067) 10^-5
        -   (1.234567...5678 +- 0) 10^-1
        -   (0 +- 1.2) 10^2
        -   (0 +- 0) 10^0

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
            mantissa_uncertainty = uncertainty * \
                10 ** pos_leftmost_digit_nominal

            mantissa_precision = self.infinite_precision

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

        elif pos_leftmost_digit_nominal is None \
        and pos_leftmost_digit_uncertainty is not None:
            # Only the uncertainty features counting digits; the
            # nominal value does not.
            # 
            # Obtain the exponent and the precision from the
            # uncertainty.

            exponent = -pos_leftmost_digit_uncertainty
            # mantissa_nominal  is not needed.
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
                number=0, precision=0)
            typeset_uncertainty = self.uncertainty_typesetter.typesetfp(
                mantissa_uncertainty, mantissa_precision)
            typeset_exponent = self.exponent_typesetter.typesetint(
                exponent, precision=0)

            return rule.apply(
                nominal=typset_nominal,
                uncertainty=typset_uncertainty,
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
            typeset_exponent = self.exponent_typsetter.typesetint(
                number=0, precision=0)

            return rule.apply(
                nominal=typeset_nominal,
                uncertainty=typeset_uncertainty,
                exponent=typeset_exponent,
            )

    def typeset(self, uarray):
        """ Typeset ``undarray`` instance *uarray* using the options
        handed over on initialisation time. """

        nominal = uarray.nominal.flatten()
        uncertainty = self.stddevs * uarray.stddev.flatten()
        N = len(nominal)

        scientific_rule = ScientificRule()

        scientific_elements = numpy.zeros(N, dtype=numpy.object)
        for index in xrange(0, N):
            scientific_elements[index] = ScientificElement(
                nominal=nominal[index],
                uncertainty=uncertainty[index],
                typesetter=self,
                rule=scientific_rule,
            )

        ready = scientific_elements.reshape(uarray.shape)
        str(ready); return str(ready)