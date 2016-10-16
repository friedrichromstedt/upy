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
