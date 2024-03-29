import unittest

from typesetting import \
    Test_TypesettingNumbers, Test_TypesettingRules, \
    Test_TypesettingScientific, Test_TypesettingEngineering, \
    Test_TypesettingFixedpoint, \
    Test_TypesettingScientificRelativeU, \
    Test_TypesettingFixedpointRelativeU, \
    Test_Convention
from operators import TestOperators
from dependency import Test_Dependency
from core import Test_Core, Test_undarray
from sessions import Test_Sessions


unittest.main()
