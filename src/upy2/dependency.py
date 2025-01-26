# Developed since: Feb 2010

import numpy

__all__ = ['Dependency']


class Dependency(object):
    """ The class :class:`Dependency` represents the dependence of an
    uncertain quantity on uncertainty sources of unity variance by a
    derivative.  When the :attr:`derivative` is real-valued, the
    induced variance of the quantity is equal to ``derivative ** 2``.
    For non-real derivatives, an induced variance of the quantity
    cannot be given.

    A single :class:`Dependency` can store *one* dependency per
    element.  The uncertainty sources are identified by integers
    called *names*.  The name ``0`` represents the *absent* dependency
    of the respective element.  Dependencies can be combined be means
    of :meth:`add`, here the argument Dependency is incorporated into
    the Dependency whose :meth:`add` is called as far as possible by
    filling elements with zero name and by adding derivatives of
    elements with matching name; :meth:`add` returns the remnant
    Dependency, with all elements used cleared.

    Dependencies can be *multiplied* and *masked*, and a range of
    ``ndarray`` methods is supported. """

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

        When at least one of *names* and *derivatives* is ``None``,
        *shape* will be used to provide an empty Dependency of the
        given *dtype* (with all names set to zero and with zero
        derivatives).  In this case, the *names* will have dtype
        ``int``.

        In all other cases, the Dependency cannot be initialised
        and ``ValueError`` will be raised. """

        if names is not None and derivatives is not None:
            self.names = numpy.asarray(names)
            self.derivatives = numpy.asarray(derivatives, dtype=dtype)
            if self.names.shape != self.derivatives.shape:
                raise ValueError(
                        'Shape mismatch in initialising a '
                        'Dependency: names.shape = {0}, derivatives.'
                        'shape = {1}'.format(
                            self.names.shape, self.derivatives.shape))

        elif shape is not None:
            self.names = numpy.zeros(shape, dtype=int)
            self.derivatives = numpy.zeros(shape, dtype=dtype)
                # leaving *dtype* ``None`` leads to a derivatives
                # ndarray with "standard" dtype (``float``).

        else:
            raise ValueError("Dependency: Unable to initialise from "
                "the arguments provided")

        self.shape = self.derivatives.shape
        self.dtype = self.derivatives.dtype
        self.ndim = self.derivatives.ndim

    def is_empty(self):
        """ Returns whether all elements of *self.names* are equal to
        zero.  This means, that the Dependency does not induce any
        uncertainty. """

        return not self.names.any()
    
    def is_nonempty(self):
        """ Returns whether any alements of *self.names* aren't equal
        to zero.  In this case, the Dependency induces some
        uncertainty. """

        return self.names.any()

    #
    # Obtaining the variances ...
    #

    @property
    def variance(self):
        """ When *self.derivatives* is real-valued, this method
        returns the variance ``self.derivatives ** 2`` induced by this
        Dependency for elements with nonzero *name*; the variance
        returned is masked out to zero for elements with zero name.
        For non-real derivatives, no such variance can be given. """

        if not numpy.isrealobj(self.derivatives):
            # It might be complex.
            raise ValueError(
                'Refusing to calculate the variance of a non-real '
                'Dependency')
        return (self.names != 0) * self.derivatives ** 2

    #
    # Complex numbers ...
    #
    
    @property
    def real(self):
        """ Returns the real part of this Dependency.  Both the names
        as well as the real part of *self.derivatives* will be copied. """

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

    conjugate = conj
        # :func:`numpy.conj` looks for :attr:`conjugate`, not
        # :attr:`conj`.

    #
    # Binary arithmetics ...
    #

    def add(self, other, key=None):
        """ This method incorporates another ``Dependency`` *other*
        into *self* in-place as far as possible by:

        1.  Filling elements of *self* with zero name by elements of
            *other* (replacing both the *name* as well as the
            *derivative*);
        2.  adding the derivatives of *other* to elements of *self*
            with matching name.

        Returned is a copy of *other* with used-up elements masked
        out.

        When *key* is given, *other* will be added to the sub arrays
        of *self.names* and *self.derivatives* indexed by *key*.

        The *other* needs to be broadcastable to the shape of *self*
        indexed by *key*.  The ``Dependency`` returned will *always*
        have this shape. """

        if key is None:
            # Index everything.
            key = ()

        # We do not apply shape checking whether the part of *self*
        # indexed by *key* has the same shape as *other*.  This
        # permits broadcasting of *other*.

        # First, add on same name ...

        matching_mask = (self.names[key] == other.names)
            # This might involve broadcasting of ``other.names``.

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
        # An element is *empty* when its *name* is *zero*.

        empty_mask = (self.names[key] == 0)

        other_filled_mask = (other.names != 0)
        fillin_mask = empty_mask * other_filled_mask

        self.names[key] += fillin_mask * other.names
        self.derivatives[key] += fillin_mask * other.derivatives
            # Do use augmented assignment ``+=`` because portions
            # where the augmenting arrays are zero are to be preserved
            # *without change*.

        # Mark the cells as used.
        other = other & (1 - fillin_mask)

        # Finished processing *other*.

        return other
            # The *other* is, now, of the same shape as ``self[key]``,
            # since the ``&`` operation above has been carried out.

    def __and__(self, mask):
        """ Returns a copy of *self* where names and derivatives are
        masked by *mask*: Parts of self's names and derivatives where
        *mask* is zero are returned zero. """

        return Dependency(
            names=(self.names * mask),
            derivatives=(self.derivatives * mask),
        )
    
    def __mul__(self, other):
        """ Returns a copy of *self* with the derivatives set to the
        product of ``self.derivatives`` and *other*.

        The shapes of *self* and *other* need not be equal as long as
        they can be broadcast.  The :attr:`names` ndarray of *self*
        will be broadcast to the result shape as well. """

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

    # Reverse multiplication is unsupported.  It would not work with
    # ndarrays as first operand (see 228ad14).

    # Augmented arithmetics will be emulated by using standard
    # arithmetics.

    #
    # Keying methods ...
    #
    
    def __getitem__(self, key):
        """ Returns a new Dependency with *key* applied both to the
        :attr:`derivatives` as well as to the :attr:`names` of *self*.
        The results will be copied. """
        
        return Dependency(
                names=self.names[key].copy(),
                derivatives=self.derivatives[key].copy(),
        )

    def clear(self, key):
        """ Set *self.names* and *self.derivatives* to zero at the
        positions indexed by *key*. """

        self.names[key] = 0
        self.derivatives[key] = 0

    def __len__(self):
        return self.shape[0]
    
    #
    # ndarray methods ...
    #

    def copy(self):
        """ Returns a Dependency constructed from copies of the names
        and derivatives of *self*. """

        return Dependency(
                names=self.names.copy(),
                derivatives=self.derivatives.copy())

    def compress(self, *compress_args, **compress_kwargs):
        """ Returns a Dependency constructed from the *compressed*
        names and derivatives of *self*. """

        # :meth:`ndarray.compress` returns a copy by itself.
        return Dependency(
                names=self.names.compress(
                    *compress_args, **compress_kwargs),
                derivatives=self.derivatives.compress(
                    *compress_args, **compress_kwargs))

    def flatten(self, *flatten_args, **flatten_kwargs):
        """ Returns a Dependency constructed from the *flattened*
        names and derivatives of *self*. """

        # :meth:`ndarray.flatten` returns a copy by itself.
        return Dependency(
                names=self.names.flatten(
                    *flatten_args, **flatten_kwargs),
                derivatives=self.derivatives.flatten(
                    *flatten_args, **flatten_kwargs))

    # Notice that :meth:`ndarray.ravel` returns a copy *only if
    # needed*, just as :func:`numpy.ravel` does, while
    # :meth:`ndarray.flatten` returns a copy *always*.  Notice also,
    # that there is no :func:`numpy.flatten`.
    #
    # Notice further, that :func:`numpy.ravel` does not make use of a
    # :meth:`ravel` of the operand provided; instead, it returns a
    # ``dtype=object`` array always.

    def repeat(self, *repeat_args, **repeat_kwargs):
        """ Returns a Dependency constructed from the *repeated* names
        and derivatives of *self*. """

        # It appears that :meth:`ndarray.repeat` returns a copy
        # *always*.
        return Dependency(
                names=self.names.repeat(
                    *repeat_args, **repeat_kwargs),
                derivatives=self.derivatives.repeat(
                    *repeat_args, **repeat_kwargs))

    def reshape(self, *reshape_args, **reshape_kwargs):
        """ Returns a Dependency constructed from the *reshaped* names
        and derivatives of *self*.  The results will be copied. """

        return Dependency(
                names=self.names.reshape(
                    *reshape_args, **reshape_kwargs).copy(),
                derivatives=self.derivatives.reshape(
                    *reshape_args, **reshape_kwargs).copy())

    def transpose(self, *transpose_args, **transpose_kwargs):
        """ Returns a Dependency constructed from the *transposed*
        names and derivatives of *self*.  The results will be copied.
        """

        return Dependency(
                names=self.names.transpose(
                    *transpose_args, **transpose_kwargs).copy(),
                derivatives=self.derivatives.transpose(
                    *transpose_args, **transpose_kwargs).copy())

    #
    # String conversion ...
    #

    def __repr__(self):
        return "<{shape}-shaped {dtype}-typed Dependency>".format(
                shape=self.shape, dtype=self.dtype)
