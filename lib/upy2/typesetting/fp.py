# Developed since: Feb 2021

from upy2.typesetting.numbers import \
        get_position_of_leftmost_digit, NumberTypesetter
from upy2.typesetting.rules import TypesetNumberRule
from upy2.typesetting.protocol import Typesetter


class FpRule(object):
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
