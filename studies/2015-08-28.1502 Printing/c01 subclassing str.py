# Does not work:
class notwork(str):
    def __init__(self, a, b):
        self.a = a
        self.b = b
#
# >>> notwork(1, 2)
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# TypeError: str() takes at most 1 argument (2 given)

class works(str):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __new__(cls, a, b):
        return str.__new__(cls)
#
# >>> w = works(1, 2)
# >>> w
# ''
# >>> w.a
# 1
# >>> w.b
# 2
# >>> type(w)
# <class '__main__.works'>
#
class derived_notwork(works):
    def __init__(self, x):
        works.__init__(self, 0, 42)
        self.x = x
#
# >>> derived(10)
# TypeError: __new__() takes exactly 3 arguments (2 given)
# >>> derived(10, 11)
# TypeError: __init__() takes exactly 2 arguments (3 given)
#
