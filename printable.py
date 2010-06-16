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
import upy.decimal2


class PrintableElement:
	"""An element of an PrintableUndarray.  Modify the .width_* attrs of
	.dn_value, .dn_uncertainty and .dn_exponent in order to make the instance
	print nicely."""

	def __init__(self, value, uncertainty,
			enforce_sign_value = None, enforce_sign_exponent = None,
			conversion_reporter = None,
			format = None,
			precision = None, infinite_precision = None):
		"""VALUE is the nominal value, UNCERTAINTY a value proportional to
		the standard deviation.  The proportionality factor depends on what
		the user intends to print.  
		
		To enforce the printing of optional '+' signs in the value and the
		exponent, use ENFORCE_SIGN_VALUE and ENFORCE_SIGN_EXPONENT.  
		
		The three FORMATS supported are 'float', e.g. 0.120 +- 0.034, 'exp', 
		e.g.  (1.20 +- 0.34) 10^-1, and 'int', e.g. 12300 +- 4500.  By default,
		the format will be determined from the values and the uncertainties.
		The 'int' mode is choosen upon integer type of values and 
		uncertainties.  If the uncertainty of a value is zero, the printing
		mode will be determined from the value alone, else both must be integer
		to enable int printing mode.

		PRECISION influences the precision of the output.  Generally, the 
		precision is determined from the uncertainty.  With PRECISION = 1, the 
		output will look like (1.0 +- 0.3), with PRECISION = 2, like 
		(1.00 +- 0.23).  If the uncertainty is zero, INFINITE_PRECISION will 
		be used instead, giving the number of digits beind the point, either 
		in float or exp mode.  In int mode all post-point digits are 
		suppressed.  If both the value and the uncertainty are zero, only 
		(0 +- 0) is printed.  The default PRECISION is 2."""

		# Other than in upy.decimal2, positive precisions indice digits
		# /behind/ the point (not before the point).
		
		# Convert VALUE and UNCERTAINTY to numpy ...

		value = numpy.asarray(value)
		uncertainty = numpy.asarray(uncertainty)

		# Autodetermine FORMAT ...

		if format is None:
			if uncertainty != 0:
				# Consider VALUE, and also consider UNCERTAINTY.
				if value.dtype.kind in 'iu' and uncertainty.dtype.kind in 'iu':
					format = 'int'
				else:
					format = 'exp'
			else:
				# Do only consider VALUE.
				if value.dtype.kind in 'iu':
					format = 'int'
				else:
					format = 'exp'

		# Autodetermine precision ...

		if precision is None:
			precision = 2

		# Autodetermine infinite precision ...

		if infinite_precision is not None:
			# Use in initialisation the convention of upy.decimal2, that
			# digits behind the point have negative indices.
			infinite_precision = -infinite_precision
		
		# Store variables ...

		self.value = value
		self.uncertainty = uncertainty
		self.conversion_reporter = conversion_reporter
		self.format = format

		# Find out intrinsic parameters ...

		self.dn_value = upy.decimal2.DecimalNumber(self.value,
				enforce_sign = enforce_sign_value,
				infinite_precision = infinite_precision)
		self.dn_uncertainty = upy.decimal2.DecimalNumber(self.uncertainty,
				ceil = True,
				infinite_precision = infinite_precision)

		self.strings_value = self.dn_value.get_strings()
		self.strings_uncertainty = self.dn_uncertainty.get_strings()

		self.leftmost_digit_value = self.dn_value.get_leftmost_digit()
		self.leftmost_digit_uncertainty = self.dn_uncertainty.\
				get_leftmost_digit()

		if self.format == 'exp':

			# Determine exponent and precision ...

			if self.leftmost_digit_value.infinite:
				# Choose the exponent such that the uncertainty prints nicely.
				if self.leftmost_digit_uncertainty.infinite:
					# Exponent doesn't matter.
					self.exponent = 0 
					
					# Signal that it's exactly zero by printing (0 +- 0).
					self.precision = 0
				else:
					self.exponent = self.leftmost_digit_uncertainty.z

					# Only print (0.0 +- 1.2) for PRECISION = 2.
					self.precision = -(precision - 1)

			else:
				# Choose the exponent such that the value prints nicely.
				self.exponent = self.leftmost_digit_value.z

				if self.leftmost_digit_uncertainty.infinite:
					# Use default value:
					self.precision = None
				
				else:
					# Print (1.234 +- 0.012) for PRECISION = 2.
					#
					# The position of the leftmost digit of .uncertainty with 
					# the .exponent taken into account is self.\
					# leftmost_digit_uncertainty.z - self.exponent.  
					self.precision = -(precision - 1) + \
							(self.leftmost_digit_uncertainty.z - \
							self.exponent)

		elif self.format == 'float':
			
			# Simply skip the exponent ...

			self.exponent = 0

			# Determine the precision ...

			# Choose the precision such that the uncertainty prints nicely.
			if self.leftmost_digit_uncertainty.infinite:
				# Precision not limited.
				if self.leftmost_digit_value.infinite:
					# Signal that value is completely zero, print simply 
					# 0 +- 0:
					self.precision = 0
				else:
					# Print 0.123456789012345 +- 0.000000000000000:
					self.precision = None
			else:
				# Print (0.000 +- 0.012) for PRECISION = 2:
				self.precision = -(precision - 1) + \
						self.leftmost_digit_uncertainty.z

		elif self.format == 'int':

			# Simply skip the exponent ...

			self.exponent = 0

			# Determine precision ...

			# Choose the precision such that the uncertainty prints nicely.
			if self.leftmost_digit_uncertainty.infinite:
				# Precision unlimited.
				#
				# self.leftmost_digit_value may be finite or infinite.  In the
				# infinite case, we print up to precision 0.  In the finite 
				# case, we also do so (it's an integer we're printing).
				self.precision = 0
			else:
				# Print (12300 +- 4500) for PRECISION = 2, but limit the
				# .precision to 0, i.e., print 0 +- 1 instead of 0.0 +- 1.0.

				# Attempt the float value:
				self.precision = -(precision - 1) + \
						self.leftmost_digit_uncertainty.z

				# Correct it if it's negative:
				self.precision = max(0, self.precision)

		else:

			raise ValueError('Unknown format "%s".' % format)

		self.dn_exponent = upy.decimal2.DecimalNumber(self.exponent,
				precision = 0, enforce_sign = enforce_sign_exponent)

		# Fill in the intrinsic parameters ...

		self.dn_value.set_exponent(self.exponent)
		self.dn_uncertainty.set_exponent(self.exponent)
		
		self.dn_value.set_precision(self.precision)
		self.dn_uncertainty.set_precision(self.precision)

	def __str__(self):
		"""Note that the return value ends on a whitespace, to make the
		space between elements in array printing two spaces wide."""

		strings_value = self.dn_value.get_strings()
		strings_uncertainty = self.dn_uncertainty.get_strings()
		strings_exponent = self.dn_exponent.get_strings()

		if self.conversion_reporter is not None:
			self.conversion_reporter(strings_value, strings_uncertainty,
					strings_exponent)
			
		# Add a space as additional spacer when printing arrays ...

		if self.format == 'exp':
			# Exponential float format.
			return '(' + str(strings_value) + ' +- ' + \
					str(strings_uncertainty) + \
					') 10^' + str(strings_exponent) + ' '

		else:
			# Format 'float' or 'int'.
			return str(strings_value) + ' +- ' + str(strings_uncertainty) + ' '


