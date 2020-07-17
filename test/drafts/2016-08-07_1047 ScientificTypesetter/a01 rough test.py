import upy2
import upy2.typesetting.scientific

ua = upy2.undarray(10, 2)

ts = upy2.typesetting.scientific.ScientificTypesetter(
    stddevs=2,
    precision=2,
)

print ts.typeset(ua)
