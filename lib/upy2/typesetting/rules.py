# Developed since: August 2015

""" The Rules provided in this file provide a means to format strings
in such a way, that certain formatting rules are obeyed. """


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
    """ This rule can be applied to instances of
    :class:`upy2.typsetting.numbers.TypesetNumber`. """

    def __init__(self):
        self.left_rule = RightRule()
        self.point_rule = CentreRule()
        self.right_rule = LeftRule()

    def apply(self, typeset_number):
        """ *typeset_number* is an instance of
        :class:`upy2.typesetting.numbers.TypesetNumber`. """

        left = self.left_rule.apply(typeset_number.left)
        point = self.point_rule.apply(typeset_number.point)
        right = self.right_rule.apply(typeset_number.right)

        return left + point + right
