# Developed since: Feb 2010

import threading
import numpy

__all__ = ['IDGenerator']

"""Implements a thread-safe generator for unique IDs."""


class IDGenerator:
    """Implement unique IDs.  Thread-safe."""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.id = 1

    def get_id(self, shape):
        """Return unique IDs in shape SHAPE."""
        
        shape = numpy.asarray(shape)
        # Because shape may be (), then ().prod() is float by default.
        N = shape.prod(dtype = numpy.int)

        # Make shure, that never two same IDs are returned, by locking the 
        # .lock until the procedure is complete ...

        self.lock.acquire()
        id_return = numpy.arange(self.id, self.id + N).\
                reshape(shape)
        self.id += N
        # Now, as the id has been stepped, others can access.
        self.lock.release()

        return id_return
