# Copyright (c) 2010 Friedrich Romstedt <friedrichromstedt@gmail.com>
# See also <www.friedrichromstedt.org> (if e-mail has changed)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
