# Developed since: Jan 2010

from upy2.id_generator import IDGenerator
from upy2.core import *  # The core module provides *__all__*.
from upy2.typesetting.scientific import ScientificTypesetter
from upy2.typesetting.engineering import EngineeringTypesetter
from upy2.typesetting.fixedpoint import FixedpointTypesetter
from upy2.typesetting.scientific_relu import ScientificRelativeUTypesetter
from upy2.typesetting.fixedpoint_relu import FixedpointRelativeUTypesetter
from upy2.typesetting.scientific_rel import RelativeScientificTypesetter
from upy2.typesetting.engineering_rel import RelativeEngineeringTypesetter
from upy2.typesetting.fixedpoint_rel import RelativeFixedpointTypesetter
from upy2.typesetting.protocol import Convention
#from upy2.averaging import *
#from upy2.linear_regression import *

__version__ = '2.3.4'


# Create the module-scope ID generator ...

guid_generator = IDGenerator()  # Globally Unique IDs
