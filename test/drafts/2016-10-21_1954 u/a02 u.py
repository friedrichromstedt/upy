from upy2 import u, U, undarray
from upy2.typesetting.scientific import ScientificTypesetter

st = ScientificTypesetter(2, 2)
st.default()

uprov = U(2)
uprov.default()

print undarray(10, 2)
print [10] +- u([2])
print 10 +- u(2)
