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
# $Last changed: 2010 Feb 24$
# Developed since: Jan 2010
# File version: 0.3.6b

import numpy
import upy
import upy.dependency
import upy.characteristic
import upy.printable

__all__ = ['undarray']

"""The central module, implementing the uncertain ndarray: undarray."""


class undarray:
	"""Implements uncertain ndarrays.  The name is derived from
	numpy.ndarray.  Read-ony attributes:
		
	.value - The plain nominal value of the undarray."""

	def __init__(self,
			object = None,
			error = None, sigma = None, 
			derivatives = None,
			characteristic = None,
			dtype = None,
			shape = None):
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
		the dtype of the undarray (value & sigma) by DTYPE.  If DTYPE is None,
		use numpy's default as the dtype of the uncertainty data, not the 
		dtype derived from OBJECT.  If OBJECT is None, SHAPE will be used to
		be passed to numpy.zeros(), and and empty error source dependency will 
		be stored in the beginning.  In all other cases, SHAPE is ignored."""
		
		if isinstance(object, undarray):

			# Take over attributes from existing undarray ...
		
			self.value = object.value
			self.characteristic = object.characteristic

		elif derivatives is not None:

			# Derive the new undarray from known ones ...

			self.value = numpy.asarray(object, dtype = dtype)

			# Create a new, empty Characteristic where we can fill in
			# the dependencies introduced by the dictionary DERIVATIVES.
			self.characteristic = upy.characteristic.Characteristic(
					shape = self.value.shape,
					dtype = dtype)

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
			dependency = upy.dependency.Dependency(
					names = upy.id_generator.get_id(
						shape = self.value.shape),
					derivatives = numpy.ones(shape = self.value.shape),
					dispersions = sigma ** 2)

			self.characteristic = upy.characteristic.Characteristic(
					shape = self.value.shape,
					dtype = dtype)
			self.characteristic.append(dependency)

		elif characteristic is not None:
			
			# Take over characteristic ...

			self.value = numpy.asarray(object, dtype = dtype)
			self.characteristic = characteristic

		elif object is not None:

			# Initialise from list-like structure or scalar number ...

			# Determine the shape.
			shapeobject = object
			shape = []
			# Indice the shapeobject until a scalar or and undarray is
			# reached:
			while True:
				if isinstance(shapeobject, undarray):
					# Finish shape:
					shape += list(shapeobject.shape)
					break
				else:
					# Try to indice, whathever the object is:
					try:
						indiced = shapeobject[0]
					except:
						# TypeError: unsubscriptable object, or
						# IndexError: invalid index to scalar variable, or
						# IndexError: 0-d arrays can't be indexed, or
						# ...
						# We reached the scalar level.  Shape finished.
						break
					# Indicing was successful, continue.
					shape.append(len(shapeobject))
					shapeobject = indiced

			# Initialise the attributes.
			self.value = numpy.zeros(shape, dtype = dtype)
			self.characteristic = upy.characteristic.Characteristic(
					shape = shape,
					dtype = dtype)

			# Provide .shape and .ndim, because __setitem__() need it.
			self.shape = shape
			self.ndim = len(shape)

			# Fill in the given values.
			# 
			# This will recurse into the OBJECT.
			self[()] = object

		elif object is not None:

			# Construct an exact undarray from OBJECT ...

			self.value = numpy.asarray(object, dtype = dtype)
			self.characteristic = upy.characteristic.Characteristic(
					shape = self.value.shape,
					dtype = dtype)

		elif shape is not None:

			# Construct an empty undarray ...

			self.value = numpy.zeros(shape, dtype = dtype)
			self.characteristic = upy.characteristic.Characteristic(
					shape = shape,
					dtype = dtype)

		else:
			
			raise ValueError("Don't know how to initialise an undarray from the arguments given.")
		
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
		inversion_mask -= 2 * (self.value < 0)

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
		to be an undarray."""

		# Handle scalar indices ...

		if not isinstance(key, tuple):
			key = (key,)
		
		# Update with a undarray subset ...

		if isinstance(value, undarray):

			# Update the respective subsets ...

			self.value[key] = value.value
			self.characteristic[key] = value.characteristic
		
		# Update in mixed-mode ...

		else:

			if len(key) == len(self.shape):

				# We have reached the innermost level, set the values ...
				#
				# VALUE is definitely not an undarray.

				self.value[key] = value
				self.characteristic.clear(key)

			else:
					
				# VALUE is definitely not an undarray.  Iterate through
				# VALUE ...

				# Check length.
				if len(value) != self.shape[len(key)]:
					raise ValueError('Shape mismatch.')

				# Iterate.
				for idx in xrange(0, len(value)):
					subkey = tuple(list(key) + [idx])
					self[subkey] = value[idx]
		
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
					new_shape = object.shape,
					*flatten_args, **flatten_kwargs))

	def repeat(self, *repeat_args, **repeat_kwargs):
		"""Returns a copy with repeat()'ed arrays."""

		object = self.value.repeat(
				*repeat_args, **repeat_kwargs)
		return undarray(
				object = object,
				characteristic = self.characteristic.repeat(
					new_shape = object.shape,
					*repeat_args, **repeat_kwargs))

	def reshape(self, *reshape_args, **reshape_kwargs):
		"""Returns a copy with reshape()'ed arrays."""

		object = self.value.reshape(
				*reshape_args, **reshape_kwargs)
		return undarray(
				object = object,
				characteristic = self.characteristic.reshape(
					new_shape = object.shape,
					*reshape_args, **reshape_kwargs))

	def transpose(self, *transpose_args, **transpose_kwargs):
		"""Returns a copy with transpos()'ed arrays."""

		object = self.value.transpose(
				*transpose_args, **transpose_kwargs)
		return undarray(
				object = object,
				characteristic = self.characteristic.transpose(
					new_shape = object.shape,
					*transpose_args, **transpose_kwargs))

	#
	# String conversion ...
	#
	
	def printable(self, sigmas = None,
			enforce_sign_value = None, enforce_sign_exponent = None,
			format = None,
			precision = None, infinite_precision = None):
		"""Return a printable object created from this undarray instance.
		SIGMA sigmas will be displayed as uncertainty (default 2).  To
		enforce the printing of optional '+' signs in the value and the
		exponent, use ENFORCE_SIGN_VALUE and ENFORCE_SIGN_EXPONENT.  The two
		FORMATS supported are 'float', e.g. "0.120 +- 0.034", and 'exp', e.g.
		"(1.20 +- 0.34) 10^-1".  Default is 'exp'.  PRECISION influences the 
		precision of the output.  Generally, the precision is determined from 
		the uncertainty.  With PRECISION = 1, the output will look like 
		(1.0 +- 0.3), with PRECISION = 2, like (1.00 +- 0.23).  If the 
		uncertainty is zero, INFINITE_PRECISION will be used instead, giving 
		the number of digits after the point, either in float or exp mode.  
		If also the value is zero, only (0 +- 0) will be printed.  The default 
		PRECISION is 2.  Note that you can affect the way the array is printed 
		also by calling numpy.set_printoptions()."""

		return upy.printable.PrintableUndarray(self,
				sigmas = sigmas,
				enforce_sign_value = enforce_sign_value,
				enforce_sign_exponent = enforce_sign_exponent,
				format = format,
				precision = precision,
				infinite_precision = infinite_precision)

	def __str__(self):
		"""For scalar undarrays, return a useful print value of the value
		and the error.  For everything else, return some symbolic string."""

		return str(self.printable())

	# No sensible repr(), because the object's interior is complex.
