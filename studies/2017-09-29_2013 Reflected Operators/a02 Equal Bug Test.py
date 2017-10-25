""" This Test probes a numpy bug reported in upy several years ago.
The issue was, that the second operand to the ``equal`` ufunc (and
likewise to the ``not_equal`` ufunc) was a scalar numpy.object ndarray
holding the second operand.

The bug apparently is no longer present in numpy-1.13.3 nowadays (Oct
2017). """


import numpy


class Reporter(object):
    def __call__(self, a, b, *args, **kwargs):
        print b

numpy.set_numeric_ops(equal=Reporter(), not_equal=Reporter())


class X(object):
    pass

numpy.asarray([1, 2]) == X()
# output::
#
#   <__main__.X object at 0x7f78e0ae7c50>
#
# as it should be.

numpy.asarray(42) == X()
numpy.asarray([10, 20]) != X()
numpy.asarray(1) != X()
# everything okay.
