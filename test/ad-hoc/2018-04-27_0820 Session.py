# Run this file by ``python -i <file>``.

import numpy
import upy2
from upy2 import u, U, undarray
from upy2.typesetting import ScientificTypesetter

upy2.install_numpy_operators()
U(2).default()
ScientificTypesetter(stddevs=2, precision=2).default()
