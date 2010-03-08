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
# $Last changed: 2010 Feb 14$
# Developed since: Feb 2010
# File version: 0.1.0b

import numpy

__all__ = ['Characteristic']

"""Dependence on multiple error sources."""


class Characteristic:
	"""A Characteristic is a dictionary of error source names and 
	dependencies on that sources.  Read-only attributes:
		
	.dependencies - {source's name: Dependency instance}"""

	#
	# Initialisation ...
	# class Characteristic cannot be made a dictionary, because the key access
	# is used to address subsets of the arrays contained.
	#

	def __init__(self, shape):
		"""SHAPE is the shape of the data the Characteristic instance is
		for.  It is used when broadcasting other Characteristics coerced
		with this instance to the correct shape."""

		self.dependencies = {}
		self.shape = shape
		self.ndim = len(self.shape)

	#
	# Obtaining the dispersion ...
	#
	
	def get_dispersion(self):
		"""Return the dispersion induced by all the dependencies stored in
		the Characteristic."""

		return sum([dependency.get_dispersion() for \
				dependency in self.dependencies.values()])

	#
	# Accessing the dependencies ...
	#

	def get_sources(self):
		"""Return the sources this Characteristic depends on."""

		return self.dependencies.keys()

	def set_dependency(self, source, dependency):
		"""Set the dependency on source SOURCE to DEPENDENCY."""

		self.dependencies[source] = dependency

	#
	# Binary arithmetic operators ...
	#

	def __add__(self, other):
		"""OTHER must be a Characteristic instance.  Add dependencies on
		the same error source together.  self and the OTHER Characteristic 
		instance will be .broadcast()'ed to the .shape with the largest .ndim 
		before being added together.  Broadcasting is necessary because not
		both Characteristics must depend on all Dependencies, thus some 
		Dependencies would be taken over, leaving their shape unchanged, and
		thus compromising data integrity, because there will be no numpy
		broadcasting mechanism bringing the operands to common shape.
		
		For the functionality of .broadcast(), see Dependency.broadcast()."""

		# Determine the shape of the resulting Characteristic instance ...

		# Set default values.
		self_broadcast = self
		other_broadcast = other
		
		if self.ndim > other.ndim:
			# Use self's .shape.
			result_shape = self.shape
			
			# Broadcast OTHER.
			other_broadcast = other.broadcast(shape = result_shape)

		elif self.ndim < other.ndim:
			# Use other's .shape.
			result_shape = other.shape

			# Broadcast self.
			self_broadcast = self.broadcast(shape = result_shape)

		elif self.ndim == other.ndim:
			# Check the shapes.
			if self.shape != other.shape:
				raise ValueError('Shape mismatch: Objects cannot be broadcast to a single shape.')
		
			# If the check doesn't fail, it doesn't matter whose shape to use.
			result_shape = self.shape

			# No object must be broadcast()'ed.

		result = Characteristic(shape = result_shape)

		self_sources = self_broadcast.get_sources()
		other_sources = other_broadcast.get_sources()

		# Calculate the union of the two sets ...

		sources = []

		# Copy the values from self_sources.
		for source in self_sources:
			sources.append(source)

		# Add the missing values from other_sources.
		for source in other_sources:
			if source not in sources:
				sources.append(source)

		for source in sources:

			if source in self_sources and source in other_sources:

				# Both operands depend on the SOURCE and the Dependency
				# instances must be added together ...
				#
				# It is fully intended to create a new Dependency instance 
				# with another new .derivative attribute.
				# This is necessary, because we do not copy in the else: 
				# branch, and hence bear the Dependencies from the added 
				# Characteristic as long as they are not added together with 
				# another Dependency on the same error source.

				result.set_dependency(source, 
						self_broadcast.dependencies[source] + \
								other_broadcast.dependencies[source])

			elif source in self_sources:

				# Only SELF depends on the error source.  Let the RESULT
				# bear SELF's Dependency ...

				result.set_dependency(source, \
						self_broadcast.dependencies[source])

			elif source in other_sources:
					
				# Only OTHER depends on the error source.  Let the RESULT
				# bear OTHER's Dependency ...

				result.set_dependency(source, \
						other_broadcast.dependencies[source])
			
			# No more cases exist.

		return result
	
	def __sub__(self, other):
		"""OTHER must be a Characteristic instance.  Add dependencies on 
		the same error source together."""

		return self + (-other)

	def __mul__(self, other):
		"""Multiply all Dependencies contained with a coefficient, in a new 
		Characteristic instance."""

		# Convert OTHER to a (maybe scalar) numpy.ndarray ...

		other = numpy.asarray(other)

		# Determine the shape of the resulting Characteristic instance 
		# and broadcast() self if necessary.  If other.ndim > self.ndim,
		# then broadcasting of self is necessary to get the .dispersion 
		# attributes of the Dependencies set to the correct shape (the
		# .derivative attributes would be broadcast by numpy in 
		# multiplication also).

		# Set default values.
		self_broadcast = self
		other_broadcast = other
		
		if self.ndim > other.ndim:
			# Use self's .shape.
			result_shape = self.shape
			
			# OTHER will be broadcast by numpy in multiplication.

		elif self.ndim < other.ndim:
			# Use other's .shape.
			result_shape = other.shape

			# Broadcast self.
			self_broadcast = self.broadcast(shape = result_shape)

		elif self.ndim == other.ndim:
			# Check the shapes.
			if self.shape != other.shape:
				raise ValueError('Shape mismatch: Objects cannot be broadcast to a single shape.')
		
			# If the check doesn't fail, it doesn't matter whose shape to use.
			result_shape = self.shape

			# No object must be broadcast()'ed.

		result = Characteristic(shape = result_shape)

		for source in self.get_sources():
			result.set_dependency(source, \
					self_broadcast.dependencies[source] * other)

		return result

	def __div__(self, other):
		"""Multiply all Dependencies contained with a coefficient, in a new
		Characteristic instance."""

		return self * (1.0 / other)

	#
	# Reverse binary operators ...
	#

	# __radd__() and __rsub__() are not needed because only Characteristics 
	# are allowed as operands.

	def __rmul__(self, other):
		"""Multiply all Dependencies contained with a coefficient, in a new
		Characteristic instance.  .shape is maintained."""

		result = Characteristic(shape = self.shape)

		for source in self.get_sources():
			result.set_dependency(source, other * self.dependencies[source])

		return result

	#
	# Augmented arithmetics will be emulated by using standard
	# arithmetics ...
	#

	#
	# Unary operators ...
	#

	def __pos__(self):
		"""Return self."""

		return self
	
	def __neg__(self):
		"""Return the Characteristic with all Dependencies inverted."""

		result = Characteristic(shape = self.shape)

		for source in self.get_sources():
			result.set_dependency(source, -self.dependencies[source])

		return result

	#
	# Keying methods ...
	#
	
	def __getitem__(self, (shape, key)):
		"""Argument is not directly the key, but the tuple (SHAPE, KEY).
		I.e., call self[new_shape, key].  This is permissible, because
		the undarray can determine the shape from the key applied to the
		undarray's .value.  Return the given subset of all Dependencies 
		contained.  Return value will be a Characteristic."""

		result = Characteristic(shape)

		for source in self.get_sources():
			result.set_dependency(source, self.dependencies[source][key])

		return result

	def __setitem__(self, key, value):
		"""VALUE is supposed to be an Characteristic instance.  Update the 
		given subset of all Dependencies contained with the respective 
		Dependencies of VALUE."""

		for source in self.get_sources():
			# This cannot be done by self.set_dependency().
			self.dependencies[source][key] = value.dependencies[source]

	def __len__(self):
		"""Return len() applied to the first Dependency in this dict.  If
		this is not applicable, the call will fail."""

		used_source = self.get_sources()[0]

		return len(self.dependencies[used_source])
		
	#
	# ndarray methods ...
	#

	def flatten(self, shape, *flatten_args, **flatten_kwargs):
		"""Returns a copy with flatten()'ed Dependency instances.  The 
		arguments are handed over to the Dependencies' methods.  SHAPE is
		the new shape."""

		result = Characteristic(shape = shape)
		for source in self.get_sources():
			result.set_dependency(source, self.dependencies[source].flatten(
				*flatten_args, **flatten_kwargs))
		return result

	def repeat(self, shape, *repeat_args, **repeat_kwargs):
		"""Returns a copy with repeat()'ed Dependency instances.  The
		arguments are handed over to the Dependencies' methods.  SHAPE is
		the new shape."""

		result = Characteristic(shape = shape)
		for source in self.get_sources():
			result.set_dependency(source, self.dependencies[source].repeat(
				*repeat_args, **repeat_kwargs))
		return result

	def reshape(self, shape, *reshape_args, **reshape_kwargs):
		"""Returns a copy with reshape()'ed Dependency instances.  The
		arguments are handed over to the Dependencies' methods.  SHAPE is
		the new shape."""

		result = Characteristic(shape = shape)
		for source in self.get_sources():
			result.set_dependency(source, self.dependencies[source].reshape(
				*reshape_args, **reshape_kwargs))
		return result
	
	def transpose(self, shape, *transpose_args, **transpose_kwargs):
		"""Returns a copy with transpose()'ed Dependency instances.  The
		arguments are handed over to the Dependencies' methods.  SHAPE is
		the new shape."""

		result = Characteristic(shape = shape)
		for source in self.get_sources():
			result.set_dependency(source, self.dependencies[source].transpose(
				*transpose_args, **transpose_kwargs))
		return result

	#
	# Special array methods ...
	#

	def broadcast(self, shape):
		"""Broadcasts the Characteristic to shape SHAPE by broadcast()'ing
		the contained Dependencies.  Thus, for documentation, see
		Dependency.broadcast()."""

		result = Characteristic(shape = shape)
		for source in self.get_sources():
			result.set_dependency(source, 
					self.dependencies[source].broadcast(shape = shape))
		return result
