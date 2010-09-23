import distutils.core

long_description = \
"""upy is a package for calculating `error propagation <http://en.wikipedia.org/wiki/Propagation_of_uncertainty>`_ in the programming language `Python <http://www.python.org>`_.  For the needed derivative information, `automatic differentiation <http://en.wikipedia.org/wiki/Automatic_differentiation>`_ (AD) is used.  (AD is also known under the name *algorithmic differentiation*.)

upy is based on `numpy <http://numpy.scipy.org>`_, and can be used to store multidimensional arrays with uncertainty."""

distutils.core.setup(
    name='upy',
    version='0.4.11b',
    description='Python Uncertainties',
    long_description=long_description,
    author='Friedrich Romstedt',
    author_email='friedrichromstedt@gmail.com',
    url='http://upy.sourceforge.net/',
    packages=['upy'],
    package_dir={'upy': '.'},
    classifiers=\
        ['Development Status :: 4 - Beta',
         'Environment :: Console',
         'Intended Audience :: Science/Research',
         'License :: OSI Approved :: MIT License',
         'Natural Language :: English',
         'Operating System :: OS Independent',
         'Programming Language :: Python :: 2',
         'Topic :: Scientific/Engineering :: Information Analysis',
         'Topic :: Scientific/Engineering :: Mathematics']
)
