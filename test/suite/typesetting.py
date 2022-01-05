# Developed since: Sep 2015

import unittest
import numpy
from upy2.typesetting.numbers import get_position_of_leftmost_digit
from upy2.typesetting.numbers import NumberTypesetter, TypesetNumber
from upy2.typesetting.protocol import ElementTypesetter, Convention
from upy2.typesetting.rules import \
    LeftRule, RightRule, CentreRule, TypesetNumberRule
from upy2.typesetting.scientific import \
    ScientificRule, ScientificTypesetter
from upy2.typesetting.engineering import \
    EngineeringRule, EngineeringTypesetter
from upy2.typesetting.fixedpoint import \
    FixedpointRule, FixedpointTypesetter
from upy2.typesetting.scientific_relu import \
    ScientificRelativeURule, ScientificRelativeUTypesetter
from upy2.typesetting.fixedpoint_relu import \
    FixedpointRelativeURule, FixedpointRelativeUTypesetter
from upy2.typesetting.scientific_rel import \
    RelativeScientificTypesetter
from upy2.typesetting.fixedpoint_rel import \
    RelativeFixedpointTypesetter
from upy2.typesetting.engineering_rel import \
    RelativeEngineeringTypesetter
from upy2 import u, U, undarray


class Test_TypesettingNumbers(unittest.TestCase):
    """ Test suite for :mod:`upy2.typesetting.numbers`. """

    def test_get_position_of_leftmost_digit(self):
        """ Tests
        upy2.typesetters.numbers.get_position_of_leftmost_digit(). """

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

    def test_convention(self):
        ts = NumberTypesetter()

        with Convention(negative='_'):
            self.assertEqual(str(ts.typesetfp(-1, 0)), '_1')


class Test_TypesettingRules(unittest.TestCase):
    """ TestCase for :mod:`upy2.typesetting.rules`. """

    def test_LeftRule(self):
        rule = LeftRule()

        str1 = rule.apply('123')
        str2 = rule.apply('1234')
        str1b = rule.apply('123')

        self.assertEqual(str1, '123')
        self.assertEqual(str2, '1234')
        self.assertEqual(str1b, '123 ')
    
    def test_RightRule(self):
        rule = RightRule()

        str1 = rule.apply('123')
        str2 = rule.apply('12345')
        str1b = rule.apply('123')

        self.assertEqual(str1, '123')
        self.assertEqual(str2, '12345')
        self.assertEqual(str1b, '  123')

    def test_CentreRule(self):
        rule = CentreRule()

        str1 = rule.apply('123')
        str2 = rule.apply('12345')
        str1b = rule.apply('123')
        str3 = rule.apply('1234')

        self.assertEqual(str1, '123')
        self.assertEqual(str2, '12345')
        self.assertEqual(str1b, ' 123 ')
        self.assertEqual(str3, ' 1234')

    def test1_TypesetNumberRule(self):
        ts = NumberTypesetter()  # nonceiling, w/o possign
        rule = TypesetNumberRule()

        n1 = ts.typesetfp(1.1, 1)
        n2 = ts.typesetfp(3.45, 2)
        n3 = ts.typesetfp(-4.2, 1)

        self.assertEqual(str(n1), '1.1')
        self.assertEqual(str(n2), '3.45')
        self.assertEqual(str(n3), '-4.2')

        ruled1 = rule.apply(n1)
        self.assertEqual(ruled1, '1.1')

        ruled2 = rule.apply(n2)
        self.assertEqual(ruled2, '3.45')

        ruled3 = rule.apply(n3)
        self.assertEqual(ruled3, '-4.2 ')

        # Reapply to *n1*:
        ruled4 = rule.apply(n1)
        self.assertEqual(ruled4, ' 1.1 ')

        n4 = ts.typesetfp(100, 0)

        ruled5 = rule.apply(n4)
        self.assertEqual(ruled5, '100   ')

        ruled6 = rule.apply(n3)
        self.assertEqual(ruled6, ' -4.2 ')

    def test2_TypesetNumberRule(self):
        ts = NumberTypesetter()
        rule = TypesetNumberRule()

        n1 = ts.typesetfp(1, 0)
        n2 = ts.typesetfp(11, 0)
        n3 = ts.typesetfp(12.3, 1)

        self.assertEqual(str(n1), '1')
        self.assertEqual(str(n2), '11')
        self.assertEqual(str(n3), '12.3')

        ruled1 = rule.apply(n1)
        self.assertEqual(ruled1, '1')

        ruled2 = rule.apply(n2)
        self.assertEqual(ruled2, '11')

        ruled3 = rule.apply(n3)
        self.assertEqual(ruled3, '12.3')

        ruled4 = rule.apply(n1)
        self.assertEqual(ruled4, ' 1  ')


