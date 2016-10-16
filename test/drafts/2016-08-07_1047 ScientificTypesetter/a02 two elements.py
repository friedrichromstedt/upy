import upy2
import upy2.typesetting.scientific

ua = upy2.undarray([10, 100], [2, 3])

ts = upy2.typesetting.scientific.ScientificTypesetter(
    stddevs=1,
    relative_precision=2,
)

print ts.typeset(ua)
