# Developed since: Feb 2010

import numpy

__all__ = ['Dependency']

"""Implements the abstract dependency of "something" on an error variance
with a derivative, identified by an error source name."""


class Dependency:
    """A Dependency represents the dependence of something on normalised error 
    sources identified by an integer.  It also stores the accompanying 
    derivatives.  The variances are unity.
    
    Derivatives can be multiplied with ndarrays, in this case the derivatives 
    ndarray will be multiplied with the operand.
    
    The variance is (derivative.real ** 2)"""

    #
    # Initialisation methods ...
    #

    def __init__(self, names = None, derivatives = None, shape = None):
        """Initialise the dependency on error sources *names* of unity 
        variances with derivatives *derivatives*.  Both are supposed to be
        ndarrays of equal shape.  As an alternative, everything can be left 
        out when specifying *shape*.  In this case, an empty Dependency 
        containing numpy.ndarrays of dtype=None [float] will be created."""

        if shape is None:

            assert(names.shape == derivatives.shape)
            
            self._names = names
            self._derivatives = derivatives

            self.shape = self.names.shape
            self.ndim = self.names.ndim

        else:

            self._names = numpy.zeros(shape, dtype=numpy.int)
            self._derivatives = numpy.zeros(shape)

            self.shape = shape
            self.ndim = len(shape)

    def copy_names(self):
        """Return a new Dependency with copied .names."""

        return Dependency(
                names = self._names.copy(),
                derivatives = self._derivatives)
    
    def is_empty(self):
        """Return True if this Dependency can be discarded."""

        return not self._names.any()
    
    def is_nonempty(self):
        """Return True if this Dependency cannot be discarded."""

        return self._names.any()

    #
    # Obtaining the variances ...
    #

    @property
    def variance(self):
        """Get the variance induced by this dependency."""

        if numpy.iscomplexbj(self._derivatives):
            raise ValueError("The variance of complex-valued "
                "Dependencies is ambiguous.")
        return (self._names != 0) * self._derivatives ** 2
    
    @property
    def real(self):
        """ Returns the real part of this Dependency. """

        return Dependency(
            names=self._names,
            derivatives=self._derivatives.real,
        )

    @property
    def imag(self):
        """ Returns the imaginary part of this Dependency. """
        
        return Dependency(
            names=self._names,
            derivatives=self._derivatives.imag,
        )

    #
    # Arithmetics:  Binary arithmetics ...
    #

    def add(self, other, key = None):
        """OTHER must be a Dependency instance of same shape.  Adds the 
        OTHER to self as far as possible, what is left and could not be 
        added is returned as new Dependency.  If KEY is given, it specifies
        the portion of self where the OTHER applies.  If KEY is given, it 
        must be a tuple or a scalar.
        
        ``self.derivatives`` might be replaced by a version with
        another dtype if the dtypes of the derivatives of *self* and
        *other* differ."""

        if key is None:
            # Index everything.
            key = ()

        # Make sure the dtype of ``self.derivatives`` can
        # hold the dtype of the sum with copy's derivatives.
        #
        # In fact, strictly speaking this is only a problem when the
        # dtype of ``copy.derivatives`` is "larger" than the dtype of
        # ``self.derivatives``.  However, we always replace the dtype
        # of ``self.derivatives`` as soon as the two dtypes differ.

        if self.derivatives.dtype != other.derivatives.dtype:
            # Possibly "upgrade" ``self.derivatives``.
            self.derivatives = self.derivatives + numpy.zeros([],
                dtype=other.derivatives.dtype)
                # numpy.zeros([]) returns a scalar zero.  Adding this
                # is a no-op on any numeric array except for dtype.
        #
        # From now on, we can use ``+=`` on ``self.derivatives`` with
        # (parts of) ``copy.derivatives`` without danger of dtype
        # downgrading.

        # First, add on same name ...

        matching_mask = (self.names[key] == copy.names)

        self.derivatives[key] += matching_mask * other.derivatives

        # Mark the cells as used.
        other &= (1 - matching_mask)
        
        # Second, try to fill empty space ...
        #
        # Where there is empty space, there are zeros.

        empty_mask = (self.names[key] == 0)

        other_filled_mask = (other.names != 0)
        fillin_mask = empty_mask * other_filled_mask

        self.names[key] += fillin_mask * other.names
        self.derivatives[key] += fillin_mask * other.derivatives

        # Mark the cells as used.
        other &= (1 - fillin_mask)

        # Ok, we're done so far ...

        return other

    #
    # Arithmetics
    #

    def __and__(self, mask):
        """ Returns a copy of *self* where names are masked by *mask*.
        Parts of self's names where *mask* is zero are returned zero.
        The derivatives are shared between the returned Dependency and
        *self*.
        """

        return Dependency(
            names=(self._names * mask),
            derivatives=self._derivatives,
        )
    
    def __mul__(self, other):
        """Multiply the dependency by some ndarray factor, i.e., scale the 
        derivative."""

        return Dependency(
                names=self.names,
                derivatives=(self.derivatives * other))

    #
    # Reflected arithmetics
    #

    # __radd__() and __rsub__() are not needed, because always both operands
    # will be Dependency instances.

    def __rmul__(self, other):
        return Dependency(
                names=self.names,
                derivatives=(other * self.derivatives))
    
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
                names=self.names[key],
                derivatives=self.derivatives[key])

    def clear(self, key):
        """Clear the portion given by KEY, by setting the values stored to
        zero."""

        self.names[key] = 0
        self.derivatives[key] = 0

    def __len__(self):
        return self.shape[0]
    
    #
    # ndarray methods ...
    #

    def compress(self, *compress_args, **compress_kwargs):
        """Returns a copy with the Dependency's arrays compress()'ed.  The
        arguments are handed over to the arrays' methods."""

        return Dependency(
                names=self.names.compress(
                    *compress_args, **compress_kwargs),
                derivatives=self.derivatives.compress(
                    *compress_args, **compress_kwargs))

    def copy(self):
        """Returns a copy with the data arrays copied.  No name replacement
        is done (see undarray.copy for documentation)."""

        return Dependency(
                names=self.names.copy(),
                derivatives=self.derivatives.copy())

    def flatten(self, *flatten_args, **flatten_kwargs):
        """Returns a copy with the Dependency's arrays flatten()'ed.  The
        arguments are handed over to the arrays' methods."""

        return Dependency(
                names=self.names.flatten(
                    *flatten_args, **flatten_kwargs),
                derivatives=self.derivatives.flatten(
                    *flatten_args, **flatten_kwargs))

    def repeat(self, *repeat_args, **repeat_kwargs):
        """Returns a copy with repeat()'ed arrays.  The arguments are handed 
        over to the arrays' methods."""

        return Dependency(
                names=self.names.repeat(
                    *repeat_args, **repeat_kwargs),
                derivatives=self.derivatives.repeat(
                    *repeat_args, **repeat_kwargs))

    def reshape(self, *reshape_args):
        """Returns a copy with reshape()'ed arrays.  The arguments are
        handed over to the arrays' methods.  numpy.reshape() takes no
        keyword arguments."""

        return Dependency(
                names=self.names.reshape(*reshape_args),
                derivatives=self.derivatives.reshape(*reshape_args))

    def transpose(self, *transpose_args, **transpose_kwargs):
        """Returns a copy with transpose()'ed arrays.  The arguments are
        handed over to the arrays' methods."""

        return Dependency(
                names=self.names.transpose(
                    *transpose_args, **transpose_kwargs),
                derivatives=self.derivatives.transpose(
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
            raise ValueError('Dependency with shape %s cannot be broadcast '    
                'to shape %s.' % (self.shape, shape))

        if self.ndim != 0:
            # If the object is scalar, the expression wouldn't work.
            if shape[-self.ndim:] != self.shape:
                raise ValueError('Dependency with shape %s cannot be '
                    'broadcast to shape %s.' % (self.shape, shape))
        # else: Scalar object can be broadcast to any shape.

        # Prepare intermediate shape ...

        shape = list(shape)
        intermediate_shape = [1] * (len(shape) - self.ndim) + list(self.shape)

        # result will in the end hold the result.
        result = self.reshape(tuple(intermediate_shape))

        # Repeat self_intermediate to match SHAPE ...

        for dim in xrange(0, len(shape) - self.ndim):

            # Repeat in SHAPE's dimension dim.
            result = result.repeat(shape[dim], axis=dim)
        
        # result became final object ...

        return result

    #
    # String conversion function ...
    #

    def __str__(self):
        """Short representation."""

        if self.ndim == 0:
            # Return a scalar representation ...
            return "(names = %d, derivatives = %s)" % \
                    (self.names, self.derivatives)
        else:
            # Return an array representation ...
            return "(names:\n%s\nderivatives:\n%s\n)" % \
                    (self.names, self.derivatives)

    # There seems to be no sensible __repr__().
