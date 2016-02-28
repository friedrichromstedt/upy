# Developed since: Sep 2015

import unittest
from upy.typesetters.numbers import get_position_of_leftmost_digit
from upy.typesetters.numbers import NumberTypesetter

from upy.typesetters.adjstr import AdjustableString as Adjstr
from upy.typesetters.adjstr import NoRule, LeftRule, RightRule, CentreRule

from upy.typesetters.scientific import \
    ScientificRule, ScientificElement, ScientificTypesetter


#####################################


class TestTypesettersScientific(unittest.TestCase):
    """ TestCase for :mod:`upy.typesetters.scientific`. """

    def test_ScientificRule(self):
        rule = ScientificRule()
        ts = NumberTypesetter()

        nom1, unc1, exp1 = ts.typeset(1.00, 2), ts.typeset(0.10, 2), '1'
        nom2, unc2, exp2 = ts.typeset(1.000, 3), ts.typeset(0.010, 3), '-1'
        nom3, unc3, exp3 = ts.typeset(1.00, 2), ts.typeset(0.10, 2), '12'
        nom4, unc4, exp4 = ts.typeset(1, 0), ts.typeset(10, 0), '1'
        nom5, unc5, exp5 = ts.typeset(1, -1), ts.typeset(100, -1), '1'

        s1 = rule.apply(nom1, unc1, exp1)
        s2 = rule.apply(nom2, unc2, exp2)
        s3 = rule.apply(nom3, unc3, exp3)
        s4 = rule.apply(nom4, unc4, exp4)
        s5 = rule.apply(nom5, unc5, exp5)

        self.assertEqual(s1.adjust(), '( 1.00  +-   0.10 ) 10^ 1')
        self.assertEqual(s2.adjust(), '( 1.000 +-   0.010) 10^-1')
        self.assertEqual(s3.adjust(), '( 1.00  +-   0.10 ) 10^12')
        self.assertEqual(s4.adjust(), '( 1     +-  10    ) 10^ 1')
        self.assertEqual(s5.adjust(), '(00     +- 100    ) 10^ 1')
    
    def test_ScientificTypesetter(self):
        sts = ScientificTypesetter(
            stddevs=2,
            relative_precision=2,
        )
        rule = ScientificRule()

        el1 = ScientificElement(10, 1, sts, rule)
        el2 = ScientificElement(100, 1, sts, rule)
        el3 = ScientificElement(100, 10, sts, rule)
        el4 = ScientificElement(10, 100, sts, rule)
        el5 = ScientificElement(10, 1000, sts, rule)

        self.assertEqual(str(el1).adjust(), '( 1.00  +-  0.10 ) 10^1')


#######################################


