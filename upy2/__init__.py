# XXX Don't forget to modify the version string in setup.py
__version__ = '0.4.11b'
__version_tup__ = (0, 4, 11)

# Developed since: Jan 2010

# Create the module-scope id generator ...

from upy.id_generator import *
id_generator = IDGenerator()

# Load all the things ...

from upy.core import *
from upy.operators import *
from upy.umath import *
from upy.averaging import *
from upy.linear_regression import *
