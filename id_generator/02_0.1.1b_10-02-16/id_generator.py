# Maintainer: Friedrich Romstedt <www.friedrichromstedt.org>
# Copyright 2008, 2009, 2010 Friedrich Romstedt
#    This file is part of upy.
#
#    upy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    upy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with upy.  If not, see <http://www.gnu.org/licenses/>.
# $Last changed: 2010 Feb 16$
# Developed since: Feb 2010
# File version: 0.1.1b

import threading
import numpy

__all__ = ['IDGenerator']

"""Implements a thread-safe generator for unique IDs."""


class IDGenerator:
	"""Implement unique IDs.  Thread-safe."""
	
	def __init__(self):
		self.lock = threading.Lock()
		self.id = 1L

	def get_id(self, shape):
		"""Return unique IDs in shape SHAPE."""
		
		shape = numpy.asarray(shape)
		N = shape.prod()

		# Make shure, that never two same IDs are returned, by locking the 
		# .lock until the procedure is complete ...

		self.lock.acquire()
		id_return = numpy.arange(self.id, self.id + N).reshape(shape)
		self.id += N
		# Now, as the id has been stepped, others can access.
		self.lock.release()

		return id_return
