import upy2
import upy2.typesetting.scientific

ua = upy2.undarray([1, 1, -1], [2, 3, 4]).reshape((3, 1))

ts = upy2.typesetting.scientific.ScientificTypesetter(
    stddevs=1,
    relative_precision=1,
)

print ts.typeset(ua)
