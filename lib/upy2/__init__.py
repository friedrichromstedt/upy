# Developed since: Jan 2010

from upy2.id_generator import IDGenerator
from upy2.core import *
from upy2.typesetting import ScientificTypesetter
#from upy2.averaging import *
#from upy2.linear_regression import *

__version__ = '2.0.1b3'


# Create the module-scope ID generator ...

guid_generator = IDGenerator()  # Globally Unique IDs

# Install the upy operators ...

import upy2.numpy_operators
upy2.numpy_operators.install_numpy_operators()
