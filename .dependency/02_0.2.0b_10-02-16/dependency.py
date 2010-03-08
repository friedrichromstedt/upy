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
# File version: 0.2.0b

__all__ = ['Dependency']

"""Implements the abstract dependency of "something" on an error dispersion
with a derivative, identified by an error source name."""


class Dependency:
	"""A Dependency represents the dependence of something on error sources
	identified by an integer.  It also stores the accompanying derivatives
	and dispersions.  
	
	A Derivative can be added with another Derivative, 
	by using .add().  This is with the spirit of the += operator, but 
	returns what is left and could not be added because the error source names
	did not match. 
	
	Also, Derivatives can be multiplied with ndarrays, in this case the
	derivatives andarray will be multiplied with the operand.
	
	To find out what actual dispersion is induced by the Dependency, call
	.get_dispersion().  It calculates derivtive ** 2 * dispersion."""

	#
	# Initialisation methods ...
	#

	def __init__(self, names, derivatives, dispersions):
		"""Initialise the dependency on error sources NAMES of dispersion
		DISPERSIONS with derivatives DERIVATIVES.  All are supposed to be
		ndarrays of equal shape."""
		
		self.names = names
		self.derivatives = derivatives
		self.dispersions = dispersions

		self.shape = self.names.shape
		self.ndim = self.names.ndim

	def copy_names(self):
		"""Return a new Dependency with copied .names."""

		return Dependency(
				names = self.names.copy(),
				derivatives = self.derivatives,
				dispersions = self.dispersions)
	
	def is_empty(self):
		"""Return True if this Dependency can be discarded."""

		return not self.names.any()
	
	def is_nonempty(self):
		"""Return True if this Dependency cannot be discarded."""

		return self.names.any()

	#
	# Obtaining the dispersion ...
	#

	def get_dispersion(self):
		"""Get the dispersion induced by this dependency."""

		return (self.names != 0) * self.derivatives ** 2 * self.dispersions

	#
	# Arithmetics:  Binary arithmetics ...
	#

	def add(self, other):
		"""OTHER must be a Dependency instance of same shape.  Adds the 
		OTHER to self as far as possible, what is left and could not be 
		added is returned as new Dependency."""

		# Zero, create a copy of the other ...

		copy = other.copy_names()
		# Now, we can play with copy.names.

		# First, add on same name ...

		matching_mask = (self.names == copy.names)

		self.derivatives += matching_mask * copy.derivatives

		# Mark the cells as used.
		copy.names *= (1 - matching_mask)
		
		# Second, try to fill empty space ...
		#
		# Where there is empty space, there are zeros.

		empty_mask = (self.names == 0)

		other_filled_mask = (copy.names != 0)
		fillin_mask = empty_mask * other_filled_mask

		self.names += fillin_mask * copy.names
		self.derivatives += fillin_mask * copy.derivatives
		self.dispersions += fillin_mask * copy.dispersions

		# Ok, we're done so far ...

		return copy
	
	def __mul__(self, other):
		"""Multiply the dependency by some ndarray factor, i.e., scale the 
		derivative."""

		return Dependency(
				names = self.names,
				derivatives = self.derivatives * other,
				dispersions = self.dispersions)

	#
	# Arithmethics:  Reversed arithmetics ...
	#

	# __radd__() and __rsub__() are not needed, because always both operands
	# will be Dependency instances.

	def __rmul__(self, other):
		return Dependency(
				names = self.names,
				derivatives = other * self.derivatives,
				dispersions = self.dispersions)
	
	#
	# Augmented arithmetics will be emulated by using standard
	# arithmetics ...
	#

	#
	# Keying methods ...
	#
	
	def __getitem__(self, key):
		"""Returns the Dependency of the given subset applied to the
		derivatives and dispersions."""

		return Dependency(
				names = self.names[key],
				derivatives = self.derivatives[key],
				dispersions = self.dispersions[key])

	def clear(self, key):
		"""Clear the portion given by KEY, by setting the values stored to
		zero."""

		self.names[key] = 0
		self.derivatives[key] = 0
		self.dispersions[key] = 0

	def __len__(self):
		return self.shape[0]
	
	#
	# ndarray methods ...
	#

	def flatten(self, *flatten_args, **flatten_kwargs):
		"""Returns a copy with the Dependency's arrays flatten()'ed.  The
		arguments are handed over to the arrays' methods."""

		return Dependency(
				names = self.names.flatter(
					*flatten_args, **flatten_kwargs),
				derivatives = self.derivatives.flatten(
					*flatten_args, **flatten_kwargs),
				dispersions = self.dispersions.flatten(
					*flatten_args, **flatten_kwargs))

	def repeat(self, *repeat_args, **repeat_kwargs):
		"""Returns a copy with repeat()'ed arrays.  The arguments are handed 
		over to the arrays' methods."""

		return Dependency(
				names = self.names.repeat(
					*repeat_args, **repeat_kwargs),
				derivatives = self.derivatives.repeat(
					*repeat_args, **repeat_kwargs),
				dispersions = self.dispersions.repeat(
					*repeat_args, **repeat_kwargs))

	def reshape(self, *reshape_args):
		"""Returns a copy with reshape()'ed arrays.  The arguments are
		handed over to the arrays' methods.  numpy.reshape() takes no
		keyword arguments."""

		return Dependency(
				names = self.names.reshape(*reshape_args),
				derivatives = self.derivatives.reshape(*reshape_args),
				dispersions = self.dispersions.reshape(*reshape_args))

	def transpose(self, *transpose_args, **transpose_kwargs):
		"""Returns a copy with transpose()'ed arrays.  The arguments are
		handed over to the arrays' methods."""

		return Dependency(
				names = self.names.transpose(
					*transpose_args, **transpose_kwargs),
				derivatives = self.derivatives.transpose(
					*transpose_args, **transpose_kwargs),
				dispersions = self.dispersions.transpose(
					*transpose_args, **transpose_kwargs))

	#
	# Special array methods ...
	#

	def broadcasted(self, shape):
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
		the second via .repeat(count, axis = axis).
		
		This method acts on a copy."""

		# Check conditions ...

		if len(shape) < self.ndim:
			raise ValueError('Dependency with shape %s cannot be broadcast to shape %s.' % (self.shape, shape))

		if self.ndim != 0:
			# If the object is scalar, the expression wouldn't work.
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
