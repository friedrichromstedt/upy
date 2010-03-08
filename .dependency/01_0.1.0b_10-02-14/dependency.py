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

__all__ = ['Dependency']

"""Implements the abstract dependency of "something" on an error dispersion
with a derivative."""


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
