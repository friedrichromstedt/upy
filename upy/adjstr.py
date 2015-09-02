class Rule:
    def __init__(self):
        self.width = 0
    
    def report(self, width):
        self.width = max(self.width, width)

    def apply(self, body):
        raise NotImplementedError("Abstract method called.")


class LJustRule(Rule):
    def apply(self, body):
        return body.ljust(self.width)


class RJustRule(Rule):
    def apply(self, body):
        return body.rjust(self.width)


class AdjustableString(str):
    def __init__(self, body, rule=None):
        """ *body* is the string to pad.  The padding rules are given
        by *rule*. """

        self.body = body
        self.rule = rule

    def __add__(self, other):
        return Sum(self, other)

    def __str__(self):
        return "Adjustable String, width = %d" % self.width

    def finalise(self):
        if self.rule is not None:
            return self.rule.apply(self.body)
        return self.body


def asadjstr(adjstr_like):
    if isinstance(adjstr_like, AdjustableString):
        return adjstr_like
    return AdjustableString(adjstr_like)


class Sum(AdjustableString):
    def __init__(self, a, b):
        self.a = asadjstr(a)
        self.b = asadjstr(b)