class TestTypesettersNumbers(unittest.TestCase):
    """ Test suite for module ``upy.typesetters.numbers``. """

    def test_get_position_of_leftmost_digit(self):
        """ Tests
        upy.typesetters.numbers.get_position_of_leftmost_digit(). """

        self.assertIsNone(get_position_of_leftmost_digit(0))
        self.assertEqual(get_position_of_leftmost_digit(1), 0)
        self.assertEqual(get_position_of_leftmost_digit(10), -1)
        self.assertEqual(get_position_of_leftmost_digit(0.1), 1)

    def setUp(self):
        
        self.without_possign_nonceiling = NumberTypesetter(
            typeset_positive_sign=False,
            ceil=False,
        )
        self.with_possign_nonceiling = NumberTypesetter(
            typeset_positive_sign=True,
            ceil=False,
        )
        self.without_possign_ceiling = NumberTypesetter(
            typeset_positive_sign=False,
            ceil=True,
        )
        self.with_possign_ceiling = NumberTypesetter(
            typeset_positive_sign=True,
            ceil=True,
        )

    def test_possign(self):
        
        plus_wo = self.without_possign_nonceiling.typeset(42, 0)
        minus_wo = self.without_possign_nonceiling.typeset(-42, 0)
        
        plus_w = self.with_possign_nonceiling.typeset(42, 0)
        minus_w = self.with_possign_nonceiling.typeset(-42, 0)

        self.assertEqual(plus_wo.left, '42')
        self.assertEqual(minus_wo.left, '-42')
        self.assertEqual(plus_w.left, '+42')
        self.assertEqual(minus_w.left, '-42')

    def test_nonceiling(self):
        
        plus_prec0 = self.without_possign_nonceiling.typeset(12.34, 0)
        plus_prec1 = self.without_possign_nonceiling.typeset(12.34, 1)
        plus_precm1 = self.without_possign_nonceiling.typeset(12.34, -1)

        minus_prec0 = self.without_possign_nonceiling.typeset(-12.34, 0)
        minus_prec1 = self.without_possign_nonceiling.typeset(-12.34, 1)
        minus_precm1 = self.without_possign_nonceiling.typeset(-12.34, -1)

        self.assertEqual(str(plus_prec0), '12')
        self.assertEqual(str(plus_prec1), '12.3')
        self.assertEqual(str(plus_precm1), '10')

        self.assertEqual(str(minus_prec0), '-12')
        self.assertEqual(str(minus_prec1), '-12.3')
        self.assertEqual(str(minus_precm1), '-10')

    def test_ceiling(self):
        
        plus_prec0 = self.without_possign_ceiling.typeset(12.34, 0)
        plus_prec2 = self.without_possign_ceiling.typeset(12.34, 2)

        self.assertEqual(str(plus_prec0), '13')
        self.assertEqual(str(plus_prec2), '12.34')

    def test_possign(self):
        
        plus_prec0 = self.with_possign_nonceiling.typeset(12.34, 0)
        self.assertEqual(str(plus_prec0), '+12')

    def test_prec_cornercase(self):

        nonceiling_precm2 = self.without_possign_nonceiling.typeset(12.34, -2)
        self.assertEqual(str(nonceiling_precm2), '000')

        ceiling_precm2 = self.without_possign_ceiling.typeset(12.34, -2)
        self.assertEqual(str(ceiling_precm2), '100')


####################################


class TestTypesettersAdjstr(unittest.TestCase):
    """ Test case for module ``unittest.typesetters.adjstr``. """
    
    def test_NoRule(self):

        norule = NoRule()

        hello = Adjstr('hello', norule)
        foobar = Adjstr('foobar', norule)

        self.assertEqual(hello.adjust(), 'hello')
        self.assertEqual(foobar.adjust(), 'foobar')

    def test_LeftRule(self):
        
        rule = LeftRule()

        hi = Adjstr('hi', rule)
        foobar = Adjstr('foobar', rule)

        self.assertEqual(hi.adjust(), 'hi    ')
        self.assertEqual(foobar.adjust(), 'foobar')

    def test_RightRule(self):
        
        rule = RightRule()

        hi = Adjstr('hi', rule)
        foobar = Adjstr('foobar', rule)
        
        self.assertEqual(hi.adjust(), '    hi')
        self.assertEqual(foobar.adjust(), 'foobar')

    def test_CentreRule(self):
        
        rule = CentreRule()

        hi = Adjstr('hi', rule)
        foobar = Adjstr('foobar', rule)
        hellworld = Adjstr('hello world', rule)

        self.assertEqual(hi.adjust(),
            '     hi    ')
        self.assertEqual(foobar.adjust(),
            '   foobar  ')
        self.assertEqual(hellworld.adjust(),
            'hello world')

    def test_concatenation(self):
        
        left = LeftRule()
        right = RightRule()
        
        left1 = Adjstr('1234', right)
        left2 = Adjstr('0', right)
        right1 = Adjstr('56', left)
        right2 = Adjstr('abc', left)

        s1 = left1 + '.' + right1
        s2 = left2 + 'x' + right2

        self.assertEqual(s1.adjust(),
            '1234.56 ')
        self.assertEqual(s2.adjust(),
            '   0xabc')

        # This test also proves 'upy.typesetters.adjstr.asadjstr()'.


######################################


if __name__ == '__main__':
    unittest.main()
