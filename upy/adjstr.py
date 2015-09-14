# Developed since: Aug 2015

class NoRule:
    def examine(self, string):
        pass

    def apply(self, string):
        return string


class WidthRule(NoRule):
    def __init__(self):
        NoRule.__init__(self)
        self.width = 0

    def examine(self, string):
        self.width = max(len(string), self.width)


class RuleLeft(WidthRule):
    def apply(self, string):
        return string.ljust(self.width)


class RuleRight(WidthRule):
    def apply(self, string):
        return string.rjust(self.width)


class RuleCentre(WidthRule):
    def apply(self, string):
        return string.center(self.width)


# crufted 11 Sep 2015
#
#X class Rule:
#X     def __init__(self):
#X         self.width = 0
#X     
#X     def report(self, width):
#X         self.width = max(self.width, width)
#X 
#X     def apply(self, body):
#X         raise NotImplementedError("Abstract method called.")
#X 
#X 
#X class LJustRule(Rule):
#X     def apply(self, body):
#X         return body.ljust(self.width)
#X 
#X 
#X class RJustRule(Rule):
#X     def apply(self, body):
#X         return body.rjust(self.width)


class AdjustableString(str):
    def __init__(self, body, rule):
        """ *body* is the string to pad.  The padding rules are given
        by *rule*. """

        self.body = body
        self.rule = rule
        self.rule.examine(self.body)

    def __add__(self, other):
        return Sum(self, other)

    def __radd__(self, other):
        return Sum(other, self)
    
    def finalise(self):
        return self.rule.apply(self.body)


def asadjstr(adjstr_like):
    if isinstance(adjstr_like, AdjustableString):
        return adjstr_like
    return AdjustableString(body=adjstr_like, rule=NoRule())


class Sum(AdjustableString):
    def __init__(self, a, b):
        self.a = asadjstr(a)
        self.b = asadjstr(b)

    def finalise(self):
        return self.a.finalise() + self.b.finalise()
