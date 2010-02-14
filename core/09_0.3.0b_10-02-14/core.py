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
# $Last changed: 2010 Feb 14$
# Developed since: Jan 2010
# File version: 0.3.0b

import numpy
import upy
import upy.decimal
import upy.dependency
import upy.characteristic

__all__ = ['undarray']

"""The central module, implementing the uncertain ndarray: undarray."""


class undarray:
	"""Implements uncertain ndarrays.  The name is derived from
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
			self.characteristic = upy.characteristic.Characteristic(
					shape = self.value.shape)

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
					derivative = numpy.ones(shape = self.value.shape),
					dispersion = sigma ** 2)

			self.characteristic = upy.characteristic.Characteristic(
					shape = self.value.shape)
			# Use as source name a package-scope unique ID.  "id_generator"
			# is an IDGenerator instance in package scope.
			self.characteristic.set_dependency(
					upy.id_generator.get_id(), 
					dependency)

		elif characteristic is not None:
			
			# Take over characteristic ...

			self.value = numpy.asarray(object, dtype = dtype)
			self.characteristic = characteristic
			
		else:

			# Construct an empty undarray ...

			self.value = numpy.asarray(object, dtype = dtype)
			self.characteristic = upy.characteristic.Characteristic(
					shape = self.value.shape)
		
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

		exponent_value = upy.decimal.get_exponent(self.value)
		exponent_error = upy.decimal.get_exponent(self.error())
		return exponent_value - exponent_error + 1

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
				exponent = upy.decimal.get_exponent(error)
		else:
			# Value determined exponent also.
			exponent_value = upy.decimal.get_exponent(self.value)
			if error == 0.0:
				# Error zero, su use value's exponent.
				exponent = exponent_value
			else:
				# Determine the maximum of both exponents.
				exponent_error = upy.decimal.get_exponent(error)
				exponent = max(exponent_value, exponent_error)

		# Scale the values such that the exponent's digit is just before
		# the dot.
		value_scaled = self.value * 10 ** (-exponent)
		error_scaled = error * 10 ** (-exponent)
		
		# The error determines the accuracy.
		error_scaled_exponent = upy.decimal.get_exponent(error_scaled)
		if error_scaled_exponent == upy.decimal.Infinity:
			# Use some large fallback value as an approximation of
			# infinite precision.
			error_scaled_exponent = -16  # 15 post-dot digits.

		# Obtain the value's mantissa string.
		mantissa_string = upy.decimal.get_rounded(
				value_scaled,
				error_scaled_exponent - 1)

		# Obtain the error's mantissa string, ceil()'ed.
		error_string = upy.decimal.get_rounded(
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

	# No sensible repr(), because the object's interior is complex.
