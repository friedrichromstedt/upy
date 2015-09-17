# Developed since: Sep 2015

from upy.typesetters.adjstr import RuleLeft, RuleRight, RuleCentre, \
    AdjustableString
from upy.typesetters.typesetter import DecimalTypesetter
from upy.typesetters.analysis import \
    get_position_of_leftmost_digit


class ScientificRule:
    def __init__(self):
        self.nominal_before = RuleRight()
        self.nominal_point = RuleCentre()
        self.nominal_after = RuleLeft()

        self.uncertainty_before = RuleRight()
        self.uncertainty_point = RuleCentre()
        self.uncertainty_after = RuleLeft()

        self.exponent = RuleRight()

    def apply(self, nominal, uncertainty, exponent): 
        """ Returns an ``AdjustableString`` instance from
        ``TypesetNumber`` instances *nominal*, *uncertainty*, and
        a string *exponent*."""

        return '(' + \
            AdjustableString(nominal.left, self.nominal_before) + \
            AdjustableString(nominal.point, self.nominal_point) + \
            AdjustableString(nominal.right, self.nominal_after) + \
            ' +- ' + \
            AdjustableString(uncertainty.left, self.uncertainty_before + \
            AdjustableString(uncertainty.point, self.uncertainty_point + \
            AdjustableString(uncertainty.right, self.uncertainty_after + \
            ') 10^' + \
            AdjustableString(exponent, self.exponent)


class ScientificElement:
    def __init__(self, 
            nominal, uncertainty,
            typesetter,
    ):
        self.nominal = nominal
        self.uncertainty = uncertainty
        self.typesetter = typesetter

    def __repr__(self):
        return self.typesetter.typeset_element(
            nominal=self.nominal, uncertainty=self.uncertainty,
            rule=self.rule,
        )


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
        if inifinite_precision is None:
            infinite_precision = 25

        self.value_typesetter = DecimalTypesetter(
            typset_positive_sign=typeset_possign_value)
        self.uncertainty_typesetter = DecimalTypesetter()

        self.relative_precision = relative_precision
        self.infinite_precision = infinite_precision
        self.stddevs = stddevs
    
    def typeset_element(self, nominal, uncertainty, rule):
        pos_leftmost_digit_nominal = \
            get_position_of_leftmost_digit(nominal)
        pos_leftmost_digit_uncertainty = \
            get_position_of_leftmost_digit(uncertainty)

        # Determine the exponent and relative precision to use ...

        if pos_leftmost_digit_nominal is not None:
            exponent = -pos_leftmost_digit_nominal
            relative_precision = self.relative_precision
        else:
            # pos_leftmost_digit_nominal is None
            if pos_leftmost_digit_uncertainty is not None:
                exponent = -pos_leftmost_digit_uncertainty
            else:
                exponent = 0
