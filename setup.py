from setuptools import setup

long_description = \
r"""Measurements are precise only up to a certain *uncertainty*.  Such
measurement results are thus called *uncertain quantities*.
 When performing calculations with uncertain quantities, the 
uncertainties of the results depend on the uncertainties of the
operands involved.  The quantification of uncertainties resulting from
a mathematical operation involving uncertain operands is called
*uncertainty propagation*.
 From a programmer's point of view, uncertainties might be associated
with the respective nominal values, such that the propagation of
uncertainties happens automatically, and existing algorithms can be
re-used with the *uncertain quantities* as arguments.
 Here I am proposing a Python package to define uncertain operands, to
carry out calculations using such operands *with uncertainty
propagation*, and to provide string representations of uncertain
quantities involved.
 Complex uncertain values are supported; net uncertainties can be
given for real-valued quantities.  The objects holding uncertain
values have array properties, though scalar arrays can be used;
elements of an array behave as if they were uncertain quantities on
their own.  When requesting a string representation of an uncertain
quantity, the typeset result can be influenced by the number of
standard deviations to use and by the precision of the decimal
fractions with respect to the uncertainty; when typesetting
multidimensional arrays with uncertainty, the decimal fractions are
aligned to improve readability of the results.
 ``upy`` uses *Algorithmic Differentiation* (also known as *Automatic
Differentation*) to track uncertainties through the operations.
Uncertain values might be used in calculations together with other
uncertain values as well as with any numeric Python or ``numpy``
objects.  A range of mathematical operations is supported.
 ``upy`` provides several syntactic conventions appropriate to the
subject.  For instance, defining uncertain quantities is possible by
writing:

.. code:: python

    uvalue = nominal +- u(uncertainty)

where ``u`` is a function provided by ``upy``.  Uncertain values
constructed in this way will be independent of each other with respect
to their uncertainties; ``upy`` will keep track of the correlations
arising from combination of uncertain quantities in mathematical
operations.  All functionality is thread safe, and suited both for use
in the interactive Python shell as well as in programs for numerical
analysis. """

setup(
    name='upy',
    version='2.0.1a4',
    description='Python Uncertainties',
    long_description=long_description,
    author='Friedrich Romstedt',
    author_email='friedrichromstedt@gmail.com',
    #url='http://friedrichromstedt.github.com/upy/',
    packages=[
        'upy2',
        'upy2.typesetting',
    ],
    install_requires=[
        'numpy',
    ],
    classifiers=\
        ['Development Status :: 3 - Alpha',
         'Environment :: Console',
         'Intended Audience :: Science/Research',
         'License :: OSI Approved :: MIT License',
         'Natural Language :: English',
         'Operating System :: OS Independent',
         'Programming Language :: Python :: 2',
         'Topic :: Scientific/Engineering :: Information Analysis',
         'Topic :: Scientific/Engineering :: Mathematics'],
)
