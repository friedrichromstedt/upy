# Developed since: Jan 2010

# Create the module-scope ID generator ...

from upy2.id_generator import IDGenerator
guid_generator = IDGenerator()  # Globally Unique IDs

# Load all the things ...

from upy2.core import *
import upy2.numpy_operators
#from upy2.umath import *
#from upy2.averaging import *
#from upy2.linear_regression import *

upy2.numpy_operators.install_numpy_operators()