class Test_TypesettingScientific(unittest.TestCase):
    """ TestCase for :mod:`upy2.typesetting.scientific`. """

    def test_ScientificRule(self):
        rule = ScientificRule(separator=' +- ', padding=' ')
        ts = NumberTypesetter()

        nom1, unc1, exp1 = ts.typesetfp(1.00, 2), ts.typesetfp(0.10, 2), '1'
        nom2, unc2, exp2 = ts.typesetfp(1.000, 3), ts.typesetfp(0.010, 3), '-1'
        nom3, unc3, exp3 = ts.typesetfp(1.00, 2), ts.typesetfp(0.10, 2), '12'
        nom4, unc4, exp4 = ts.typesetfp(1, 0), ts.typesetfp(10, 0), '1'
        nom5, unc5, exp5 = ts.typesetfp(1, -1), ts.typesetfp(100, -1), '1'

        rule.apply(nom1, unc1, exp1)
        rule.apply(nom2, unc2, exp2)
        rule.apply(nom3, unc3, exp3)
        rule.apply(nom4, unc4, exp4)
        rule.apply(nom5, unc5, exp5)

        s1 = rule.apply(nom1, unc1, exp1)
        s2 = rule.apply(nom2, unc2, exp2)
        s3 = rule.apply(nom3, unc3, exp3)
        s4 = rule.apply(nom4, unc4, exp4)
        s5 = rule.apply(nom5, unc5, exp5)

        self.assertEqual(s1, '( 1.00  +-   0.10 ) 10^ 1 ')
        self.assertEqual(s2, '( 1.000 +-   0.010) 10^-1 ')
        self.assertEqual(s3, '( 1.00  +-   0.10 ) 10^12 ')
        self.assertEqual(s4, '( 1     +-  10    ) 10^ 1 ')
        self.assertEqual(s5, '(00     +- 100    ) 10^ 1 ')

    def test2_ScientificRule(self):
        rule = ScientificRule(separator=' +- ', padding='', unit='N')
        ts = NumberTypesetter()

        nom1, unc1, exp1 = ts.typesetfp(1.00, 2), ts.typesetfp(0.10, 2), '1'
        nom2, unc2, exp2 = ts.typesetfp(1.000, 3), ts.typesetfp(0.010, 3), '-1'

        rule.apply(nom1, unc1, exp1)
        rule.apply(nom2, unc2, exp2)

        s1 = rule.apply(nom1, unc1, exp1)
        s2 = rule.apply(nom2, unc2, exp2)

        self.assertEqual(s1, '(1.00  +- 0.10 ) 10^ 1 N')
        self.assertEqual(s2, '(1.000 +- 0.010) 10^-1 N')
    
    def test_ScientificTypesetter(self):
        sts = ScientificTypesetter(
            stddevs=2,
            precision=2,
        )
        rule = ScientificRule(separator=' +- ', padding=' ')

        with U(2):
            el1 = ElementTypesetter(10 +- u(1), sts, rule)
            el2 = ElementTypesetter(100 +- u(1), sts, rule)
            el3 = ElementTypesetter(100 +- u(10), sts, rule)
            el4 = ElementTypesetter(10 +- u(100), sts, rule)
            el5 = ElementTypesetter(10 +- u(1000), sts, rule)

        str(el1); str(el2); str(el3); str(el4); str(el5)

        self.assertEqual(str(el1), '( 1.00  +-   0.10 ) 10^1 ')
        self.assertEqual(str(el2), '( 1.000 +-   0.010) 10^2 ')
        self.assertEqual(str(el3), '( 1.00  +-   0.10 ) 10^2 ')
        self.assertEqual(str(el4), '( 1     +-  10    ) 10^1 ')
        self.assertEqual(str(el5), '(00     +- 100    ) 10^1 ')

        # Test typesetting non-scalar undarrays:

        with U(2), sts:
            a = numpy.asarray([[1, 2], [42, 10]])
            stddev = numpy.asarray([[0.1, 0.1], [10, 1]]) / 2
            ua = a +- u(2 * stddev)
            self.assertEqual(str(ua),
                    '[[(1.00 +- 0.10) 10^0  (2.00 +- 0.10) 10^0 ]\n'
                    ' [(4.2  +- 1.0 ) 10^1  (1.00 +- 0.10) 10^1 ]]'
            )  # ua.nominal is laid out in C order.

            b = numpy.asarray([[1, 42], [2, 10]]).T
                # .T will swap the strides.
            self.assertEqual(str(b),
                    '[[ 1  2]\n'
                    ' [42 10]]')
            ub = undarray(
                    nominal=b.astype(float),
                        # .astype preserves the strides.
                    stddev=stddev,
            )
            self.assertEqual(str(ub),
                    '[[(1.00 +- 0.10) 10^0  (2.00 +- 0.10) 10^0 ]\n'
                    ' [(4.2  +- 1.0 ) 10^1  (1.00 +- 0.10) 10^1 ]]'
            )  # ub.nominal is laid out in F order.

            # I do not verify the swapped strides of ub.nominal w.r.t.
            # ua.nominal since these figures depend on the number of
            # bytes per element, which can vary with architecture.

        # Test behaviour of *sts* with:
        #
        #   1.  Zero uncertainty;
        #   2.  zero nominal value;
        #   3.  both zero uncertainty as well as zero nominal value.

        with U(2), sts:
            # Test with zero uncertainty:
            ua1 = numpy.pi +- u(0)
            ua2 = numpy.pi / 10 +- u(0)
            ua3 = numpy.pi * 10 +- u(0)

            self.assertEqual(str(ua1),
                    '(3.14159265359 +- 0) 10^0 ')
            self.assertEqual(str(ua2),
                    '(3.14159265359 +- 0) 10^-1 ')
            self.assertEqual(str(ua3),
                    '(3.14159265359 +- 0) 10^1 ')

            # Test with zero nominal value:
            ub1 = 0 +- u(numpy.pi)
            ub2 = 0 +- u(numpy.pi / 10)
            ub3 = 0 +- u(numpy.pi * 10)

            self.assertEqual(str(ub1),
                    '(0.0 +- 3.2) 10^0 ')
            self.assertEqual(str(ub2),
                    '(0.0 +- 3.2) 10^-1 ')
            self.assertEqual(str(ub3),
                    '(0.0 +- 3.2) 10^1 ')

            # Test overall zero:
            uc1 = u(0)

            self.assertEqual(str(uc1),
                    '(0 +- 0) 10^0 ')

    def test2_ScientificTypesetter(self):
        sts = ScientificTypesetter(stddevs=2, precision=2, unit='N')

        with U(2), sts:
            self.assertEqual(str(42 +- u(0.5)),
                    '(4.200 +- 0.050) 10^1 N ')

    def test3_ScientificTypesetter(self):
        sts = ScientificTypesetter(stddevs=2, precision=2,
                typeset_possign_value=True,
                typeset_possign_exponent=True)

        with U(2), sts:
            self.assertEqual(str(42 +- u(0.5)), '(+4.200 +- 0.050) 10^+1 ')

    def test_Convention(self):
        sts = ScientificTypesetter(stddevs=2, precision=2)
        with U(2), sts, Convention(separator=' _ '):
            self.assertEqual(str(42 +- u(0.5)), '(4.200 _ 0.050) 10^1 ')
        with U(2), sts, Convention(plusminus='__', padding='_'):
            self.assertEqual(str(42 +- u(0.5)), '(4.200 __ 0.050) 10^1_')


