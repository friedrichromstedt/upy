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
    
    The variance is ``derivative ** 2`` if ``derivative`` is not
    complex; otherwise the variance is undefined."""

    #
    # Initialisation methods ...
    #

    def __init__(self,
            names=None, derivatives=None,
            shape=None, dtype=None):
        """Initialise the dependency on error sources *names* of unity 
        variances with derivatives *derivatives*.  Both are supposed to be
        ndarrays of equal shape.

        Alternatively, *shape* and *dtype* can be specified.  In this
        case, an empty Dependency with a derivatives array of dtype
        *dtype* will be constructed. """

        if names is not None and derivatives is not None:

            if names.shape != derivatives.shape:
                raise ValueError("Shape mismatch in initialising a"
                    " Dependency:"
                    " names.shape = %s, derivatives.shape = %s"
                    % (names.shape, derivatives.shape))
            
            self.names = names
            self.derivatives = derivatives

            self.shape = self.names.shape
            self.dtype = self.derivatives.dtype
            self.ndim = self.names.ndim

        elif shape is not None:

            self.names = numpy.zeros(shape, dtype=numpy.int)
            self.derivatives = numpy.zeros(shape, dtype=dtype)
                # leaving *dtype* ``None`` leads to a derivatives
                # ndarray with "standard" dtype (``numpy.float``).

            self.shape = shape
            self.dtype = self.derivatives.dtype
                # When *dtype* is None, ``self.derivatives.dtype``
                # will differ from *dtype*.
            self.ndim = len(self.shape)

        else:
            raise ValueError("Dependency: Unable to initialise from"
                " the arguments provided")

#X    def copy_names(self):
#X        """Return a new Dependency with copied .names."""
#X
#X        return Dependency(
#X                names = self.names.copy(),
#X                derivatives = self.derivatives)
    
    def is_empty(self):
        """Return True if this Dependency can be discarded."""

        return not self.names.any()
    
    def is_nonempty(self):
        """Return True if this Dependency cannot be discarded."""

        return self.names.any()

    #
    # Obtaining the variances ...
    #

    @property
    def variance(self):
        """Get the variance induced by this dependency."""

        if not numpy.isrealobj(self.derivatives):
            # It might be complex.
            raise ValueError('Refusing to calculate variances '
                    'of non-real Dependency')
        return (self.names != 0) * self.derivatives ** 2

    #
    # Complex numbers ...
    #
    
    @property
    def real(self):
        """ Returns the real part of this Dependency. """

        return Dependency(
            names=self.names.copy(),
            derivatives=self.derivatives.real.copy(),
                # ``array.real`` returns a *view*::
                #
                #   >>> z = numpy.asarray(1 + 1j)
                #   >>> r = z.real
                #   >>> z[()] = 2 + 1j
                #   >>> r
                #   array(2.0)
        )

    @property
    def imag(self):
        """ Returns the imaginary part of this Dependency. """
        
        return Dependency(
            names=self.names.copy(),
            derivatives=self.derivatives.imag.copy(),
        )

    def conj(self):
        """ Returns the complex conjugate. """

        return Dependency(
            names=self.names.copy(),
            derivatives=self.derivatives.conj(),
                # This copies the real component.
        )

    #
    # Arithmetics:  Binary arithmetics ...
    #

    def add(self, other, key=None):
        """ Adds the *other* to self as far as possible, what is left
        and could not be added is returned as a new Dependency.  If
        *key* is given, it specifies the portion of *self* where the
        *other* is applied. """

        if key is None:
            # Index everything.
            key = ()

        # Check if the part of *self* indexed by *key* has the same
        # shape as *other* does:
# We leave this alone to allow broadcasting of *other*.
#X1        indexed_shape = self.derivatives[key].shape
#X1        if indexed_shape != other.shape:
#X1            raise ValueError('In Dependency.add:  '
#X1                'Attempted to add other.shape=%s to indexed shape=%s '
#X1                'with key=%s (self.shape=%s).'
#X1                % (other.shape, indexed_shape, key, self.shape)
#X1            )

#X        # Make sure the dtype of ``self.derivatives`` can
#X        # hold the dtype of the sum with copy's derivatives.
#X        #
#X        # In fact, strictly speaking this is only a problem when the
#X        # dtype of ``copy.derivatives`` is "larger" than the dtype of
#X        # ``self.derivatives``.  However, we always replace the dtype
#X        # of ``self.derivatives`` as soon as the two dtypes differ.
#X
#X        if self.derivatives.dtype != other.derivatives.dtype:
#X            # Possibly "upgrade" ``self.derivatives``.
#X            self.derivatives = self.derivatives + numpy.zeros([],
#X                dtype=other.derivatives.dtype)
#X                # numpy.zeros([]) returns a scalar zero.  Adding this
#X                # is a no-op on any non-scalar numeric array except
#X                # for dtype (scalar ndarrays turn into "true"
#X                # scalars).
#X        #
#X        # From now on, we can use ``+=`` on ``self.derivatives`` with
#X        # (parts of) ``other.derivatives`` without danger of dtype
#X        # downgrading.

        # First, add on same name ...

        matching_mask = (self.names[key] == other.names)
            # This might involve broadcasting of ``other.names``.

        self.derivatives = numpy.asarray(self.derivatives)
            # Turn "true" scalars into scalar ndarrays prior to item
            # assignment.
        self.derivatives[key] += matching_mask * other.derivatives
            # If the shape of ``matching_mask * other.derivatives`` is
            # too large, numpy will complain.  In all other cases, the
            # result of ``matching_mask * other.derivatives`` will fit
            # ``self.derivatives[key]``.

        # Mark the cells as used.
        other = other & (1 - matching_mask)
            # From now on, *other* has the shape of ``(1 -
            # matching_mask)``, which is identical to the shape of
            # ``self[key]``.  The ``&`` operation might involve
            # broadcasting inside of ``__and__``.
        
        # Second, try to fill empty space ...
        #
        # Where there is empty space, there are zeros.

        empty_mask = (self.names[key] == 0)

        other_filled_mask = (other.names != 0)
        fillin_mask = empty_mask * other_filled_mask

        self.names = numpy.asarray(self.names)
            # Turn "true" scalars into scalar ndarrays prior to item
            # assignment.  *self.derivatives* has already been
            # prepared above.
        self.names[key] += fillin_mask * other.names
        self.derivatives[key] += fillin_mask * other.derivatives
            # Do use augmented assignment ``+=`` because portions
            # where the assigned arrays are zero are to be preserved
            # *without change*.

        # Mark the cells as used.
        other = other & (1 - fillin_mask)

        # Ok, we're done so far ...

        return other
            # The *other* is, now, of the same shape as ``self[key]``,
            # since the ``&`` operations above have been carried out.

    #
    # Arithmetics
    #

    def __and__(self, mask):
        """ Returns a copy of *self* where names are masked by *mask*.
        Parts of self's names where *mask* is zero are returned zero.
        Same applies to the *derivatives* attribute of the returned
        Dependency.  """

        return Dependency(
            names=(self.names * mask),
            derivatives=(self.derivatives * mask),
        )
    
    def __mul__(self, other):
        """Multiply the dependency by some ndarray factor, i.e., scale the 
        derivatives."""

        result_derivatives = self.derivatives * other
        (bc_names, bc_derivatives) = numpy.broadcast_arrays(
                self.names, result_derivatives)
        # The shape of *bc_derivatives* will always be equal to the
        # shape of *result_derivatives*, since *self.derivatives* and
        # *self.names* have equal shape.  As a safety measure, we
        # assert this fact:
        assert(bc_derivatives.shape == result_derivatives.shape)
        # With this assertion, we can skip copying *bc_derivatives* by
        # means of ``numpy.array``, since all elements refer to a
        # unique memory location.  This does not hold necessarily for
        # *bc_names*, so we copy *bc_names*.  Copying *bc_names* is a
        # necessity anyhow to avoid crosstalk.  *result_derivatives*
        # already satisfies this requirement.

        return Dependency(
                names=numpy.array(bc_names),
                derivatives=bc_derivatives,
        )

    #
    # Reflected arithmetics
    #

    # __radd__() and __rsub__() are not needed, because always both operands
    # will be Dependency instances.

#X    def __rmul__(self, other):
#X        return Dependency(
#X                names=self.names,
#X                derivatives=(other * self.derivatives))
    __rmul__ = __mul__
        # I do not expect use cases of Dependency with data arrays
        # which do not commute on multiplication.
    
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
                names=self.names[key].copy(),
                derivatives=self.derivatives[key].copy(),
        )

    def clear(self, key):
        """Clear the portion given by KEY, by setting the values stored to
        zero."""

        self.names = numpy.asarray(self.names)
        self.derivatives = numpy.asarray(self.derivatives)
            # Turn "true" scalars into scalar ndarrays prior to item
            # assignment.
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

#X2    def broadcasted(self, shape):
#X2        """Bring the instance in shape SHAPE, by repetition of the object.  No
#X2        reshape()'ing will be performed.  This function is used when coercing
#X2        lower-dimensional object with higher-dimensional ones.  It makes shure
#X2        that both operands can have the same shape before coercion takes 
#X2        place.  Broadcasting is necessary in the case that an Dependency is
#X2        taken over from the other operand into the final result, because there
#X2        is no dependency of both operands on the Dependency.  In this case,
#X2        no numpy broadcasting would occour, and the data integrity would be
#X2        compromised.
#X2
#X2        The call will fail if len(SHAPE) < .ndim.  Otherwise, the .ndim last
#X2        items of SHAPE must be equal to .shape.  The object will first be
#X2        brought to the shape [1, 1, 1, ...] + .shape, such that .ndim 
#X2        becomes len(SHAPE).  Then, it will be repeated in the added dimensions
#X2        to meet SHAPE's elements.  The first step is done via .reshape(), and
#X2        the second via .repeat(count, axis = axis).
#X2        
#X2        This method acts on a copy."""
#X2
#X2        # Check conditions ...
#X2
#X2        if len(shape) < self.ndim:
#X2            raise ValueError('Dependency with shape %s cannot be broadcast '    
#X2                'to shape %s.' % (self.shape, shape))
#X2
#X2        if self.ndim != 0:
#X2            # If the object is scalar, the expression wouldn't work.
#X2            if shape[-self.ndim:] != self.shape:
#X2                raise ValueError('Dependency with shape %s cannot be '
#X2                    'broadcast to shape %s.' % (self.shape, shape))
#X2        # else: Scalar object can be broadcast to any shape.
#X2
#X2        # Prepare intermediate shape ...
#X2
#X2        shape = list(shape)
#X2        intermediate_shape = [1] * (len(shape) - self.ndim) + list(self.shape)
#X2
#X2        # result will in the end hold the result.
#X2        result = self.reshape(tuple(intermediate_shape))
#X2
#X2        # Repeat self_intermediate to match SHAPE ...
#X2
#X2        for dim in xrange(0, len(shape) - self.ndim):
#X2
#X2            # Repeat in SHAPE's dimension dim.
#X2            result = result.repeat(shape[dim], axis=dim)
#X2        
#X2        # result became final object ...
#X2
#X2        return result

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
