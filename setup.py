from setuptools import setup

long_description = \
r"""Physical measurements are precise only up to a certain
*uncertainty*.  Measurement results are thus called *uncertain
quantities*.

When performing calculations with uncertain quantities, the outcomes
of the calculations will feature a certain uncertainty as well.  The
uncertainty of the results can be expressed in terms of the
uncertainties of the operands involved.

The uncertainty quantification of results of mathematical operations
involving *uncertain operands* is called *uncertainty propagation*.

Here I am proposing a Python package to define uncertain
operands, to carry out calculations using such operands with
uncertainty propagation, and to provide string representations of
uncertain quantities involved.

Complex uncertain values are supported; net uncertainties can be given
for real-valued quantities.  Uncertain values can be arrays; each of
the elements is independent of the other elements in an array.  When
requesting string representations of uncertain quantities, the typset
results can be influenced by the number of standard deviations to use
and by the precision of the decimal fractions with respect to the
uncertainty; when typesetting arrays with uncertainty, the decimal
fractions are aligned to improve readability of the results.

``upy`` uses *Algorithmic Differentiation* (also known as *Automatic
Differentation*) to track uncertainties through the operations.
Uncertain values might be used in calculations with other uncertain
values or any numeric Python or ``numpy`` objects.  A broad range of
mathematical operations is supported.

``upy`` provides several syntactic conventions appropriate to the
subject.  For instance, defining uncertain quantities is possible by
writing:

.. code:: python

    uvalue = value +- u(uncertainty)

All functionality is thread safe, and suited both for use in the
interactive Python shell as well as in programs for numerical
analysis.
"""

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
