upy Tutorial
============


Webcast
-------

There is a Webcast on the `sourceforge <http://upy.sourceforge.net/>`_ page,
presenting a talk on ``upy`` by me.  Its auditory should match you, although 
I'm not sure how well I matched the auditory :-).


Example Python Session
----------------------

Here is a small Python shell session::

    Python 2.6.5 (r265:79063, Jul 18 2010, 12:14:53) 
    [GCC 4.2.1 (Apple Inc. build 5659)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.

    >>> import upy
    >>> ua = upy.undarray(2, 0.1)
    >>> ub = upy.undarray(10, 0.05)
    >>> print ua, ub
    (2.00 +- 0.10) 10^0  (1.0000 +- 0.0051) 10^1 
    >>> print ub.printable(format='float')
    10.000 +- 0.050 
    >>> print ua * ub
    (2.00 +- 0.11) 10^1 
    >>> print upy.cos(ua * ub) + ub
    (1.041 +- 0.092) 10^1 

    >>> uc = upy.undarray([[1, 2], [3, 4]], [[0.1, 0.5], [0.7, 2]])
    >>> print uc
    [[(1.00 +- 0.10) 10^0  (2.00 +- 0.50) 10^0 ]
     [(3.00 +- 0.70) 10^0  (4.0  +- 2.0 ) 10^0 ]]

    >>> ^D
    Python-32(3414) malloc: *** error for object 0x239670: incorrect checksum 
    for freed object - object was probably modified after being freed.
    *** set a breakpoint in malloc_error_break to debug

Notice the nice error in the end.  Can you reproduce this (on your machine)?
It is related to numpy.
