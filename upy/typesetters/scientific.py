# Developed since: Sep 2015

from upy.adjstr import RuleLeft, RuleRight, RuleCentre


class ScientificCoordinator:
    def __init__(self):
        self.nominal_before = RuleRight()
        self.nominal_point = RuleCentre()
        self.nominal_after = RuleLeft()

        self.uncertainty_before = RuleRight()
        self.uncertainty_point = RuleCentre()
        self.uncertainty_after = RuleLeft()

        self.exponent = RuleRight()


class ScientificElement:
    def __init__(self, 
            nominal, uncertainty,
    ):
        self.nominal = nominal
        self.uncertainty = uncertainty