class Test_TypesettingEngineering(unittest.TestCase):
    """ TestCase for :mod:`upy2.typesetting.engineering. """

    def test_EngineeringRule(self):
        ts = NumberTypesetter()

        nom1, unc1, exp1, u1 = ts.typesetfp(1.00, 2), ts.typesetfp(0.10, 2), '1', None
        nom2, unc2, exp2, u2 = ts.typesetfp(1.000, 3), ts.typesetfp(0.010, 3), None, 'm'
        nom3, unc3, exp3, u3 = ts.typesetfp(1.00, 2), ts.typesetfp(0.10, 2), None, 'mm'
        nom4, unc4, exp4, u4 = ts.typesetfp(1, 0), ts.typesetfp(10, 0), '3', 'm'
        nom5, unc5, exp5, u5 = ts.typesetfp(1, -1), ts.typesetfp(100, -1), '-3', None

        ruleA = EngineeringRule(separator=' +- ', padding=' ')
        ruleA.apply(nom1, unc1, exp1, u1)
        ruleA.apply(nom2, unc2, exp2, u2)

        self.assertEqual(ruleA.apply(nom1, unc1, exp1, u1), '(1.00  +- 0.10 ) 10^1   ')
        self.assertEqual(ruleA.apply(nom2, unc2, exp2, u2), '(1.000 +- 0.010)      m ')

        ruleB = EngineeringRule(separator=' +- ', padding='_')
        ruleB.apply(nom2, unc2, exp2, u2)
        ruleB.apply(nom3, unc3, exp3, u3)

        self.assertEqual(ruleB.apply(nom2, unc2, exp2, u2), '(1.000 +- 0.010)  m_')
        self.assertEqual(ruleB.apply(nom3, unc3, exp3, u3), '(1.00  +- 0.10 ) mm_')

        ruleC = EngineeringRule(separator=' +- ', padding='')
        ruleC.apply(nom3, unc3, exp3, u3)
        ruleC.apply(nom4, unc4, exp4, u4)

        self.assertEqual(ruleC.apply(nom3, unc3, exp3, u3), '(1.00 +-  0.10)      mm')
        self.assertEqual(ruleC.apply(nom4, unc4, exp4, u4), '(1    +- 10   ) 10^3  m')

        ruleD = EngineeringRule(separator=' +- ', padding='')
        ruleD.apply(nom1, unc1, exp1, u1)
        ruleD.apply(nom5, unc5, exp5, u5)

        self.assertEqual(ruleD.apply(nom1, unc1, exp1, u1), '( 1.00 +-   0.10) 10^ 1')
        self.assertEqual(ruleD.apply(nom5, unc5, exp5, u5), '(00    +- 100   ) 10^-3')

    def test1_EngineeringTypesetter(self):
        """ Test the EngineeringTypesetter, first with plain numbers,
        and then with *useprefixes* and a *unit*. """

        # Numbers with a finite binary representation: powers of 2.
        #
        # 16, 8, 4, 2, 1, 0.5, 0.25, 0.125, 0.0625
        # However it still happens that the error isn't binary-rational and is rounded up.

        with EngineeringTypesetter(stddevs=2, precision=2), \
                Convention(padding=''), U(2):
            self.assertEqual(str((1 +- u(0.25)) * 1e27), '(1.00 +- 0.25) 10^27')
            self.assertEqual(str((4 +- u(0.25)) * 1e24), '(4.00 +- 0.25) 10^24')
            self.assertEqual(str((0.0625 +- u(16)) * 1e24), '(0000 +- 16000) 10^21')
                # 1e21 (62.5 +- 16000) = 1e21 (0000 +- 16000)
            self.assertEqual(str((0.0625 +- u(1)) * 1e21), '(100 +- 1100) 10^18')
                # 1e18 (62.5 +- 1000) = 1e18 (100 +- 1000)
            self.assertEqual(str((0.0625 +- u(4)) * 1e18), '(100 +- 4100) 10^15')
            self.assertEqual(str((1 +- u(4)) * 1e12), '(1.0 +- 4.0) 10^12')
            self.assertEqual(str((0.25 +- u(4)) * 1e12), '(300 +- 4100) 10^9')
            self.assertEqual(str((2 +- u(0.5)) * 1e6), '(2.00 +- 0.50) 10^6')
            self.assertEqual(str((0.125 +- u(0.0625)) * 1e6), '(125 +- 63) 10^3')
            self.assertEqual(str((0.125 +- u(2)) * 1e3), '(100 +- 2000) 10^0')
            self.assertEqual(str((0.0625 +- u(0.5)) * 1e0), '(60 +- 500) 10^-3')
            self.assertEqual(str((1 +- u(1)) * 1e-6), '(1.0 +- 1.0) 10^-6')
            self.assertEqual(str((4 +- u(0.25)) * 1e-9), '(4.00 +- 0.25) 10^-9')
            self.assertEqual(str((2 +- u(8)) * 1e-12), '(2.0 +- 8.0) 10^-12')
            self.assertEqual(str((16 +- u(0.25)) * 1e-15), '(16.00 +- 0.25) 10^-15')
            self.assertEqual(str((0.0625 +- u(0.25)) * 1e-15), '(60 +- 260) 10^-18')
            self.assertEqual(str((0.0625 +- u(0.125)) * 1e-18), '(60 +- 130) 10^-21')
            self.assertEqual(str((0.0625 +- u(8)) * 1e-21), '(100 +- 8000) 10^-24')
            self.assertEqual(str((1 +- u(0.25)) * 1e-27), '(1.00 +- 0.25) 10^-27')

        with EngineeringTypesetter(stddevs=2, precision=2,
                unit='m', useprefixes=True), Convention(padding=''), U(2):
            self.assertEqual(str((1 +- u(0.25)) * 1e27), '(1.00 +- 0.25) 10^27 m')
            self.assertEqual(str((4 +- u(0.25)) * 1e24), '(4.00 +- 0.25) Ym')
            self.assertEqual(str((0.0625 +- u(16)) * 1e24), '(0000 +- 16000) Zm')
                # 1e21 (62.5 +- 16000) = 1e21 (0000 +- 16000)
            self.assertEqual(str((0.0625 +- u(1)) * 1e21), '(100 +- 1100) Em')
                # 1e18 (62.5 +- 1000) = 1e18 (100 +- 1000)
            self.assertEqual(str((0.0625 +- u(4)) * 1e18), '(100 +- 4100) Pm')
            self.assertEqual(str((1 +- u(4)) * 1e12), '(1.0 +- 4.0) Tm')
            self.assertEqual(str((0.25 +- u(4)) * 1e12), '(300 +- 4100) Gm')
            self.assertEqual(str((2 +- u(0.5)) * 1e6), '(2.00 +- 0.50) Mm')
            self.assertEqual(str((0.125 +- u(0.0625)) * 1e6), '(125 +- 63) km')
            self.assertEqual(str((0.125 +- u(2)) * 1e3), '(100 +- 2000) m')
            self.assertEqual(str((0.0625 +- u(0.5)) * 1e0), '(60 +- 500) mm')
            self.assertEqual(str((1 +- u(1)) * 1e-6), '(1.0 +- 1.0) um')
            self.assertEqual(str((4 +- u(0.25)) * 1e-9), '(4.00 +- 0.25) nm')
            self.assertEqual(str((2 +- u(8)) * 1e-12), '(2.0 +- 8.0) pm')
            self.assertEqual(str((16 +- u(0.25)) * 1e-15), '(16.00 +- 0.25) fm')
            self.assertEqual(str((0.0625 +- u(0.25)) * 1e-15), '(60 +- 260) am')
            self.assertEqual(str((0.0625 +- u(0.125)) * 1e-18), '(60 +- 130) zm')
            self.assertEqual(str((0.0625 +- u(8)) * 1e-21), '(100 +- 8000) ym')
            self.assertEqual(str((1 +- u(0.25)) * 1e-27), '(1.00 +- 0.25) 10^-27 m')

        with EngineeringTypesetter(stddevs=2, precision=2,
                typeset_possign_value=True,
                typeset_possign_exponent=True), U(2):
            self.assertEqual(str(10 +- u(0.10)), '(+10.00 +- 0.10) 10^+0 ')

        with EngineeringTypesetter(stddevs=2, precision=2, unit='N',
                useprefixes=True), U(2):
            self.assertEqual(str(0.100 +- u(0)), '(100.000000000 +- 0) mN ')
            self.assertEqual(str(0 +- u(0.5)), '(00 +- 500) mN ')
            self.assertEqual(str(0 +- u(0.05)), '(0 +- 50) mN ')
            self.assertEqual(str(0 +- u(0.005)), '(0.0 +- 5.0) mN ')
            self.assertEqual(str(0 +- u(0)), '(0 +- 0) N ')

    def test_Convention(self):
        with EngineeringTypesetter(stddevs=2, precision=2), U(2), \
                Convention(plusminus='+/-', padding='_', negative='_'):
            self.assertEqual(str(-42 +- u(0.5)), '(_42.00 +/- 0.50) 10^0_')


