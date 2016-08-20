# Developed since: Sep 2015

import unittest
from upy2.typesetters.numbers import get_position_of_leftmost_digit
from upy2.typesetters.numbers import NumberTypesetter
from upy2.typesetters.scientific import \
    ScientificRule, ScientificElement, ScientificTypesetter


class Test_TypesettersNumbers(unittest.TestCase):
    """ Test suite for module ``upy.typesetters.numbers``. """

    # Test for :func:`get_position_of_leftmost_digit`.

    def test_get_position_of_leftmost_digit(self):
        """ Tests
        upy.typesetters.numbers.get_position_of_leftmost_digit(). """

        self.assertIsNone(get_position_of_leftmost_digit(0))

        self.assertEqual(get_position_of_leftmost_digit(1), 0)
        self.assertEqual(get_position_of_leftmost_digit(10), -1)
        self.assertEqual(get_position_of_leftmost_digit(0.1), 1)

        self.assertEqual(get_position_of_leftmost_digit(-1), 0)
        self.assertEqual(get_position_of_leftmost_digit(-10), -1)
        self.assertEqual(get_position_of_leftmost_digit(-0.1), 1)

    def test_woplus_nonceiling(self):
        ts = NumberTypesetter(
            typeset_positive_sign=False,
            ceil=False,
        )
        
        # typesetfp tests ...

        # positive
        self.assertEqual(str(ts.typesetfp(18.37, 3)), '18.370')
        self.assertEqual(str(ts.typesetfp(18.37, 1)), '18.4')
        self.assertEqual(str(ts.typesetfp(18.37, 0)), '18')
        self.assertEqual(str(ts.typesetfp(18.37, -1)), '20')
        self.assertEqual(str(ts.typesetfp(18.37, -2)), '000')
        self.assertEqual(str(ts.typesetfp(90, -2)), '100')

        # negative
        self.assertEqual(str(ts.typesetfp(-18.37, 3)), '-18.370')
        self.assertEqual(str(ts.typesetfp(-18.37, 1)), '-18.4')
        self.assertEqual(str(ts.typesetfp(-18.37, 0)), '-18')
        self.assertEqual(str(ts.typesetfp(-18.37, -1)), '-20')
        self.assertEqual(str(ts.typesetfp(-18.37, -2)), '-000')
        self.assertEqual(str(ts.typesetfp(-90, -2)), '-100')

        # typesetint tests ...

        # integer
        self.assertEqual(str(ts.typesetint(42, 0)), '42')
        self.assertEqual(str(ts.typesetint(-42, 0)), '-42')

        # positive fp
        with self.assertRaises(ValueError):
            ts.typesetint(18.37, 1)
        self.assertEqual(str(ts.typesetint(18.37, 0)), '18')
        self.assertEqual(str(ts.typesetint(18.37, -1)), '20')
        self.assertEqual(str(ts.typesetint(18.37, -2)), '000')
        self.assertEqual(str(ts.typesetint(90, -2)), '100')

        # negative fp
        with self.assertRaises(ValueError):
            ts.typesetint(-18.37, 1)
        self.assertEqual(str(ts.typesetint(-18.37, 0)), '-18')
        self.assertEqual(str(ts.typesetint(-18.37, -1)), '-20')
        self.assertEqual(str(ts.typesetint(-18.37, -2)), '-000')
        self.assertEqual(str(ts.typesetint(-90, -2)), '-100')

    def test_woplus_ceiling(self):
        ts = NumberTypesetter(
            typeset_positive_sign=False,
            ceil=True,
        )

        # typesetfp tests ...

        # positive
        self.assertEqual(str(ts.typesetfp(18.37, 3)), '18.370')
        self.assertEqual(str(ts.typesetfp(18.37, 1)), '18.4')
        self.assertEqual(str(ts.typesetfp(18.37, 0)), '19')
        self.assertEqual(str(ts.typesetfp(18.37, -1)), '20')
        self.assertEqual(str(ts.typesetfp(18.37, -2)), '100')
        self.assertEqual(str(ts.typesetfp(90, -2)), '100')

        # negative
        self.assertEqual(str(ts.typesetfp(-18.37, 3)), '-18.370')
        self.assertEqual(str(ts.typesetfp(-18.37, 1)), '-18.4')
        self.assertEqual(str(ts.typesetfp(-18.37, 0)), '-19')
        self.assertEqual(str(ts.typesetfp(-18.37, -1)), '-20')
        self.assertEqual(str(ts.typesetfp(-18.37, -2)), '-100')
        self.assertEqual(str(ts.typesetfp(-90, -2)), '-100')

        # typesetint tests ...

        # integer
        self.assertEqual(str(ts.typesetint(42, 0)), '42')
        self.assertEqual(str(ts.typesetint(-42, 0)), '-42')

        # positive fp
        with self.assertRaises(ValueError):
            ts.typesetint(18.37, 1)
        self.assertEqual(str(ts.typesetint(18.37, 0)), '19')
        self.assertEqual(str(ts.typesetint(18.37, -1)), '20')
        self.assertEqual(str(ts.typesetint(18.37, -2)), '100')
        self.assertEqual(str(ts.typesetint(90, -2)), '100')

        # negative fp
        with self.assertRaises(ValueError):
            ts.typesetint(-18.37, 1)
        self.assertEqual(str(ts.typesetint(-18.37, 0)), '-19')
        self.assertEqual(str(ts.typesetint(-18.37, -1)), '-20')
        self.assertEqual(str(ts.typesetint(-18.37, -2)), '-100')
        self.assertEqual(str(ts.typesetint(-90, -2)), '-100')

    def test_wplus_nonceiling(self):
        ts = NumberTypesetter(
            typeset_positive_sign=True,
            ceil=False,
        )

        # typesetfp tests ...

        # positive
        self.assertEqual(str(ts.typesetfp(18.37, 3)), '+18.370')
        self.assertEqual(str(ts.typesetfp(18.37, 1)), '+18.4')
        self.assertEqual(str(ts.typesetfp(18.37, 0)), '+18')
        self.assertEqual(str(ts.typesetfp(18.37, -1)), '+20')
        self.assertEqual(str(ts.typesetfp(18.37, -2)), '+000')
        self.assertEqual(str(ts.typesetfp(90, -2)), '+100')

        # negative
        self.assertEqual(str(ts.typesetfp(-18.37, 3)), '-18.370')
        self.assertEqual(str(ts.typesetfp(-18.37, 1)), '-18.4')
        self.assertEqual(str(ts.typesetfp(-18.37, 0)), '-18')
        self.assertEqual(str(ts.typesetfp(-18.37, -1)), '-20')
        self.assertEqual(str(ts.typesetfp(-18.37, -2)), '-000')
        self.assertEqual(str(ts.typesetfp(-90, -2)), '-100')

        # typesetint tests ...

        # integer
        self.assertEqual(str(ts.typesetint(42, 0)), '+42')
        self.assertEqual(str(ts.typesetint(-42, 0)), '-42')

        # positive fp
        with self.assertRaises(ValueError):
            ts.typesetint(18.37, 1)
        self.assertEqual(str(ts.typesetint(18.37, 0)), '+18')
        self.assertEqual(str(ts.typesetint(18.37, -1)), '+20')
        self.assertEqual(str(ts.typesetint(18.37, -2)), '+000')
        self.assertEqual(str(ts.typesetint(90, -2)), '+100')

        # ngative fp
        with self.assertRaises(ValueError):
            ts.typesetint(-18.37, 1)
        self.assertEqual(str(ts.typesetint(-18.37, 0)), '-18')
        self.assertEqual(str(ts.typesetint(-18.37, -1)), '-20')
        self.assertEqual(str(ts.typesetint(-18.37, -2)), '-000')
        self.assertEqual(str(ts.typesetint(-90, -2)), '-100')

    def test_wplus_ceiling(self):
        ts = NumberTypesetter(
            typeset_positive_sign=True,
            ceil=True,
        )

        # typesetfp tests ...

        # positive
        self.assertEqual(str(ts.typesetfp(18.37, 3)), '+18.370')
        self.assertEqual(str(ts.typesetfp(18.37, 1)), '+18.4')
        self.assertEqual(str(ts.typesetfp(18.37, 0)), '+19')
        self.assertEqual(str(ts.typesetfp(18.37, -1)), '+20')
        self.assertEqual(str(ts.typesetfp(18.37, -2)), '+100')
        self.assertEqual(str(ts.typesetfp(90, -2)), '+100')

        # negative
        self.assertEqual(str(ts.typesetfp(-18.37, 3)), '-18.370')
        self.assertEqual(str(ts.typesetfp(-18.37, 1)), '-18.4')
        self.assertEqual(str(ts.typesetfp(-18.37, 0)), '-19')
        self.assertEqual(str(ts.typesetfp(-18.37, -1)), '-20')
        self.assertEqual(str(ts.typesetfp(-18.37, -2)), '-100')
        self.assertEqual(str(ts.typesetfp(-90, -2)), '-100')

        # typesetint tests ...

        # positive fp
        with self.assertRaises(ValueError):
            ts.typesetint(18.37, 1)
        self.assertEqual(str(ts.typesetint(18.37, 0)), '+19')
        self.assertEqual(str(ts.typesetint(18.37, -1)), '+20')
        self.assertEqual(str(ts.typesetint(18.37, -2)), '+100')
        self.assertEqual(str(ts.typesetint(90, -2)), '+100')

        # negatve fp
        with self.assertRaises(ValueError):
            ts.typesetint(-18.37, 1)
        self.assertEqual(str(ts.typesetint(-18.37, 0)), '-19')
        self.assertEqual(str(ts.typesetint(-18.37, -1)), '-20')
        self.assertEqual(str(ts.typesetint(-18.37, -2)), '-100')
        self.assertEqual(str(ts.typesetint(-90, -2)), '-100')


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


if __name__ == '__main__':
    unittest.main()
