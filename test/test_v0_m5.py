# Developed since: Sep 2015

import unittest
from upy.typesetters.numbers import get_position_of_leftmost_digit


class TestTypsettersNumbers(unittest.TestCase):
    """ Test suite for upy.typesetters.numbers. """

    def test_get_position_of_leftmost_digit(self):
        """ Tests
        upy.typesetters.numbers.get_position_of_leftmost_digit(). """

        self.assert_(get_position_of_leftmost_digit(0) is None)
        self.assert_(get_position_of_leftmost_digit(1) == 0)
        self.assert_(get_position_of_leftmost_digit(10) == -1)
        self.assert_(get_position_of_leftmost_digit(0.1) == 1)


if __name__ == '__main__':
    unittest.main()
