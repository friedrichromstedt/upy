# Developed since: Feb 2010
# Rewritten: Dec 2017

import threading
import numpy


class IDGenerator:
    """ Generates unique IDs in a thread-safe manner. """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._current_id = 1

    def get_idarray(self, shape):
        """ Returns unique IDs in shape *shape*. """
        
        # For an empty iterable *shape* like [] and (), ``numpy.prod``
        # returns 1.0 with dtype numpy.float by default; thus we need
        # to override the result dtype.  This does not affect the
        # standard case of non-empty iterables as *shape* like [1, 2]
        # or (42, 100).
        N = numpy.prod(shape, dtype=numpy.int)

        # Make creating the IDs and incrementing the ID counter
        # transactional:
        with self._lock:
            idarray = numpy.arange(
                self._current_id,
                self._current_id + N
            ).reshape(shape)
            self._current_id += N

        return idarray
