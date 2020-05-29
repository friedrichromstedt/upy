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

    def __init__(self,
            names=None, derivatives=None,
            shape=None, dtype=None):
        """ A ``Dependency`` can be initialised in two ways:

        1.  Providing its *shape*; or
        2.  specifying *names* and *derivatives*.

        When both *names* as well as *derivatives* aren't ``None``,
        they will both be transformed into ndarrays, where *dtype* is
        used for the derivatives ndarray.  When their shapes are
        different, a ``ValueError`` will be raised.  If *dtype* is
        ``None``, the dtype of the derivatives ndarray won't be
        overridden.  The dtype of the *names* array *never* will be
        overridden.

        Otherwise, *shape* will be used to provide an empty Dependency
        of the given *dtype* (with all names set to zero and with zero
        derivatives).  In this case, the *names* will have dtype
        ``numpy.int``.

        In all other cases, the Dependency cannot be initialised
        and ``ValueError`` will be raised. """

        if names is not None and derivatives is not None:
            self.names = numpy.asarray(names)
            self.derivatives = numpy.asarray(derivatives, dtype=dtype)
            if self.names.shape != self.derivatives.shape:
                raise ValueError("Shape mismatch in initialising a"
                    " Dependency:"
                    " names.shape = %s, derivatives.shape = %s"
                    % (names.shape, derivatives.shape))

        elif shape is not None:
            self.names = numpy.zeros(shape, dtype=numpy.int)
            self.derivatives = numpy.zeros(shape, dtype=dtype)
                # leaving *dtype* ``None`` leads to a derivatives
                # ndarray with "standard" dtype (``numpy.float``).

        else:
            raise ValueError("Dependency: Unable to initialise from"
                " the arguments provided")

        self.shape = self.derivatives.shape
        self.dtype = self.derivatives.dtype
        self.ndim = self.derivatives.ndim

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
    # Binary arithmetics ...
    #

    def add(self, other, key=None):
        """ Adds the *other* to self as far as possible, what is left
        and could not be added is returned as a new Dependency.  If
        *key* is given, it specifies the portion of *self* where the
        *other* is applied. """

        if key is None:
            # Index everything.
            key = ()

        # We do not apply shape checking whether the part of *self*
        # indexed by *key* has the same shape as *other*.  This
        # permits broadcasting of *other*.

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

    __rmul__ = __mul__
    
    # Augmented arithmetics will be emulated by using standard
    # arithmetics.

    #
    # Keying methods ...
    #
    
    def __getitem__(self, key):
        """ Returns a new Dependency with *key* applied both to the
        :attr:`derivatives` as well as to the :attr:`names` of *self*.
        The indexed results will be copied. """
        
        return Dependency(
                names=self.names[key].copy(),
                derivatives=self.derivatives[key].copy(),
        )

    def clear(self, key):
        """ Set *self.names* and *self.derivatives* to zero at the
        positions indexed by *key*. """

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
    # String conversion ...
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
