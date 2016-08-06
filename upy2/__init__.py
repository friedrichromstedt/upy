# XXX Don't forget to modify the version string in setup.py
__version__ = '0.4.11b'
__version_tup__ = (0, 4, 11)

# Developed since: Jan 2010

# Create the module-scope id generator ...

from upy2.id_generator import *
id_generator = IDGenerator()

# Load all the things ...

from upy2.core import *
from upy2.operators import *
from upy2.umath import *
from upy2.averaging import *
from upy2.linear_regression import *
