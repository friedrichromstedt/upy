import mod
from mod import access

mod.registry[1] = 2
print access(1)
