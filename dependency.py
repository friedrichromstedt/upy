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

import numpy

__all__ = ['Dependency']

"""Implements the abstract dependency of "something" on an error variance
with a derivative, identified by an error source name."""


class Dependency:
	"""A Dependency represents the dependence of something on error sources
	identified by an integer.  It also stores the accompanying derivatives
	and variances.  
	
	A Derivative can be added with another Derivative, 
	by using .add().  This is with the spirit of the += operator, but 
	returns what is left and could not be added because the error source names
	did not match. 
	
	Also, Derivatives can be multiplied with ndarrays, in this case the
	derivatives andarray will be multiplied with the operand.
	
	To find out what actual variance is induced by the Dependency, call
	.get_variance().  It calculates derivative ** 2 * variance."""

	#
	# Initialisation methods ...
	#

	def __init__(self, names = None, derivatives = None, variances = None,
			shape = None):
		"""Initialise the dependency on error sources NAMES of variances
		VARIANCES with derivatives DERIVATIVES.  All are supposed to be
		ndarrays of equal shape.  As an alternative, everything can be left 
		out when specifying SHAPE.  In this case, an empty Dependency 
		containing numpy.ndarrays of dtype = None [float] will be created."""

		if shape is None:
			
			self.names = names
			self.derivatives = derivatives
			self.variances = variances

			self.shape = self.names.shape
			self.ndim = self.names.ndim

		else:

			self.names = numpy.zeros(shape, dtype = numpy.int)
			self.derivatives = numpy.zeros(shape)
			self.variances = numpy.zeros(shape)

			self.shape = shape
			self.ndim = len(shape)

	def copy_names(self):
		"""Return a new Dependency with copied .names."""

		return Dependency(
				names = self.names.copy(),
				derivatives = self.derivatives,
				variances = self.variances)
	
	def is_empty(self):
		"""Return True if this Dependency can be discarded."""

		return not self.names.any()
	
	def is_nonempty(self):
		"""Return True if this Dependency cannot be discarded."""

		return self.names.any()

	#
	# Obtaining the variances ...
	#

	def get_variance(self):
		"""Get the variance induced by this dependency."""

		return (self.names != 0) * self.derivatives ** 2 * self.variances

	#
	# Arithmetics:  Binary arithmetics ...
	#

	def add(self, other, key = None):
		"""OTHER must be a Dependency instance of same shape.  Adds the 
		OTHER to self as far as possible, what is left and could not be 
		added is returned as new Dependency.  If KEY is given, it specifies
		the portion of self where the OTHER applies.  If KEY is given, it 
		must be a tuple or a scalar."""
		
		if key is None:
			# Indice everything.
			key = ()

		# Zero, create a copy of the other ...

		copy = other.copy_names()
		# Now, we can play with copy.names.

		# First, add on same name ...

		matching_mask = (self.names[key] == copy.names)

		self.derivatives[key] += matching_mask * copy.derivatives

		# Mark the cells as used.
		copy.names *= (1 - matching_mask)
		
		# Second, try to fill empty space ...
		#
		# Where there is empty space, there are zeros.

		empty_mask = (self.names[key] == 0)

		other_filled_mask = (copy.names != 0)
		fillin_mask = empty_mask * other_filled_mask

		self.names[key] += fillin_mask * copy.names
		self.derivatives[key] += fillin_mask * copy.derivatives
		self.variances[key] += fillin_mask * copy.variances

		# Mark the cells as used.
		copy.names *= (1 - fillin_mask)

		# Ok, we're done so far ...

		return copy
	
	def __mul__(self, other):
		"""Multiply the dependency by some ndarray factor, i.e., scale the 
		derivative."""

		return Dependency(
				names = self.names,
				derivatives = self.derivatives * other,
				variances = self.variances)

	#
	# Arithmethics:  Reversed arithmetics ...
	#

	# __radd__() and __rsub__() are not needed, because always both operands
	# will be Dependency instances.

	def __rmul__(self, other):
		return Dependency(
				names = self.names,
				derivatives = other * self.derivatives,
				variances = self.variances)
	
	#
	# Augmented arithmetics will be emulated by using standard
	# arithmetics ...
	#

	#
	# Keying methods ...
	#
	
	def __getitem__(self, key):
		"""Returns the Dependency of the given subset applied to the
		derivatives and variances."""
		
		return Dependency(
				names = self.names[key],
				derivatives = self.derivatives[key],
				variances = self.variances[key])

	def clear(self, key):
		"""Clear the portion given by KEY, by setting the values stored to
		zero."""

		self.names[key] = 0
		self.derivatives[key] = 0
		self.variances[key] = 0

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
				variances = self.variances.flatten(
					*flatten_args, **flatten_kwargs))

	def repeat(self, *repeat_args, **repeat_kwargs):
		"""Returns a copy with repeat()'ed arrays.  The arguments are handed 
		over to the arrays' methods."""

		return Dependency(
				names = self.names.repeat(
					*repeat_args, **repeat_kwargs),
				derivatives = self.derivatives.repeat(
					*repeat_args, **repeat_kwargs),
				variances = self.variances.repeat(
					*repeat_args, **repeat_kwargs))

	def reshape(self, *reshape_args):
		"""Returns a copy with reshape()'ed arrays.  The arguments are
		handed over to the arrays' methods.  numpy.reshape() takes no
		keyword arguments."""

		return Dependency(
				names = self.names.reshape(*reshape_args),
				derivatives = self.derivatives.reshape(*reshape_args),
				variances = self.variances.reshape(*reshape_args))

	def transpose(self, *transpose_args, **transpose_kwargs):
		"""Returns a copy with transpose()'ed arrays.  The arguments are
		handed over to the arrays' methods."""

		return Dependency(
				names = self.names.transpose(
					*transpose_args, **transpose_kwargs),
				derivatives = self.derivatives.transpose(
					*transpose_args, **transpose_kwargs),
				variances = self.variances.transpose(
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

			return "(names = %d, derivatives = %e, variances = %e)" % \
					(self.names, self.derivatives, self.variances)
		else:

			# Return an array representation ...

			return "(names:\n%s\nderivatives:\n%s,\nvariances:\n%s\n)" % \
					(self.names, self.derivatives, self.variances)

	# There seems to be no sensible __repr__().
