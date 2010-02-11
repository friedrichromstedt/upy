# Maintainer: Friedrich Romstedt <friedrichromstedt@gmail.com>
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
# $Last changed: 2010 Feb 3$
# Developed since: Jan 2010
# File version: 0.2.2b

import numpy
import decimal_toolbox


class Dependency:
	"""A Depency represents, that a variable depends by some derivation on
	some error source.  When adding Dependencies, the derivations will add.
	When mulitplying a Dependency, the derivative will be multiplied.  A
	Dependency holds arrays of derivatives and dispersions, scalar arrays
	or pure scalars.  To find out what the actual dispersion induced by the
	dependency is, call .get_dispersion().  It computes the dispersion from
	the dispersion of the error source and from the derivative with that
	the target depends on that error source, by using:
		
		disperion = derivative ** 2 * error_source_dispersion
	"""

	#
	# Initialisation methods ...
	#

	def __init__(self, derivative, dispersion):
		"""Initialise the dependency on the error source of dispersion
		VARIANCE with derivative DERIVATIVE on that error source.
		DERIVATIVE and DISPERSION are supposed to have equal shape."""

		self.derivative = derivative
		self.dispersion = dispersion

		self.shape = self.derivative.shape
		self.ndim = self.derivative.ndim

	#
	# Obtaining the dispersion ...
	#

	def get_dispersion(self):
		"""Get the dispersion induced by this dependency."""

		return self.derivative ** 2 * self.dispersion

	#
	# Arithmetics:  Binary arithmetics ...
	#

	def __add__(self, other):
		"""OTHER must be a Dependency instance.  Add the dependencies
		together, such that the target depends by both on the error source."""

		# assuming self.sigmasquared == other.sigmasquared.
		return Dependency(
				derivative = self.derivative + other.derivative,
				dispersion = self.dispersion)
	
	def __sub__(self, other):
		"""OTHER must be a Dependency instance.  Add the dependencies
		together, such that the target depends by both on the error source."""

		# assuming self.sigmasquared == other.sigmasquared.
		return Dependency(
				derivative = self.derivative - other.derivative,
				dispersion = self.dispersion)

	def __mul__(self, other):
		"""Multiply the dependency by some factor, i.e., scale the 
		derivative."""

		return Dependency(
				derivative = self.derivative * other,
				dispersion = self.dispersion)

	def __div__(self, other):
		"""Multiply the dependency by some factor, i.e., scale the
		derivative."""

		return Dependency(
				derivative = self.derivative / other,
				dispersion = self.dispersion)

	#
	# Arithmethics:  Reversed arithmetics ...
	#

	# __radd__() and __rsub__() are not needed, because always both operands
	# will be Dependency instances.

	def __rmul__(self, other):
		return Dependency(
				derivative = other * self.derivative,
				dispersion = self.dispersion)
	
	# __rdiv__() is undefined, makes no sense.

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
		"""Return the dependency, where the target depends inversed on
		the error source, i.e, invert the derivative."""

		return Dependency(
				derivative = -self.derivative,
				dispersion = self.dispersion)
	
	
	#
	# Keying methods ...
	#
	
	def __getitem__(self, key):
		"""Returns the Dependency of the given subset applied to the
		derivatives and dispersions."""

		return Dependency(
				derivative = self.derivative[key],
				dispersion = self.dispersion[key])

	def __setitem__(self, key, value):
		"""VALUE is supposed to by a suitable Dependency instance."""

		self.derivative[key] = value.derivative
		self.dispersion[key] = value.dispersion

	def __len__(self):
		return len(self.derivative)
	
	#
	# ndarray methods ...
	#

	def flatten(self, *flatten_args, **flatten_kwargs):
		"""Returns a copy with the Dependency's arrays flatten()'ed.  The
		arguments are handed over to the arrays' methods."""

		return Dependency(
				derivative = self.derivative.flatten(
					*flatten_args, **flatten_kwargs),
				dispersion = self.dispersion.flatten(
					*flatten_args, **flatten_kwargs))

	def repeat(self, *repeat_args, **repeat_kwargs):
		"""Returns a copy with repeat()'ed arrays.  The arguments are handed 
		over to the arrays' methods."""

		return Dependency(
				derivative = self.derivative.repeat(
					*repeat_args, **repeat_kwargs),
				dispersion = self.dispersion.repeat(
					*repeat_args, **repeat_kwargs))

	def reshape(self, *reshape_args):
		"""Returns a copy with reshape()'ed arrays.  The arguments are
		handed over to the arrays' methods.  numpy.reshape() takes no
		keyword arguments."""

		return Dependency(
				derivative = self.derivative.reshape(*reshape_args),
				dispersion = self.dispersion.reshape(*reshape_args))

	def transpose(self, *transpose_args, **transpose_kwargs):
		"""Returns a copy with transpose()'ed arrays.  The arguments are
		handed over to the arrays' methods."""

		return Dependency(
				derivative = self.derivative.transpose(
					*transpose_args, **transpose_kwargs),
				dispersion = self.dispersion.transpose(
					*transpose_args, **transpose_kwargs))

	#
	# Special array methods ...
	#

	def broadcast(self, shape):
		"""Bring the instance in shape SHAPE, by repetition of the object.  No
		reshape()'ing will be performed.  This function is used when coercing
		lower-dimensional object with higher-dimensional ones.  It makes shure
		that both operands can have the same shape before coercion takes 
		place.  Broadcasting is necessary in the case that an Dependency is
		taken over from the other operand into the final result, because there
		is no dependency of both operands on the Dependency.  In this case,
		no numpy broadcasting would occour, and the data integrity would be
		compromised.

		The call will fail if len(SHAPE) < .ndim.  Otherwise, the .ndim last
		items of SHAPE must be equal to .shape.  The object will first be
		brought to the shape [1, 1, 1, ...] + .shape, such that .ndim 
		becomes len(SHAPE).  Then, it will be repeated in the added dimensions
		to meet SHAPE's elements.  The first step is done via .reshape(), and
		the second via .repeat(count, axis = axis)."""

		# Check conditions ...

		if len(shape) < self.ndim:
			raise ValueError('Dependency with shape %s cannot be broadcast to shape %s.' % (self.shape, shape))

		# If the object is scalar, the expression wouldn't work.
		if self.ndim != 0:
			if shape[-self.ndim:] != self.shape:
				raise ValueError('Dependency with shape %s cannot be broadcast to shape %s.' % (self.shape, shape))
		# else: Scalar object can be broadcast to any shape.

		# Prepare intermediate shape ...

		shape = list(shape)
		intermediate_shape = [1] * (len(shape) - self.ndim) + list(self.shape)

		# result will in the end hold the result.
		result = self.reshape(tuple(intermediate_shape))

		# Repeat self_intermediate to match SHAPE ...

		for dim in xrange(0, len(shape) - self.ndim):

			# Repeat in SHAPE's dimension dim.
			result = result.repeat(
					shape[dim], axis = dim)
		
		# result became final object ...

		return result

	#
	# String conversion function ...
	#

	def __str__(self):
		"""Short representation."""

		if self.ndim == 0:
			
			# Return a scalar representation ...

			return "(derivative = %e, dispersion = %d)" % \
					(self.derivative, self.dispersion)
		else:

			# Return an array representation ...

			return "(derivative:\n%e, dispersion:\n%e\n)" % \
					(self.derivative, self.dispersion)

	# There seems to be no sensible __repr__().


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