class Test_TypesettingFixedpoint(unittest.TestCase):
    """ TestCase for :mod:`upy2.typesetting.fixedpoint`. """

    def test_FixedpointRule(self):
        ts = NumberTypesetter()
        nom1, unc1 = ts.typesetfp(1.00, 2), ts.typesetfp(0.10, 2)
        nom2, unc2 = ts.typesetfp(100, 0), ts.typesetfp(1, 0)

        ruleA = FixedpointRule(separator=' +- ', padding=' ')
        ruleA.apply(nom1, unc1)
        ruleA.apply(nom2, unc2)

        self.assertEqual(ruleA.apply(nom1, unc1), '(  1.00 +- 0.10) ')
        self.assertEqual(ruleA.apply(nom2, unc2), '(100    +- 1   ) ')

        ruleB = FixedpointRule(separator=' +- ', padding='_', unit='N')
        ruleB.apply(nom1, unc1)
        ruleB.apply(nom2, unc2)

        self.assertEqual(ruleB.apply(nom1, unc1), '(  1.00 +- 0.10) N_')
        self.assertEqual(ruleB.apply(nom2, unc2), '(100    +- 1   ) N_')

    def test_FixedpointTypesetter(self):
        with FixedpointTypesetter(stddevs=2, precision=2), U(2):
            self.assertEqual(str(42 +- u(1)), '(42.0 +- 1.0) ')
            self.assertEqual(str(1 +- u(42)), '(1 +- 42) ')
            self.assertEqual(str(1 +- u(100)), '(00 +- 100) ')

            self.assertEqual(str(1 +- u(0)), '(1.00000000000 +- 0) ')
            self.assertEqual(str(0 +- u(0.5)), '(0.00 +- 0.50) ')
            self.assertEqual(str(0 +- u(0)), '(0 +- 0) ')

        with FixedpointTypesetter(stddevs=2, precision=2,
                typeset_possign_value=True), U(2):
            self.assertEqual(str(4 +- u(0.5)), '(+4.00 +- 0.50) ')

    def test_convention(self):
        with FixedpointTypesetter(stddevs=2, precision=2, unit='N'), \
                U(2), Convention(separator='+-', padding='__'):
            self.assertEqual(str(4 +- u(0.5)), '(4.00+-0.50) N__')

        with FixedpointTypesetter(stddevs=2, precision=2), U(2), \
                Convention(plusminus='+/-'):
            self.assertEqual(str(4 +- u(0.5)), '(4.00 +/- 0.50) ')


