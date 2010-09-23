import distutils.core
import upy

distutils.core.setup(
    name='upy',
    version=upy.__version__,
    description='Python Uncertainties',
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
