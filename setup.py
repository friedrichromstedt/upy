import distutils.core

long_description = \
r'''`upy <http://friedrichromstedt.github.com/upy/>` is a Python package for 
handling uncertainties.  It provides a class for storing uncertain arrays or 
scalars.

Uncertain arrays can be constructed in three ways:

1)  From nominal value and a specification of the symmetric error.
2)  By calculating functions of one or more uncertain arrays.
3)  From a number of other uncertain arrays, in an array_like format.

There is no way to store asymmetric errors.

In case (1), all array elements will be independent variables.  The dependence
on this independent variables is tracked.  The error propagation is always 
applied to this independent variables.

The functions in case (2) must be known and well-behaved functions, in that
sense, that their derivatives with respect to their arguments must be 
accessible given the arguments' nominal values.  This criterion is fulfulled 
by many real-world functions, and most common functions are implemented.

Element access, slicing, element assignment is possible.  The uncertain array
class resemples the interface of numpy ndarrays.
'''


distutils.core.setup(
    name='upy',
    version='2.0.0b1',
    description='Python Uncertainties',
    long_description=long_description,
    author='Friedrich Romstedt',
    author_email='friedrichromstedt@gmail.com',
    url='http://friedrichromstedt.github.com/upy/',
    packages=[
        'upy2',
        'upy2.typesetting',
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