class Test_TypesettingScientificRelativeU(unittest.TestCase):
    """ Tests relative uncertainty tyesetting using scientific notation for
    the relative uncertainty: The typesetting of the uncertainty alone and
    all "full" relative typesetters, using the scientific relative
    uncertainty typesetter. """

    def test_ScientificRelativeURule(self):
        rule = ScientificRelativeURule(separator=' +- ', infinity='oo')
        man1, exp1 = TypesetNumber(left='4', point='.', right='2'), '-2'
        man2, exp2 = TypesetNumber(left='100', point='', right=''), '1'

        rule.apply(man1, exp1)
        rule.apply(man2, exp2)
        rule.apply_infinity()

        self.assertEqual(rule.apply(man1, exp1), '1 +-   4.2 10^-2')
        self.assertEqual(rule.apply(man2, exp2), '1 +- 100   10^ 1')
        self.assertEqual(rule.apply_infinity(),  '1 +-  oo        ')

    def test_ScientificRelativeUTypesetter(self):
        ts = ScientificRelativeUTypesetter(stddevs=2, precision=2)
        with U(2):
            ar = numpy.asarray([1.0, 10.0, -5.0, 0.0, 1.0]) +- \
                             u([0.1,  0.1,  5.0, 1.0, 0.0])

        result = ts.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), "1 +-  1.0 10^-1")
        self.assertEqual(str(result[1]), "1 +-  1.0 10^-2")
        self.assertEqual(str(result[2]), "1 +-  1.0 10^ 0")
        self.assertEqual(str(result[3]), "1 +- oo        ")
        self.assertEqual(str(result[4]), "1 +-  0   10^ 0")

        with U(2), ts:
            self.assertEqual(
                    str(1e12 +- u(1e11)),
                    "1 +- 1.0 10^-1")
            self.assertEqual(
                    str(1e23 +- u(1e22)),
                    "1 +- 1.0 10^-1")
            self.assertEqual(
                    str(1 +- u(0.10001)),
                    "1 +- 1.1 10^-1")

    @unittest.expectedFailure
    def test_ScientificRelativeUTypesetter_largevalue(self):
        ts = ScientificRelativeUTypesetter(stddevs=2, precision=2)
        with U(2), ts:
            self.assertEqual(
                    str(1e23 +- u(1e22)),
                    "1 +- 1.0 10^-1")  # succeeds
            self.assertEqual(
                    str(1e24 +- u(1e23)),
                    "1 +- 1.0 10^-1")  # found: "1 +- 10.0 10^-2"
            # >>> 1e23 / 1e24
            # 0.09999999999999999
            # >>> 1e22 / 1e23
            # 0.1

    def test_RelativeScientificTypesetter(self):
        """ Tests :class:`ScientificRelativeUTypesetter` with
        :class:`RelativeScientificTypesetter`. """

        uts1 = ScientificRelativeUTypesetter(stddevs=2, precision=2)
        ts1 = RelativeScientificTypesetter(precision=2, utypesetter=uts1)

        with U(2):
            ar = numpy.asarray([1.0, 10.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,  0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts1.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), " 1.0 10^ 0 (1 +-  1.0 10^-1)")
        self.assertEqual(str(result[1]), " 1.0 10^ 1 (1 +-  1.0 10^-2)")
        self.assertEqual(str(result[2]), "-5.0 10^-1 (1 +-  1.0 10^ 0)")
        self.assertEqual(str(result[3]), " 0   10^ 0 (1 +- oo        )")
        self.assertEqual(str(result[4]), " 1.0 10^ 0 (1 +-  0   10^ 0)")

        with Convention(padding='', infinity='inf'), ts1:
            self.assertEqual(str(ar[3]), "0 10^0 (1 +- inf)")


        uts2 = ScientificRelativeUTypesetter(stddevs=2, precision=2,
                typeset_possign_exponent=True)
        ts2 = RelativeScientificTypesetter(precision=2, utypesetter=uts2,
                typeset_possign_value=True, typeset_possign_exponent=True)

        with U(2):
            ar = numpy.asarray([1.0, -10.0, 0.5, 0.0]) +- \
                             u([0.1,   0.1, 0.5, 1.0])

        with Convention(padding=''):
            result = ts2.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), "+1.0 10^+0 (1 +-  1.0 10^-1)")
        self.assertEqual(str(result[1]), "-1.0 10^+1 (1 +-  1.0 10^-2)")
        self.assertEqual(str(result[2]), "+5.0 10^-1 (1 +-  1.0 10^+0)")
        self.assertEqual(str(result[3]), "+0   10^+0 (1 +- oo        )")


        ts3 = RelativeScientificTypesetter(precision=2, utypesetter=uts1,
                unit='N')

        with U(2):
            ar = numpy.asarray([1.0, 10.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,  0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts3.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), " 1.0 10^ 0 (1 +-  1.0 10^-1) N")
        self.assertEqual(str(result[1]), " 1.0 10^ 1 (1 +-  1.0 10^-2) N")
        self.assertEqual(str(result[2]), "-5.0 10^-1 (1 +-  1.0 10^ 0) N")
        self.assertEqual(str(result[3]), " 0   10^ 0 (1 +- oo        ) N")
        self.assertEqual(str(result[4]), " 1.0 10^ 0 (1 +-  0   10^ 0) N")

    def test_RelativeFixedpointTypesetter(self):
        """ Tests :class:`ScientificRelativeUTypesetter` with
        :class:`RelativeFixedpointTypesetter`. """

        uts1 = ScientificRelativeUTypesetter(stddevs=2, precision=2)
        ts1 = RelativeFixedpointTypesetter(precision=2, utypesetter=uts1)

        with U(2):
            ar = numpy.asarray([1.0, 10.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,  0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts1.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), " 1.0  (1 +-  1.0 10^-1)")
        self.assertEqual(str(result[1]), "10    (1 +-  1.0 10^-2)")
        self.assertEqual(str(result[2]), "-0.50 (1 +-  1.0 10^ 0)")
        self.assertEqual(str(result[3]), " 0    (1 +- oo        )")
        self.assertEqual(str(result[4]), " 1.0  (1 +-  0   10^ 0)")


        ts2 = RelativeFixedpointTypesetter(precision=2, utypesetter=uts1,
                typeset_possign_value=True)

        with U(2):
            ar = numpy.asarray([1.0, -10.0, 0.5, 0.0]) +- \
                             u([0.1,   0.1, 0.5, 1.0])

        with Convention(padding=''):
            result = ts2.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), " +1.0  (1 +-  1.0 10^-1)")
        self.assertEqual(str(result[1]), "-10    (1 +-  1.0 10^-2)")
        self.assertEqual(str(result[2]), " +0.50 (1 +-  1.0 10^ 0)")
        self.assertEqual(str(result[3]), " +0    (1 +- oo        )")

        
        ts3 = RelativeFixedpointTypesetter(precision=2, utypesetter=uts1,
                unit='N')

        with U(2):
            ar = numpy.asarray([1.0, 10.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,  0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts3.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), " 1.0  (1 +-  1.0 10^-1) N")
        self.assertEqual(str(result[1]), "10    (1 +-  1.0 10^-2) N")
        self.assertEqual(str(result[2]), "-0.50 (1 +-  1.0 10^ 0) N")
        self.assertEqual(str(result[3]), " 0    (1 +- oo        ) N")
        self.assertEqual(str(result[4]), " 1.0  (1 +-  0   10^ 0) N")

    def test_RelativeEngineeringTypesetter(self):
        """ Tests :class:`ScientificRelativeUTypesetter` with
        :class:`RelativeEngineeringTypesetter. """

        uts = ScientificRelativeUTypesetter(stddevs=2, precision=2)
        ts1 = RelativeEngineeringTypesetter(precision=2, utypesetter=uts)

        with U(2):
            ar = numpy.asarray([1.0, 1000.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,    0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts1.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), "   1.0 10^ 0 (1 +-  1.0 10^-1)")
        self.assertEqual(str(result[1]), "   1.0 10^ 3 (1 +-  1.0 10^-4)")
        self.assertEqual(str(result[2]), "-500   10^-3 (1 +-  1.0 10^ 0)")
        self.assertEqual(str(result[3]), "   0   10^ 0 (1 +- oo        )")
        self.assertEqual(str(result[4]), "   1.0 10^ 0 (1 +-  0   10^ 0)")


        ts2 = RelativeEngineeringTypesetter(precision=2, utypesetter=uts,
                typeset_possign_value=True, typeset_possign_exponent=True)

        with U(2):
            ar = numpy.asarray([1.0, -10000.0, 0.5, 0.0]) +- \
                             u([0.1,      0.1, 0.5, 1.0])

        with Convention(padding=''):
            result = ts2.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), "  +1.0 10^+0 (1 +-  1.0 10^-1)")
        self.assertEqual(str(result[1]), " -10   10^+3 (1 +-  1.0 10^-5)")
        self.assertEqual(str(result[2]), "+500   10^-3 (1 +-  1.0 10^ 0)")
        self.assertEqual(str(result[3]), "  +0   10^+0 (1 +- oo        )")


        ts3 = RelativeEngineeringTypesetter(precision=2, utypesetter=uts,
                unit='N', useprefixes=True)

        with U(2):
            ar = numpy.asarray([1.0, 1000.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,    0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts3.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), "   1.0 (1 +-  1.0 10^-1)  N")
        self.assertEqual(str(result[1]), "   1.0 (1 +-  1.0 10^-4) kN")
        self.assertEqual(str(result[2]), "-500   (1 +-  1.0 10^ 0) mN")
        self.assertEqual(str(result[3]), "   0   (1 +- oo        )  N")
        self.assertEqual(str(result[4]), "   1.0 (1 +-  0   10^ 0)  N")

        with U(2), Convention(padding=''), ts3:
            self.assertEqual(
                    str(100 +- u(10)),
                    "100 (1 +- 1.0 10^-1) N")
            self.assertEqual(
                    str(1e12 +- u(1e11)),
                    "1.0 (1 +- 1.0 10^-1) TN")
            self.assertEqual(
                    str(1e30 +- u(2e29)),
                    "1.0 10^30 (1 +- 2.0 10^-1) N")
                    # about why to use ``2e29`` instead of ``1e29`` see
                    # :meth:`test_ScientificRelativeUTypesetter_largevalue`
                    # above.
            self.assertEqual(
                    str(1e-30 +- u(1e-31)),
                    "1.0 10^-30 (1 +- 1.0 10^-1) N")


        ts4 = RelativeEngineeringTypesetter(precision=2, utypesetter=uts,
                unit='N')

        with U(2):
            ar = numpy.asarray([1.0, 1000.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,    0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts4.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), "   1.0 10^ 0 (1 +-  1.0 10^-1) N")
        self.assertEqual(str(result[1]), "   1.0 10^ 3 (1 +-  1.0 10^-4) N")
        self.assertEqual(str(result[2]), "-500   10^-3 (1 +-  1.0 10^ 0) N")
        self.assertEqual(str(result[3]), "   0   10^ 0 (1 +- oo        ) N")
        self.assertEqual(str(result[4]), "   1.0 10^ 0 (1 +-  0   10^ 0) N")


        ts5 = RelativeEngineeringTypesetter(precision=2, utypesetter=uts,
                useprefixes=True)

        with U(2), Convention(padding=''), ts5:
            self.assertEqual(
                str(1.0 +- u(0.1)),
                "1.0 10^0 (1 +- 1.0 10^-1)")


