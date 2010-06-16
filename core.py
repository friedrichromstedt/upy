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

# Developed since: Jan 2010

import numpy
import upy
import upy.dependency
import upy.characteristic
import upy.printable

__all__ = ['undarray']

"""The central module, implementing the uncertain ndarray: undarray."""


def ravel(object):
	"""Ravel a mixed-mode initialisation argument.  undarray instances
	contained will ravel to their raveled .values."""

	if isinstance(object, undarray):
		
		# Return the raveled version of object.value ...
		#
		# This is done beause *all* elements of object.value may contribute
		# to the dtype.  E.g., when dtype = numpy.object, this may occur 
		# because the first element is an non-numeric type, or the second, ...

		return object.value.flatten().tolist()

	elif numpy.isscalar(object) or \
			(isinstance(object, numpy.ndarray) and \
			 object.shape == ()):

		# Scalars are already raveled ...

		return [object]

	else:

		# Sequence objects must be recursed ...

		raveled = []

		for element in object:
			raveled.extend(ravel(element))

		return raveled


class undarray:
	"""Implements uncertain ndarrays.  The name is derived from
	numpy.ndarray.  Read-ony attributes:
		
	.value - The plain nominal value of the undarray."""

	def __init__(self,
			object = None,
			uncertainty = None,
			derivatives = None,
			characteristic = None,
			dtype = None,
			shape = None,
			sigmas = None):
		"""If OBJECT is an undarray, its content will not be copied.  (This 
		initialisation scheme is intendend to make shure that some object is 
		an undarray.)
		
		If DERIVATIVES and OBJECT are not None, DERIVATIVES must be a list 
		[(undarray instance: derivative), ...], giving the derivatives with 
		that the new undarray depends on the key undarrays.  OBJECT will be 
		converted to an numpy.ndarray.

		If UNCERTAINTY and OBJECT aren't None, OBJECT and UNCERTAINTY will be 
		converted to numpy.ndarrays.  SIGMAS tells how many sigmas the 
		UNCERTAINTY covers.  The default for SIGMAS is 2.0.  SIGMAS will be 
		converted by float().

		If CHARACTERISTIC and OBJECT are not None, OBJECT is converted to an 
		numpy.ndarray, and the CHARACTERISTIC is used directly without copying.

		If OBJECT isn't None, but all other branches mentioned so far are not
		fulfilled, Mixed-Mode applies.  In this mode, OBJECT will not be 
		converted to an numpy.ndarray, but will be recursed into.  
		Nevertheless the objects comprising OBJECT must match the effective
		shape of the OBJECT.  OBJECT may be contain upy.undarrays.  The shape 
		of the new undarray is obtained from the first scalar element in the 
		upy.ravel()ed version of the OBJECT and from the lengthes of the 
		sequences containing that first element.  Scalars are objects for 
		which numpy.isscalar() returns True.  When there are shape 
		inconsistencies, an exception will occur.  If the first element is an 
		undarray, its shape will be taken into account.  In Mixed-Mode, the 
		DTYPE of the initially zero .value ndarray is either determined 
		automatically from all values contained in OBJECT and undarrays 
		therein, or can be given explicitly via DTYPE.  It is strongly 
		recommended to use DTYPE, because raveling large datasets can be very 
		expensive in memory and time both.
		
		If also OBJECT is None, SHAPE is taken into account, to create a new,
		zero-valued undarray of dtype DTYPE (None means numyp.float).
		
		If none of these branches match, ValueError will be raised."""
		
		if sigmas is None:
			sigmas = 2.0

		if isinstance(object, undarray):

			# Take over attributes from existing undarray ...
		
			self.value = object.value
			self.characteristic = object.characteristic

		elif derivatives is not None and object is not None:

			# Derive the new undarray from known ones ...

			self.value = numpy.asarray(object)

			# Create a new, empty Characteristic where we can fill in
			# the dependencies introduced by the dictionary DERIVATIVES.
			self.characteristic = upy.characteristic.Characteristic(
					shape = self.value.shape)

			# Fill in the dependencies.
			for (instance, derivative) in derivatives:
				self.characteristic += \
						instance.characteristic * derivative

		elif uncertainty is not None and object is not None:
			
			# Constuct a new undarray ...

			self.value = numpy.asarray(object)
			
			# Calculate standard deviation.
			sigma = numpy.asarray(uncertainty) / float(sigmas)

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
					shape = self.value.shape)
			self.characteristic.append(dependency)

		elif characteristic is not None and object is not None:
			
			# Take over characteristic ...

			self.value = numpy.asarray(object)
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
				elif numpy.isscalar(shapeobject):
					# We reached the scalar level.  Shape finished.
					break
				else:
					# Test for scalar array.
					if isinstance(shapeobject, numpy.ndarray) and \
							shapeobject.shape == ():
						# In fact, it's scalar:
						break
					else:
						# It's not a scalar array, indicing possible:
						shape.append(len(shapeobject))
						shapeobject = shapeobject[0]

			# Initialise the attributes.

			# If dtype is None, infer dtype from raveled OBJECT:
			if dtype is None:
				dtype = numpy.asarray(ravel(object)).dtype

			# Initialise .value and .characteristic:
			self.value = numpy.zeros(shape, dtype = dtype)
			self.characteristic = upy.characteristic.Characteristic(
					shape = tuple(shape))

			# Provide .shape and .ndim, because __setitem__() need it.
			self.shape = shape
			self.ndim = len(shape)

			# Fill in the given values.
			# 
			# This will recurse into the OBJECT.
			self[()] = object

		elif shape is not None:

			# Construct an empty undarray ...

			if not isinstance(shape, tuple):
				raise ValueError("SHAPE must be tuple.")

			self.value = numpy.zeros(shape, dtype = dtype)
			self.characteristic = upy.characteristic.Characteristic(
					shape = tuple(shape))

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
	
	def stddev(self):
		"""Returns the standard deviation."""

		return self.sigma()

	def error(self):
		"""Returns the error, i.e., 2 * sigma."""

		return 2 * self.sigma()
	
	def uncertainty(self, sigmas):
		"""Returns SIGMAS * (standard deviation)."""

		return sigmas * self.sigma()

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
		
		SIGMA sigmas will be displayed as uncertainty (default 2).  
		
		To enforce the printing of optional '+' signs in the value and the
		exponent, use ENFORCE_SIGN_VALUE and ENFORCE_SIGN_EXPONENT.  
		
		The three FORMATS supported are 'float', e.g. 0.120 +- 0.034, 'exp', 
		e.g.  (1.20 +- 0.34) 10^-1, and 'int', e.g. 12300 +- 4500.  By default,
		the format will be determined from the values and the uncertainties.
		The 'int' mode is choosen upon integer type of values and 
		uncertainties.  If the uncertainty is all-zero, the printing mode will 
		be determined from the value alone, else both must be integer to 
		enable int printing mode.

		PRECISION influences the precision of the output.  Generally, the 
		precision is determined from the uncertainty.  With PRECISION = 1, the 
		output will look like (1.0 +- 0.3), with PRECISION = 2, like 
		(1.00 +- 0.23).  If the uncertainty is zero, INFINITE_PRECISION will 
		be used instead, giving the number of digits behind the point, either 
		in float or exp mode.  In int mode all post-point digits are 
		suppressed.  If both the value and the uncertainty are zero, only 
		(0 +- 0) is printed.  The default PRECISION is 2.
		
		Note that you can affect the way the array is printed also by calling 
		numpy.set_printoptions()."""

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
