from upy2 import u, U
from upy2.typesetting import ScientificTypesetter

U(2).default()
ScientificTypesetter(2, 2).default()

a = u(2.0)
print a

b = u([1.0, 2.0])
print b

c = 10 +- u([[1.0, 2.0], [5.0, 20.0]])
print c

d = u(1)  # Integer ``1`` will be truncated in division by ``2``.
print d