class Test_TypesettingFixedpointRelativeU(unittest.TestCase):
    def test_FixedpointRelativeURule(self):
        rule = FixedpointRelativeURule(separator=' +- ', infinity='oo')
        unc1 = TypesetNumber(left='4', point='.', right='2')
        unc2 = TypesetNumber(left='100', point='', right='')

        rule.apply(unc1)
        rule.apply(unc2)
        rule.apply_infinity()

        self.assertEqual(rule.apply(unc1), '1 +-   4.2')
        self.assertEqual(rule.apply(unc2), '1 +- 100  ')
        self.assertEqual(rule.apply_infinity(), '1 +-  oo  ')

    def test_FixedpointRelativeUTypesetter(self):
        ts = FixedpointRelativeUTypesetter(stddevs=2, precision=2)
        with U(2):
            ar = numpy.asarray([1.0, 10.0, -5.0, 0.0, 1.0]) +- \
                             u([0.1,  0.1,  5.0, 1.0, 0.0])

        result = ts.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), "1 +-  0.10 ")
        self.assertEqual(str(result[1]), "1 +-  0.010")
        self.assertEqual(str(result[2]), "1 +-  1.0  ")
        self.assertEqual(str(result[3]), "1 +- oo    ")
        self.assertEqual(str(result[4]), "1 +-  0    ")

        with U(2), ts:
            self.assertEqual(
                    str(1 +- u(0.100001)),
                    "1 +- 0.11")

    def test_RelativeScientificTypesetter(self):
        """ Tests :class:`FixedpointRelativeUTypesetter` with
        :class:`RelativeScientificTypsetter`. """

        uts = FixedpointRelativeUTypesetter(stddevs=2, precision=2)
        ts = RelativeScientificTypesetter(precision=2, utypesetter=uts)

        with U(2):
            ar = numpy.asarray([1.0, 10.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,  0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), " 1.0 10^ 0 (1 +-  0.10 )")
        self.assertEqual(str(result[1]), " 1.0 10^ 1 (1 +-  0.010)")
        self.assertEqual(str(result[2]), "-5.0 10^-1 (1 +-  1.0  )")
        self.assertEqual(str(result[3]), " 0   10^ 0 (1 +- oo    )")
        self.assertEqual(str(result[4]), " 1.0 10^ 0 (1 +-  0    )")

    def test_RelativeFixedpointTypesetter(self):
        """ Tests :class:`FixedpointRelativeUTypesetter` with
        :class:`RelativeFixedpointTypesetter`. """

        uts = FixedpointRelativeUTypesetter(stddevs=2, precision=2)
        ts = RelativeFixedpointTypesetter(precision=2, utypesetter=uts)

        with U(2):
            ar = numpy.asarray([1.0, 10.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,  0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), " 1.0  (1 +-  0.10 )")
        self.assertEqual(str(result[1]), "10    (1 +-  0.010)")
        self.assertEqual(str(result[2]), "-0.50 (1 +-  1.0  )")
        self.assertEqual(str(result[3]), " 0    (1 +- oo    )")
        self.assertEqual(str(result[4]), " 1.0  (1 +-  0    )")

    def test_RelativeEngineeringTypesetter(self):
        """ Tests :class:`FixedpointRelativeUTypesetter` with
        :class:`RelativeEngineeringTypesetter`. """

        uts = FixedpointRelativeUTypesetter(stddevs=2, precision=2)
        ts = RelativeEngineeringTypesetter(precision=2, utypesetter=uts)

        with U(2):
            ar = numpy.asarray([1.0, 10.0, -0.5, 0.0, 1.0]) +- \
                             u([0.1,  0.1,  0.5, 1.0, 0.0])

        with Convention(padding=''):
            result = ts.element_typesetters(ar); str(result)
        self.assertEqual(str(result[0]), "   1.0 10^ 0 (1 +-  0.10 )")
        self.assertEqual(str(result[1]), "  10   10^ 0 (1 +-  0.010)")
        self.assertEqual(str(result[2]), "-500   10^-3 (1 +-  1.0  )")
        self.assertEqual(str(result[3]), "   0   10^ 0 (1 +- oo    )")
        self.assertEqual(str(result[4]), "   1.0 10^ 0 (1 +-  0    )")