class undarray:
	"""Implements error afflicted ndarrays.  The name is derived from
	numpy.ndarray.  Read-ony attributes:
		
	.value - The plain nominal value of the undarray."""

	def __init__(self,
			object,
			error = None, sigma = None, 
			derivatives = None,
			characteristic = None,
			dtype = None):
		"""Initialise from object OBJECT.  If OBJECT is an undarray, its 
		content will not be copied.  (This initialisation scheme is intendend 
		to make shure that some object is an undarray.)  Else the OBJECT is 
		interpreted as the value of the undarray.  The standard deviation can 
		be specified either by ERROR (2 * standard deviation) or by sigma 
		(= standard deviation).  When DERIVATIVES is not None, it must be a 
		list [(undarray instance: derivative), ...], giving the derivatives 
		of the dependency of the new undarray on the key undarrays.  From 
		value-OBJECTs newly created undarrays convert their value first by 
		numpy.asarray().  When ERROR, SIGMA and DERIVATIVES are all None, an 
		undarray without dependencies on error sources will be created, i.e., 
		a precise ndarray wrap.  Also CHARACTERISTIC can be given, directly 
		specifying the dependence on various error sources.  You can specify 
		the dtype of the undarray (value & sigma) by DTYPE.  

		It is ineffective to create undarrays from lists of undarrays, 
		because all the different undarrays have most likely different error 
		sources.  Thus for each error source there would to be maintained a 
		distinct array storing mostly zeros, except for the element of that 
		single undarray component.  It is therefore by design choice not 
		implemented to create undarrays from several other undarrays in a 
		list structure."""
		
		if isinstance(object, undarray):

			# Take over attributes from existing undarray ...
		
			self.value = object.value
			self.characteristic = object.characteristic

		elif derivatives is not None:

			# Derive the new undarray from known ones ...

			self.value = numpy.asarray(object, dtype = dtype)

			# Create a new, empty Characteristic where we can fill in
			# the dependencies introduced by the dictionary DERIVATIVES.
			self.characteristic = Characteristic(shape = self.value.shape)

			# Fill in the dependencies.
			for (instance, derivative) in derivatives:
				self.characteristic += \
						instance.characteristic * derivative

		elif error is not None or sigma is not None:
			
			# Constuct a new undarray ...

			self.value = numpy.asarray(object, dtype = dtype)
			
			# Calculate standard deviation.
			if error is not None:
				sigma = numpy.asarray(error, dtype = dtype) / 2.0
			else:
				sigma = numpy.asarray(sigma, dtype = dtype)

			# Check shape.
			if self.value.shape != sigma.shape:
				raise ValueError("Shape mismatch between OBJECT and SIGMA or ERROR.  Shapes are: OBJECT %s, SIGMA/ERROR %s" % (self.value.shape, sigma.shape))

			# Create Dependency instance from scratch.
			dependency = Dependency(
					derivative = numpy.ones(shape = self.value.shape),
					dispersion = sigma ** 2)

			# Use id(dependency) as source name.
			self.characteristic = Characteristic(shape = self.value.shape)
			self.characteristic.set_dependency(id(dependency), dependency)

		elif characteristic is not None:
			
			# Take over characteristic ...

			self.value = numpy.asarray(object, dtype = dtype)
			self.characteristic = characteristic
			
		else:

			# Construct an empty undarray ...

			self.value = numpy.asarray(object, dtype = dtype)
			self.characteristic = Characteristic(shape = self.value.shape)
		
		self.shape = self.value.shape
		self.ndim = self.value.ndim

	#
	# Methods to obtain net quantities ...
	#

	def dispersion(self):
		"""Returns the dispersion array, i.e., sigma ** 2."""

		return self.characteristic.get_dispersion()

	def sigma(self):
		"""Returns the sigma array, i.e., the variance."""

		return numpy.sqrt(self.dispersion())

	def variance(self):
		"""Returns the variance, i.e., the sigma."""

		return numpy.sqrt(self.dispersion())

	def error(self):
		"""Returns the error, i.e., 2 * sigma."""

		return 2 * self.sigma()
	
	def weight(self):
		"""Returns an numpy.ndarray suitable for weighting this undarray.
		The weights are 1.0 / .dispersion().  When a dispersion element is
		zero, the used dispersion is 1.0."""
		
		# Calculate the dispersion used.
		used_dispersion = self.dispersion()
		used_dispersion += 1.0 * (used_dispersion == 0.0)

		# Calculate the weight from the dispersion.
		return 1.0 / used_dispersion

	#
	# Binary arithmetics ...
	#

	def __add__(self, other):
		if isinstance(other, undarray):
			return undarray(
					object = self.value + other.value,
					derivatives = [(self, 1.0), (other, 1.0)])
		else:
			return undarray(
					object = self.value + other,
					derivatives = [(self, 1.0)])

	def __sub__(self, other):
		if isinstance(other, undarray):
			return undarray(
					object = self.value - other.value,
					derivatives = [(self, 1.0), (other, -1.0)])
		else:
			return undarray(
					object = self.value - other,
					derivatives = [(self, 1.0)])

	def __mul__(self, other):
		if isinstance(other, undarray):
			return undarray(
					object = self.value * other.value,
					derivatives = [(self, other.value), (other, self.value)])
		else:
			return undarray(
					object = self.value * other,
					derivatives = [(self, other)])

	def __div__(self, other):
		if isinstance(other, undarray):
			return self * (1.0 / other)
		else:
			return self * (1.0 / numpy.asarray(other))

	def __pow__(self, other):
		if isinstance(other, undarray):
			self_pow_other = self.value ** other.value
			return undarray(
					object = self_pow_other,
					derivatives = \
						[(self, self.value ** (other.value - 1) * other.value),
						 (other, self_pow_other * numpy.log(self.value))])

		else:
			other = numpy.asarray(other)
			return undarray(
					object = self.value ** other,
					derivatives = \
						[(self, self.value ** (other - 1) * other)])

	#
	# Reverse binary arithmetics ...
	#

	def __radd__(self, other):
		# OTHER is not an undarray.
		return undarray(
				object = other + self.value,
				derivatives = [(self, 1.0)])

	def __rsub__(self, other):
		# OTHER is not an undarray.
		return undarray(
				object = other - self.value,
				derivatives = [(self, -1.0)])

	def __rmul__(self, other):
		# OTHER is not an undarray.
		return undarray(
				object = other * self.value,
				derivatives = [(self, other)])

	def __rdiv__(self, other):
		# OTHER is not an undarray.
		other = numpy.asarray(other)
		return undarray(
				object = other / self.value,
				derivatives = [(self, -other / self.value ** 2)])

	def __rpow__(self, other):
		# OTHER is not an undarray.
		other_pow_self = other ** self.value
		return undarray(
				object = other_pow_self,
				derivatives = \
						[(self, other_pow_self * numpy.log(other))])

	#
	# Augmented arithmetics will be emulated ...
	#

	#
	# Unary operators ...
	#

	def __pos__(self):
		return self

	def __neg__(self):
		return undarray(
				object = -self.value,
				derivatives = [(self, -1)])

	def __abs__(self):
		"""This works for real-valued undarrays."""
		
		# Calculate an inversion mask ...

		inversion_mask = numpy.ones(shape = self.value.shape)

		for yi in xrange(0, self.values.shape[0]):
			for xi in xrange(0, self.values.shape[1]):
				if self.values[yi, xi] < 0:
					inversion_mask[yi, xi] = -1.0

		# Invert values which must be inverted, and invert also the dependency
		# of this values on the error source ...

		return self * inversion_mask
	
	#
	# Casts to int, float, ... are impossible, because we have ndarray values.
	#

	#
	# Comparison operators ...
	#

	def __lt__(self, other):
		if isinstance(other, undarray):
			return self.value < other.value
		else:
			return self.value < other

	def __le__(self, other):
		if isinstance(other, undarray):
			return self.value <= other.value
		else:
			return self.value <= other

	def __gt__(self, other):
		if isinstance(other, undarray):
			return self.value > other.value
		else:
			return self.value > other

	def __ge__(self, other):
		if isinstance(other, undarray):
			return self.value >= other.value
		else:
			return self.value >= other

	def __eq__(self, other):
		if isinstance(other, undarray):
			return self.value == other.value
		else:
			return self.value == other

	def __ne__(self, other):
		if isinstance(other, undarray):
			return self.value != other.value
		else:
			return self.value != other
	
	#
	# Keying methods ...
	#
	
	def __getitem__(self, key):
		"""Returns the given subset of the undarray array, by applying the
		KEY both the the value and the Characteristic.  VALUE is assumed
		to be an undarray."""

		object = self.value[key]
		return undarray(
				object = object,
				characteristic = self.characteristic[object.shape, key])

	def __setitem__(self, key, value):
		"""Updates the given subset of the undarray array, by replacing the
		value's subset and the Characteristic's subset.  VALUE is supposed
		to be an undarray.  Note that it is difficult to change the value
		of a subset of an undarray array once it is created.  This is because 
		of the tracking of error sources, which must be exactly the same for
		the replacement subset of the array."""

		# Update the respective subsets ...

		self.value[key] = value.value
		self.characteristic[key] = value.characteristic
		
	def __len__(self):
		return len(self.value)

	#
	# ndarray methods ...
	#

	def flatten(self, *flatten_args, **flatten_kwargs):
		"""Returns a copy with flatten()'ed arrays."""

		object = self.value.flatten(
				*flatten_args, **flatten_kwargs)
		return undarray(
				object = object,
				characteristic = self.characteristic.flatten(
					shape = object.shape,
					*flatten_args, **flatten_kwargs))

	def repeat(self, *repeat_args, **repeat_kwargs):
		"""Returns a copy with repeat()'ed arrays."""

		object = self.value.repeat(
				*repeat_args, **repeat_kwargs)
		return undarray(
				object = object,
				characteristic = self.characteristic.repeat(
					shape = object.shape,
					*repeat_args, **repeat_kwargs))

	def reshape(self, *reshape_args, **reshape_kwargs):
		"""Returns a copy with reshape()'ed arrays."""

		object = self.value.reshape(
				*reshape_args, **reshape_kwargs)
		return undarray(
				object = object,
				characteristic = self.characteristic.reshape(
					shape = object.shape,
					*reshape_args, **reshape_kwargs))

	def transpose(self, *transpose_args, **transpose_kwargs):
		"""Returns a copy with transpos()'ed arrays."""

		object = self.value.transpose(
				*transpose_args, **transpose_kwargs)
		return undarray(
				object = object,
				characteristic = self.characteristic.transpose(
					shape = object.shape,
					*transpose_args, **transpose_kwargs))

	#
	# Precision ...
	#

	def get_precision(self):
		"""The number of counting digits after the point in exponential 
		representation.  The position of the last counting digit.  The 
		precision may be zero or negative.  Note that this function fails 
		for non-scalar undarrays."""

		if self.ndim != 0:
			raise ValueError("Function not applicable to array undarrays.")

		exponent_value=decimal_toolbox.get_exponent(self.value)
		exponent_error=decimal_toolbox.get_exponent(self.error())
		return exponent_value-exponent_error+1

	#
	# Strings ...
	#

	def get_strings(self):
		"""Returns (mantissa string, error string, exponent string).  
		Mantissa string and error string represent the value's and the 
		error's mantissa with respect to the exponent common to both.  The
		exponent string has at least three digits and is in the form 
		e+000.  Note that this function fails for non-scalar undarrays."""
		
		if self.ndim != 0:
			raise ValueError("Function not applicable to array undarrays.")

		# Determine the counting exponents of the value and of the error ...

		error = self.error()

		if self.value == 0.0:
			# Exponent determined by error alone.
			if error == 0.0:
				# Use zero as fallback, as everything is zero actually.
				exponent = 0
			else:
				# Exponent is determined by error alone.
				exponent = decimal_toolbox.get_exponent(error)
		else:
			# Value determined exponent also.
			exponent_value = decimal_toolbox.get_exponent(self.value)
			if error == 0.0:
				# Error zero, su use value's exponent.
				exponent = exponent_value
			else:
				# Determine the maximum of both exponents.
				exponent_error = decimal_toolbox.get_exponent(error)
				exponent = max(exponent_value, exponent_error)

		# Scale the values such that the exponent's digit is just before
		# the dot.
		value_scaled = self.value * 10 ** (-exponent)
		error_scaled = error * 10 ** (-exponent)
		
		# The error determines the accuracy.
		error_scaled_exponent = decimal_toolbox.get_exponent(error_scaled)
		if error_scaled_exponent == decimal_toolbox.Infinity:
			# Use some large fallback value as an approximation of
			# infinite precision.
			error_scaled_exponent = -16  # 15 post-dot digits.

		# Obtain the value's mantissa string.
		mantissa_string = decimal_toolbox.get_rounded(
				value_scaled,
				error_scaled_exponent - 1)

		# Obtain the error's mantissa string, ceil()'ed.
		error_string = decimal_toolbox.get_rounded(
				error_scaled,
				error_scaled_exponent - 1,
				ceil = True)
		
		# Calculate the exponent's string.
		exponent_string = "e%+04d" % exponent

		# Return everything.
		return (mantissa_string, error_string, exponent_string)

	#
	# String conversion ...
	#

	def __str__(self):
		"""For scalar undarrays, return a useful print value of the value
		and the error.  For everything else, return some symbolic string."""

		if self.ndim == 0:
			# Scalar undarray.
			(mantissa_string, error_string, exponent_string) = \
					self.get_strings()
			return "(" + mantissa_string + " +- " + error_string + ")" + \
					exponent_string
		else:
			return "(%d-dimensional undarray with shape %s)" % \
					(self.ndim, self.value.shape)

	# No sensible repr(), because the object's interior is elaborate.

#
# Explicit operators ...
#

def add(a, b):
	if isinstance(b, undarray):
		return b.__rmul__(a)
	else:
		return a + b

def substract(a, b):
	if isinstance(b, undarray):
		return b.__rmul__(a)
	else:
		return a - b
