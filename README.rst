Measurements are precise only up to a particular *uncertainty*.  Such
measurement results are thus called *uncertain quantities*.  When
performing calculations with uncertain quantities, the uncertainties of the
results depend on the uncertainties of the operands involved.  The
quantification of uncertainties resulting from a mathematical operation
involving uncertain operands is called *uncertainty propagation*.

From a programmer's point of view, uncertainties might be associated with
the respective nominal values, such that the propagation of uncertainties
happens automatically, and existing algorithms can be re-used with the
*uncertain quantities* as arguments.  Here I am proposing a Python package
to define uncertain operands, to carry out calculations using such operands
*with uncertainty propagation*, and to provide string representations of
uncertain quantities involved.

Complex numbers can be used to define uncertain quantities; for such
complex-valued uncertainties no net uncertainty can be calculated.

The objects holding uncertain values have array properties, though scalar
arrays can be used; elements of an uncertain array behave as if they were
uncertain quantities on their own.

When requesting a string representation of an uncertain quantity, the
typeset result depends on the number of standard deviations to use and on
the chosen precision, given by the number of digits with respect to the
uncertainty.  Furthermore, when typesetting multidimensional arrays with
uncertainty, the decimal fractions are aligned to improve readability of
the results.

``upy`` uses *algorithmic differentiation* (also known as *automatic
differentation*) to track uncertainties through the operations.  Uncertain
values might be used in calculations together with other uncertain values
as well as with any numeric Python or ``numpy.ndarray`` objects.  A range
of mathematical functions is supported.

``upy`` provides several syntactic conventions appropriate to the
subject.  For instance, defining uncertain quantities is possible by
writing:

.. code:: python

    uvalue = nominal +- u(uncertainty)

where ``u`` is a function provided by ``upy``.  Uncertain values
constructed in this way will be independent of each other with respect to
their uncertainties; ``upy`` will keep track of the correlations arising
from combination of uncertain quantities in mathematical operations.  All
functionality is suited both for use in the interactive Python shell as
well as in programs for numerical analysis.
