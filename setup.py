import distutils.core

long_description = \
r"""Physical measurements are precise only up to a certain
*uncertainty*.  Measurement results are thus called *uncertain
quantities*.

When performing calculations with them, the calculation outcomes will
feature a certain uncertainty as well.  Here, the uncertainty of the
result will depend on the operands' uncertainty.

The quanitification of the results of mathematical operations with
*uncertain operands* is called *uncertainty propagation*.

Here I am proposing a Python package meant to define uncertain
operands, to carry out calculations using such operands *with
uncertainty propagation*, and to provide string representations of any
*uncertain quantity* involved.

String representations of uncertain quantities can be tuned by giving
the *precision* of the decimal fractions involved based on the
standard deviation of the uncertainty and the number of standard
deviations, and conversion of uncertain arrays aligns decimal
fractions such that the result is well-readable.  ``upy`` uses
*Algorithmic Differentiation* (also known as *Automatic
Differentiation*) to track uncertainties through the operations.
Complex values are supported (both for the nominal value as well as
for the uncertainty), net uncertainties can be given for real-valued
quantities.

For this, ``upy`` provides a new class ``undarray``.  ``undarrays``
might be used in calculations with other ``undarrays`` or any numeric
Python or ``numpy`` objects.  A broad range of mathematical operations
is supported.

``upy`` provides several syntactic conventions adapted to the subject.
For instance, defining uncertain quantities is possible by writing:

.. code:: python

    uvalue = value +- u(uncertainty)

All functionality is thread safe, and suited both for use in the
interactive Python shell as well as in programs for numerical
analysis.
"""

distutils.core.setup(
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
        ['Development Status :: 4 - Beta',
         'Environment :: Console',
         'Intended Audience :: Science/Research',
         'License :: OSI Approved :: MIT License',
         'Natural Language :: English',
         'Operating System :: OS Independent',
         'Programming Language :: Python :: 2',
         'Topic :: Scientific/Engineering :: Information Analysis',
         'Topic :: Scientific/Engineering :: Mathematics'],
)
