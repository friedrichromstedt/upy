import upy2
from upy2.typesetting.scientific import ScientificTypesetter

a = upy2.undarray(10, 2)

with ScientificTypesetter(2, 3):
    print a

print a
