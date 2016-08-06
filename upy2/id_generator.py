# Developed since: Feb 2010

import threading
import numpy

__all__ = ['IDGenerator']

"""Implements a thread-safe generator for unique IDs."""


class IDGenerator:
    """ Generates unique IDs in a threadsafe manner. """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._current_id = 1

    def get_idarray(self, shape):
        """ Returns unique IDs in shape *shape*. """
        
#X        shape = numpy.asarray(shape)
#X        # Because shape may be (), then ().prod() is float by default.
#X        N = shape.prod(dtype = numpy.int)
        # For an empty iterable *shape* like [] and (), ``numpy.prod``
        # returns 1.0 with dtype numpy.float by default; thus we need
        # to override the result dtype.  This does not affect the
        # standard case of non-empty iterables as *shape* like [1, 2]
        # or (42, 100).
        N = numpy.prod(shape, dtype=numpy.int)

        # Make sure that never two same IDs are returned by locking the 
        # .lock until the procedure is complete ...

        with self._lock:
            idarray = numpy.arange(
                self._current_id,
                self._current_id + N
            ).reshape(shape)
            self._current_id += N

        return idarray
#X
#X        self.lock.acquire()
#X        id_return = numpy.arange(self.id, self.id + N).\
#X                reshape(shape)
#X        self.id += N
#X        # Now, as the id has been stepped, others can access.
#X        self.lock.release()
#X
#X        return id_return
