# Developed since: Feb 2010

""" Implements a thread-safe generator for unique IDs. """

import threading
import numpy

__all__ = ['IDGenerator']


class IDGenerator:
    """ Generates unique IDs in a threadsafe manner. """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._current_id = 1

    def generate_idarray(self, shape):
        """ Returns unique IDs in shape *shape*. """
        
        # For an empty iterable *shape* like [] and (), ``numpy.prod``
        # returns 1.0 with dtype float by default; thus we need to
        # override the result dtype.  This does not affect the
        # standard case of non-empty iterables as *shape* like [1, 2]
        # or (42, 100).
        N = numpy.prod(shape, dtype=int)

        # Make sure that never two same IDs are returned by acquiring
        # ``self.lock`` until the transaction is complete:
        with self._lock:
            idarray = numpy.arange(
                self._current_id,
                self._current_id + N
            ).reshape(shape)
            self._current_id += N

        return idarray