class Widths:
	def __init__(self):
		"""Initialise to zero."""

		self.width_left = 0
		self.width_point = 0
		self.width_right = 0

	def report(self, strings):
		"""Report a upy.decimal2.DecimalStrings instance to be printed."""

		self.width_left = max(self.width_left, len(strings.str_left))
		self.width_point = max(self.width_point, len(strings.str_point))
		self.width_right = max(self.width_right, len(strings.str_right))

	def apply_to(self, decimal_number):
		"""Apply this widths to a upy.decimal2.DecimalNumber DECIMAL_NUMBER."""

		decimal_number.width_left = self.width_left
		decimal_number.width_point = self.width_point
		decimal_number.width_right = self.width_right


class PrintableUndarray:
	"""Prints an undarray.  To print subportions, use __getattr__()."""

	def __init__(self, undarray = None,
			sigmas = None,
			enforce_sign_value = None, enforce_sign_exponent = None,
			format = None,
			precision = None, infinite_precision = None):
		"""Print undarray UNDARRAY or printable array PRINTABLE_ARRAY by 
		giving SIGMAS standard deviations as uncertainty.  
		
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
		be used instead, giving the number of digits beind the point, either 
		in float or exp mode.  In int mode all post-point digits are 
		suppressed.  If both the value and the uncertainty are zero, only 
		(0 +- 0) is printed.  The default PRECISION is 2.
		
		Note that you can affect the way the array is printed also by calling 
		numpy.set_printoptions()."""
		
		if sigmas is None:
			sigmas = 2
		
		# Autodetermine FORMAT ...

		if format is None:
			sigma = undarray.sigma()
			uncertainty = sigma * sigmas  # SIGMAS may be zero.
			if (uncertainty != 0).any():
				# Consider value, and also consider uncertainty.
				if undarray.value.dtype.kind in 'iu' and \
						sigma.dtype.kind in 'iu':
					format = 'int'
				else:
					format = 'exp'
			else:
				# Do only consider value.
				if undarray.value.dtype.kind in 'iu':
					format = 'int'
				else:
					format = 'exp'

		# Store attributes ...

		self.sigmas = sigmas
		self.enforce_sign_value = enforce_sign_value
		self.enforce_sign_exponent = enforce_sign_exponent
		self.format = format
		self.precision = precision
		self.infinite_precision = infinite_precision
		self.undarray = undarray

		# Load from UNDARRAY ...

		self.printable_array = numpy.zeros(shape = undarray.shape,
				dtype = numpy.object)
		self.shape = undarray.shape
		self.ndim = undarray.ndim

		# Put in the values ...

		self[()] = undarray

	def report_strings(self,
			strings_value, strings_uncertainty, strings_exponent):

		self.widths_value.report(strings_value)
		self.widths_uncertainty.report(strings_uncertainty)
		self.widths_exponent.report(strings_exponent)

	#
	# Item access ...
	#

	def __getitem__(self, key):
		"""Return a portion of self."""

		return PrintableUndarray(
				undarray = self.undarray[key],
				sigmas = self.sigmas,
				enforce_sign_value = self.enforce_sign_value,
				enforce_sign_exponent = self.enforce_sign_exponent)

	def __setitem__(self, key, value):
		"""Set a portion KEY of self to undarray VALUE."""

		# Allow for scalar indices.
		if not isinstance(key, tuple):
			key = (key,)

		if len(key) == self.ndim:

			# Final level reached.
			self.printable_array[key] = PrintableElement(
					value.value, self.sigmas * value.sigma(),
					enforce_sign_value = self.enforce_sign_value,
					enforce_sign_exponent = self.enforce_sign_exponent,
					conversion_reporter = self.report_strings,
					format = self.format,
					precision = self.precision,
					infinite_precision = self.infinite_precision)
		
		else:

			# Iterate.
			for idx in xrange(0, self.shape[len(key)]):
				new_key = tuple(list(key) + [idx])
				self[new_key] = value[idx]
		
	def __len__(self):
		return len(self.printable_array)
	
	#
	# String conversion ...
	#
		
	def _apply_widths(self, key,
			widths_value, widths_uncertainty, widths_exponent):
		"""Apply the widths WIDTHS_* to all elements."""

		if len(key) == self.ndim:
			
			# Final level reached.
			widths_value.apply_to(self.printable_array[key].\
					dn_value)
			widths_uncertainty.apply_to(self.printable_array[key].\
					dn_uncertainty)
			widths_exponent.apply_to(self.printable_array[key].\
					dn_exponent)
		
		else:

			# Iterate.
			for idx in xrange(0, self.shape[len(key)]):
				new_key = tuple(list(key) + [idx])
				self._apply_widths(new_key,
						widths_value, widths_uncertainty, widths_exponent)

	
	def __str__(self):
		"""First, simulate the conversion, thereby reporting all used elements
		to .widths_*.  Not all elements may be printed because of ellipsis.
		Then, apply the found maximum widths to self, and print the array."""

		# Set the minimum widths ...

		self.widths_value = Widths()
		self.widths_uncertainty = Widths()
		self.widths_exponent = Widths()

		# First, simulate and report the widths ...

		str(self.printable_array)

		# Now, apply the widths ...

		self._apply_widths(key = (),
				widths_value = self.widths_value,
				widths_uncertainty = self.widths_uncertainty,
				widths_exponent = self.widths_exponent)
		
		# Now, as the elements are synchronised, build the final string ...

		return str(self.printable_array)
