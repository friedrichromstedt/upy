# Developed since: Jan 2010

"""The central upy2 module, implementing the uncertain ndarray:
:class:`undarray`."""

import numpy
import upy2
import upy2.dependency
import upy2.typesetting.protocol
import upy2.context
#import upy2.printable
#import warnings

__all__ = ['undarray', 'uzeros', 'asuarray', 'U', 'u', 'ucopy',
    'unegative',
    'uadd', 'usubtract', 'umultiply', 'udivide',
    'upower']

typesetting_context = upy2.context.byprotocol(
    upy2.typesetting.protocol.Typesetter)

#
# Internal helper function(s) ...
#

#   This method has been superseded by :func:`find_common_dtype`.
#
#X def _ravel(object):
#X     """Ravel a mixed-mode initialisation argument.  undarray instances
#X     contained will ravel to their raveled .values."""
#X 
#X     if isinstance(object, undarray):
#X         
#X         # Return the raveled version of object.value ...
#X         #
#X         # This is done beause *all* elements of object.value may contribute
#X         # to the dtype.  E.g., when dtype = numpy.object, this may occur 
#X         # because the first element is an non-numeric type, or the second, ...
#X 
#X         return object.value.flatten().tolist()
#X 
#X     elif numpy.isscalar(object) or \
#X             (isinstance(object, numpy.ndarray) and \
#X              object.shape == ()):
#X 
#X         # Scalars are already raveled ...
#X 
#X         return [object]
#X 
#X     else:
#X 
#X         # Sequence objects must be recursed ...
#X 
#X         raveled = []
#X 
#X         for element in object:
#X             raveled.extend(_ravel(element))
#X 
#X         return raveled

# This method has been deprectated before it came to use.  It is no
# longer necessary since the implementation of __setitem__ is able to
# upgrade the dtype of self.value.
#
#X def find_common_dtype(object):
#X     """ Calculates the least dtype to store the nominal value taken
#X     from the given *object*. """
#X     
#X     if isinstance(object, undarray):
#X         return object.value.dtype
#X 
#X     elif numpy.isscalar(object) or (isinstance(object, numpy.ndarray)
#X             and object.shape == ()):
#X         return numpy.asarray(object).dtype
#X 
#X     else:
#X         dtypes = [find_common_dtype(element) for element in object]
#X         zeros = [numpy.zero(shape=[], dtype=dtype) for dtype in
#X             dtypes]
#X         return numpy.asarray(zeros).dtype
#X             # When *zeros* == [], numpy.asarray([]) returns
#X             # ``array([], dtype=float64)``.

#
# Some convenience functions ...
#

def uzeros(shape, dtype=None):
    """ Returns a zero-undarray of shape *shape* and optionally using
    dtype *dtype*.  All *shape* arguments accepted by
    ``numpy.zeros()`` will work. """

    return undarray(shape=shape, dtype=dtype)

#? def zeros(shape):
#?     """Equivalent to :func:`uzeros`.
#?     
#?     This method will be deprecated in v0.5.  Use :func:`uzeros` instead."""
#? 
#?     warnings.warn(DeprecationWarning('zeros() will be deprecated in v0.5, '
#?         'use uzeros() instead')
#? 
#?     return uzeros(shape)

def asuarray(uarray_like):
    """ If *uarray_like* is *not* an :class:`undarray`, it will be fed
    to the constructor of :class:`undarray` in order to produce an
    undarray.  If, on the contrary, *undarray_like* is already an
    undarray instance, it will be returned without change. """

    if isinstance(uarray_like, undarray):
        return uarray_like
    return undarray(uarray_like)

def ucopy(uarray_like):
    """ If *uarray_like* is an instance of :class:`undarray`, its
    contents will be copied.  Otherwise, a new :class:`undarray` is
    constructed; in that case the ``uarray_like`` data structure
    will be copied using ``numpy.copy``. """

    if isinstance(uarray_like, undarray):
        return uarray_like.copy()
    return undarray(nominal=numpy.copy(uarray_like))

#
# Syntactic Sugar ...
#

# Definition of the "Uncertainty" Protocol:

class U(upy2.context.Protocol):
    def __init__(self, stddevs):
        """ "Uncertainty" (``U``) Context Providers provide
        uncertainty *standard deviations* based on *errors*.  The
        *error* is supposed to be a multiple of the *standard
        deviation*.  The connecting factor is given by the *stddevs*
        argument. """

        upy2.context.Protocol.__init__(self)

        self.stddevs = stddevs

    def provide(self, error):
        """ Provides an undarray with zero nominal value and with
        uncertainty based on *error*.  *error* is interpreted as a
        multiple of the standard deviation as defined on
        initialisation time. """

        stddev = numpy.true_divide(error, self.stddevs)
        shape = stddev.shape
        result = undarray(shape=shape, dtype=stddev.dtype)

        dependency = upy2.dependency.Dependency(
                names=upy2.id_generator.get_idarray(shape=shape),
                derivatives=stddev,
        )
        result.append(dependency)

        return result

    def __call__(self, error):
        """ Convenience method to provide a short-hand for
        :meth:`provide`.

        Example::

            u5 = U(5)
            ua = nominal +- u5(five_sigma_error)

        Writing ``.provide(...)`` is not needed to ensure readability
        and hence the syntax can be made more terse by pruning the
        explicit call to :meth:`provide`. """

        return self.provide(error)

upy2.context.define(U)

# Access to the "U" Context:

U_context = upy2.context.byprotocol(U)

def u(error):
    return U_context.current().provide(error)

#
# The central undarray class ...
#

class undarray(object):
    """Implements uncertain ndarrays.  The name is derived from
    numpy.ndarray. """

    def __init__(self,
            nominal=None,
            stddev=None,
            derivatives=None,
            characteristic=None,
            dtype=None,
            shape=None):
        """ If *stddev* and *nominal* aren't None, *nominal* and
        *stddev* will be converted to numpy.ndarrays by
        ``numpy.asarray``.  The initial Characteristic will reflect
        the single dependency expressed by *stddev*.

        If *derivatives* and *nominal* are not None, *derivatives*
        must be a list ``[(undarray instance, derivative), ...]``,
        giving the derivatives with that the new undarray depends on
        the given undarrays.  *nominal* will be converted to a
        ``numpy.ndarray``.

        If *characteristic* and *nominal* are not None, *nominal* is
        converted to a ``numpy.ndarray`` by means of ``numpy.asarray``
        and the *characteristic* is taken over *without copying it*.

        If otherwise *nominal* is given, it will be converted by
        ``numpy.asarray`` and the ``undarray`` instance will carry an
        empty Characteristic.
        
        If *nominal* is None, *shape* is taken into account, to create
        a new, zero-valued undarray of dtype *dtype* (giving ``None``
        as *dtype* results in ``numpy.float`` used as dtype).  As the
        Characteristic is empty in this case, and only the
        Dependencies carry a dtype, the *dtype* given pertains to the
        ``nominal`` attribute alone.
        
        If none of these branches matches, ValueError will be raised.

        *nominal* and *stddev* will be used as returned from
        ``numpy.asarray``.  They won't be copied explicitly.  The
        ``Characterstic`` instances of the ``undarray`` instances in
        ``derivatives`` *will* be copied during the initialisation.
        """
        
        # Attributes to initialise:
        #
        # - self.nominal
        # - self.dependencies
        # - self.dtype
        # - self.shape
        # - self.ndim

        self.dependencies = []

        if stddev is not None and nominal is not None:
            
            # Constuct a new undarray ...

            # Convert to ndarrays.
            nominal = numpy.asarray(nominal)
            stddev = numpy.asarray(stddev)

            # Check shape.
            if nominal.shape != stddev.shape:
                raise ValueError("Shape mismatch between *nominal* (shape %s) and *stddev* (shape %s)" % (nominal.shape, stddev.shape))

            self.nominal = nominal

            self.shape = self.nominal.shape
            self.ndim = self.nominal.ndim
            
            # Create a Dependency instance from scratch.
            dependency = upy2.dependency.Dependency(
                names=upy2.id_generator.get_idarray(
                    shape=self.shape),
                derivatives=stddev,
            )   # The Dependency constructor doesn't copy the data
                # given.

            self.characteristic = upy2.characteristic.Characteristic(
                shape=self.shape,
            )
            self.characteristic.append(dependency)

        elif derivatives is not None and nominal is not None:

            # Derive the new undarray from known ones ...

            self.nominal = numpy.asarray(nominal)
            self.shape = self.nominal.shape
            self.ndim = self.nominal.ndim

            # Create a new, empty Characteristic where we can fill in
            # the dependencies introduced by *derivatives*.
            self.characteristic = upy2.characteristic.Characteristic(
                    shape=self.shape)

            # Fill in the dependencies.
            for (instance, derivative) in derivatives:
                self.characteristic += \
                        instance.characteristic * derivative

        elif characteristic is not None and nominal is not None:

            nominal = numpy.asarray(nominal)
            if characteristic.shape != nominal.shape:
                raise ValueError("Shape mismatch between *nominal* (shape %s) and *characteristic* (shape %s)" % (nominal.shape, characteristic.shape))

            # Take over the characteristic ...

            self.nominal = nominal
            self.characteristic = characteristic

            self.shape = self.nominal.shape
            self.ndim = self.nominal.ndim

        elif nominal is not None:

            # Construct a new undarray with an empty Characteristic.

            self.nominal = numpy.asarray(nominal)

#X
#X            # Initialise from list-like structure or scalar number ...
#X
#X            # Determine the shape.
#X            shapeobject = object
#X            shape = []
#X            # Index the shapeobject until a scalar or an undarray is
#X            # reached:
#X            while True:
#X                if isinstance(shapeobject, undarray):
#X                    # Finish shape:
#X                    shape += list(shapeobject.shape)
#X                    break
#X                elif numpy.isscalar(shapeobject):
#X                    # We reached the scalar level.  Shape finished.
#X                    break
#X                else:
#X                    # Test for scalar array.
#X                    if isinstance(shapeobject, numpy.ndarray) and \
#X                            shapeobject.shape == ():
#X                        # In fact, it's scalar:
#X                        break
#X                    else:
#X                        # It's not a scalar array, indexing is
#X                        # possible:
#X                        shape.append(len(shapeobject))
#X                        shapeobject = shapeobject[0]
#X
#X            # Initialise the attributes.
#X
#X            # Initialise .value and .characteristic:
#X            self.value = numpy.zeros(shape, dtype=dtype)
#X            self.characteristic = upy.characteristic.Characteristic(
#X                    shape = tuple(shape))
#X
#X            # Provide .shape and .ndim, because __setitem__() needs it.
#X            self.shape = shape
#X            self.ndim = len(shape)
#X
#X            # Fill in the given values.
#X            # 
#X            # This will recurse into the OBJECT.
#X            self[()] = object

        elif shape is not None:

            # Construct an empty undarray ...

#X            if not isinstance(shape, tuple):
#X                raise ValueError("Cannot construct undarray: *shape* must be a tuple")
#X
#X            self.shape = shape
#X            self.ndim = len(shape)

            self.nominal = numpy.zeros(shape, dtype=dtype)
                # This accepts a scalar *shape* argument as well as
                # tuples and lists.  We delegate the job of
                # interpreting *shape* to ``numpy.zeros``.

        else:
            raise ValueError("Cannot initialise an undarray from the arguments given.")

        self.dtype = self.nominal.dtype
        self.shape = self.nominal.shape
        self.ndim = self.nominal.ndim

    def append(self, dependency):
        if not self.shape == dependency.shape:
            raise ValueError('Cannot append a Dependency of shape %s '
                    'to a %s-shaped undarray' %
                    (dependency.shape, self.shape))
        if not self.dtype == dependency.dtype:
            raise ValueError('Cannot append a Dependency of dtype %s '
                    'to a %s-dtyped undarray' %
                    (dependency.dtype, self.dtype))
        self.dependencies.append(dependency)

    def clear(self, key):
        for dependency in self.dependencies:
            dependency.clear(key)

    def depend(self, other, derivative=None, key=None):
        """ *other* is an ``undarray``.  The ``Dependencies`` of
        *other* will be used multiplied by *derivative*.  *key*
        indexes *self* and determines the location where the
        ``Dependencies`` of *other* will be added.
        
        *derivative* defaults to an integer ``1``.  Without *key*, all
        of *self* is specified. """

        if derivative is None:
            derivative = 1

        # Check dtype compatibility ...

        derivative_dtype = numpy.result_type(derivative)
        dependency_dtype = numpy.result_type(
                other.dtype,
                derivative_dtype,
        )
        if not numpy.can_cast(dependency_dtype, self.dtype):
            raise ValueError(
                    'Cannot make a %s-dtype undarray depend on a '
                    '%s-dtype undarray with a derivative of dtype %s.'
                    % (self.dtype, other.dtype, derivative_dtype))

        # Make *self* depend on *other* with *derivative* ...

        for source in other.dependencies:
            # First, everything is left:
            source_remnant = source * derivative

            for target in self.dependencies:
                if source_remnant.is_empty():
                    # This source has been exhausted.
                    break
                # Attempt to add on same name or to fill empty space:
                source_remnant = target.add(source_remnant, key)

            if source_remnant.is_nonempty():
                # Append the *source_remnant* added to a new empty
                # Dependency of self's shape.
                broadcasted_source_remnant = \
                    upy2.dependency.Dependency(
                        shape=self.shape,
                        dtype=self.dtype,
                    )
                broadcasted_source_remnant.add(source_remnant, key)
                self.append(broadcasted_source_remnant)

    #
    # Complex numbers ...
    #

    @property
    def real(self):
        """ Returns the real component of *self*.  This pertains to
        the nominal value as well as to the Dependencies. """

        result = undarray(self.nominal.real.copy())
        for dependency in self.dependencies:
            result.append(dependency.real)
        return result

    @property
    def imag(self):
        """ Returns the imaginary component of *self*.  This pertains to
        the nominal value as well as to the Dependencies. """

        result = undarray(self.nominal.imag.copy())
        for dependency in self.dependencies:
            result.append(dependency.imag)
        return result

    def conj(self):
        """ Returns the conjugate of *self*. """

        result = undarray(self.nominal.conj())
        for dependency in self.dependencies:
            result.append(dependency.conj())
        return result

    #
    # Uncertainty properties ...
    #

    @property
    def variance(self):
        """ Returns the variance array, i.e., stddev ** 2. """

        result = numpy.zeros(shape=self.shape, dtype=self.dtype)
        for dependency in self.dependencies:
            result += dependency.variance
        return result
    
    @property
    def stddev(self):
        """ Returns the standard deviation. """
        
        return numpy.sqrt(self.variance)
            # In case of complex dependencies, retrieving
            # self.variance will fail when in the code path of
            # the :class:`Dependency` instance exhibiting complex
            # derivatives.

#?    def uncertainty(self, sigmas):
#?        """Returns ``sigmas * self.stddev``.
#?        
#?        This method will be deprecated by v0.5, please use explicit
#?        multiplication instead."""
#?
#?        warnings.warn(DeprecationWarning('undarray.uncertainty() will be '
#?            'deprecated by v0.5, please use explicit multiplication instead')
#?
#?        return sigmas * self.stddev
#?
#?    def weight(self):
#?        """Returns a numpy.ndarray suitable for weighting this undarray.
#?        The weights are 1.0 / .variance().  When a variance element is
#?        zero, the used variance is 1.0.
#?        
#?        This method will be deprecated in v0.5, use ``1 / ua.variance()``
#?        directly."""
#?        
#?        warnings.warn(DeprecationWarning('undarray.weight() will be '
#?            'deprecated in v0.5, use 1 / ua.variance() instead')
#?        
#?        # Calculate the variance used.
#?        used_variance = self.variance()
#?        used_variance += 1.0 * (used_variance == 0.0)
#?
#?        # Calculate the weight from the variance.
#?        return 1.0 / used_variance

    #
    # Binary arithmetics ...
    #

    def __add__(self, other):
        return uadd(self, other)

    def __sub__(self, other):
        return usubtract(self, other)

    def __mul__(self, other):
        return umultiply(self, other)

    def __div__(self, other):
        return udivide(self, other)

    def __pow__(self, other):
        return upower(self, other)

    #
    # Reflected binary arithmetics ...
    #

    def __radd__(self, other):
        return uadd(other, self)

    def __rsub__(self, other):
        return usubtract(other, self)

    def __rmul__(self, other):
        return umultiply(other, self)

    def __rdiv__(self, other):
        return udivide(other, self)

    def __rpow__(self, other):
        # Return: other ** self
        return upower(other, self)

    #
    # Augmented arithmetics will be emulated ...
    #

    #
    # Unary operators ...
    #

    def __pos__(self):
        return self

    def __neg__(self):
        return unegative(self)

    def __abs__(self):
        return uabsolute(self)
#X?        """This works for real-valued undarrays."""
#X?        
#X?        # Calculate an inversion mask ...
#X?
#X?        inversion_mask = numpy.ones(shape = self.nominal.shape)
#X?        inversion_mask -= 2 * (self.nominal < 0)
#X?
#X?        # Invert values which must be inverted, and invert also the dependency
#X?        # of this values on the error source ...
#X?
#X?        return self * inversion_mask
    
    #
    # Casts to int, float, ... are impossible, because we have ndarray values.
    #

    #
    # Comparison operators ...
    #

    def __lt__(self, other):
        if isinstance(other, undarray):
            return self.nominal < other.nominal
        else:
            return self.nominal < numpy.asarray(other)

    def __le__(self, other):
        if isinstance(other, undarray):
            return self.nominal <= other.nominal
        else:
            return self.nominal <= numpy.asarray(other)

    def __gt__(self, other):
        if isinstance(other, undarray):
            return self.nominal > other.nominal
        else:
            return self.nominal > numpy.asarray(other)

    def __ge__(self, other):
        if isinstance(other, undarray):
            return self.nominal >= other.nominal
        else:
            return self.nominal >= numpy.asarray(other)

    def __eq__(self, other):
        if isinstance(other, undarray):
            return self.nominal == other.nominal
        else:
            return self.nominal == numpy.asarray(other)

    def __ne__(self, other):
        if isinstance(other, undarray):
            return self.nominal != other.nominal
        else:
            return self.nominal != numpy.asarray(other)
    
    #
    # Keying methods ...
    #
    
    def __getitem__(self, key):
        """Returns the given subset of the undarray, by applying *key*
        both to the nominal value as well as to the Dependencies. """

        result = undarray(nominal=self.nominal[key])
        for dependency in self.dependencies:
            result.append(dependency[key])

    def __setitem__(self, key, value):
        """ Replace the portion of *self* indexed by *key* by *value*.

        If *value* is not an ``undarray``, it will be treated as the
        replacement for the specified portion of self's nominal value.

        *value* might be broadcast to fit the portion of *self*
        indexed by *key*. """

        self.clear(key)

        self.nominal = numpy.asarray(self.nominal)
            # Turn "true" scalars into scalar ndarrays prior to item
            # assignment.

        if isinstance(value, undarray):
            self.nominal[key] = value.nominal
                # Since we use key assignment, the shape of
                # ``self.nominal`` cannot grow.
            self.depend(other=value, key=key)
        else:
            self.nominal[key] = value

    def __len__(self):
        return len(self.nominal)

    #
    # ndarray methods, alphabetically sorted ...
    #
    
    def argmax(self, *args, **kwargs):
        """Refer to numpy.argmax() for documentation of the functionality."""

        return self.nominal.argmax(*args, **kwargs)

    def argmin(self, *args, **kwargs):
        """Refer to numpy.argmin() for documentation of the functionality."""

        return self.nominal.argmin(*args, **kwargs)

    def argsort(self, *args, **kwargs):
        """Refer to numpy.argsort() for documentation of the functionality."""

        return self.nominal.argsort(*args, **kwargs)

# It is difficult to match the semantics of ``clip``: What shall be
# the nominal value and the standard deviation of the result?  *Any
# possible value* is *probable*.  The implementation below, which
# sets the errors of clipped values to zero, in not precise by just
# ignoring the highly asymmetric and constrained pdf of a clipped
# Gaussian.
#
#    def clip(self, a_min, a_max):
#        """Refer to numpy.clip() for documentation of the functionality.
#        
#        The errors of the clipped values will be set to zero and any
#        dependency stored before in them will be removed.  Thus the clipped
#        values are then exact.
#        
#        Returned is a copy."""
#
#        # Retrieve the clipped nominal value.
#        clipped_nominal = self.nominal.clip(a_min, a_max)
#
#        # Retrieve the mask where to set the error to 0.0.
#        changed_mask = (self.nominal != clipped_nominal)
#
#        copied_characteristic = self.characteristic.copy()
#        copied_characteristic.clear(changed_mask)
#            # This statement finally boils down in :class:`Dependency`
#            # to:
#            #
#            #   >>> import numpy
#            #   >>> a = numpy.arange(10).reshape(2, 5)
#            #   >>> a
#            #   array([[0, 1, 2, 3, 4],
#            #          [5, 6, 7, 8, 9]])
#            #   >>> idx = (a % 2) == 0
#            #   >>> idx
#            #   array([[ True, False,  True, False,  True],
#            #          [False,  True, False,  True, False]], dtype=bool)
#            #   >>> a[idx]
#            #   array([0, 2, 4, 6, 8])
#            #   >>> a[idx] = -1
#            #   >>> a
#            #   array([[-1,  1, -1,  3, -1],
#            #          [ 5, -1,  7, -1,  9]])
#        return undarray(
#            nominal=clipped_nominal,
#            characteristic=copied_characteristic,
#        )

    def compress(self, *compress_args, **compress_kwargs):
        """Refer to numpy.compress() for documentation of the functionality."""

        result = undarray(
            nominal=self.nominal.compress(
                *compress_args, **compress_kwargs
            ))
        for dependency in self.dependencies:
            result.append(dependency.compress(
                *compress_args, **compress_kwargs
            ))
        return result

    def copy(self):
        """Returns a copy of the undarray.  Note that only the data is
        copied, and no new names for the dependencies are created.  This
        means, that the undarray will bahave in all arithmetics the same as
        the original, except for that it has its own memory.
        
        This behaviour is chosen, because there may happen too many
        complications with lost intercorrelations when the data would be
        dropped and replaced by new names completely.  Also, it cannot be
        decided at this program level which correlation to keep and which
        to "copy", i.e., to replicate with new names."""

        result = undarray(nominal=self.nominal.copy())
        for dependency in self.dependencies:
            result.append(dependency.copy())
        return result


# This method is deprecated, because its implementation is too rough.
# I feel it is better to _not_ provide an implementation when it
# cannot be done elegantly.
#
#X    def cumprod(self, axis=None):
#X        """Calculate the cumulative product along axis AXIS.  If AXIS is not
#X        given, perform the operation on the flattened array."""
#X
#X        if axis is None:
#X            # Promote the call to the flattened array.
#X            return self.flatten().cumprod(axis=0)
#X        
#X        else:
#X            # Perform an axis-wise operation ...
#X
#X            # Calculate the resulting shape.  Cut out the index at position
#X            # AXIS from the .shape attribute.
#X            result_shape = numpy.\
#X                    concatenate((self.shape[:axis], self.shape[axis + 1:]))
#X
#X            # Prepare the result undarray.
#X            result = uzeros(result_shape)
#X            
#X            # Perform the cumulative product calculation.
#X
#X            # Calculate the index position prefix:
#X            index_position_prefix = numpy.zeros(axis)
#X
#X            cumprod = 1.0  # Placeholder which will be immediately replaced
#X            for index in xrange(0, self.shape[axis]):
#X                # Calculate the index where to take data from and where to
#X                # put data:
#X                #
#X                # This indices are the same.  When AXIS == 0, 
#X                # *index_position_prefix* == [].  I.e., put data in the first
#X                # coordinate, and take data from the first coordinate.  When
#X                # *axis* == 1, *index_position_prefix* == [0].  I.e., put data
#X                # in the second coordinate, and take data from the second
#X                # coordinate.
#X                index_position = numpy.\
#X                        concatenate((index_position_prefix, [index]))
#X
#X                # Retrieve the current element:
#X                current_element = self[index_position]
#X
#X                # Multiply the CUMPROD variable by the current element.
#X                cumprod *= current_element
#X
#X                # Put the newly calculated element:
#X                result[index_position] = cumprod
#X
#X            # We're done!
#X            return result

    def flatten(self, *flatten_args, **flatten_kwargs):
        """Returns a copy with flatten()'ed arrays."""

        result = undarray(
            nominal=self.nominal.flatten(
                *flatten_args, **flatten_kwargs
            ))
        for dependency in self.dependencies:
            result.append(dependency.compress(
                *flatten_args, **flatten_kwargs
            ))
        return result

    def repeat(self, *repeat_args, **repeat_kwargs):
        """Returns a copy with repeat()'ed arrays."""

        result = undarray(
            nominal=self.nominal.repeat(
                *repeat_args, **repeat_kwargs
            ))
        for dependency in self.dependencies:
            result.appen(dependency.repeat(
                *repeat_arg, **repeat_kwargs
            ))
        return result

    def reshape(self, *reshape_args, **reshape_kwargs):
        """Returns a copy with reshape()'ed arrays."""

        result = undarray(
            nominal=self.nominal.reshape(
                *reshape_args, **reshape_kwargs
            ))
        for dependency in self.dependencies:
            result.append(dependency.reshape(
                *reshape_args, **reshape_kwargs
            ))
        return result

    def transpose(self, *transpose_args, **transpose_kwargs):
        """Returns a copy with transpos()'ed arrays."""

        result = undarray(
            nominal=self.nominal.transpose(
                *transpose_args, **transpose_kwargs
            ))
        for dependency in self.dependencies:
            result.append(dependency.transpose(
                *transpose_args, **transpose_kwargs
            ))
        return result

    #
    # String conversion ...
    #

    def __str__(self):
        typesetter = typesetting_context.current()
        return typesetter.typeset(self)

#X  To be adapted for upy2.
#X 
#X     def printable(self,
#X         stddevs, format=None, precision=None,
#X         infinite_precision=None,
#X         enforce_sign_value=None, enforce_sign_exponent=None,
#X     ):
#X         """Return a printable object created from this undarray instance.
#X         
#X         *stddevs* sigmas will be displayed as uncertainty (default 2).
#X         
#X         To enforce the printing of optional '+' signs in the value and the
#X         exponent, use ENFORCE_SIGN_VALUE and ENFORCE_SIGN_EXPONENT.  
#X         
#X         The three FORMATS supported are 'float', e.g. 0.120 +- 0.034, 'exp', 
#X         e.g.  (1.20 +- 0.34) 10^-1, and 'int', e.g. 12300 +- 4500.  By default,
#X         the format will be determined from the values and the uncertainties.
#X         The 'int' mode is choosen upon integer type of values and 
#X         uncertainties.  If the uncertainty is all-zero, the printing mode will 
#X         be determined from the value alone, else both must be integer to 
#X         enable int printing mode.
#X 
#X         PRECISION influences the precision of the output.  Generally, the 
#X         precision is determined from the uncertainty.  With PRECISION = 1, the 
#X         output will look like (1.0 +- 0.3), with PRECISION = 2, like 
#X         (1.00 +- 0.23).  If the uncertainty is zero, INFINITE_PRECISION will 
#X         be used instead, giving the number of digits behind the point, either 
#X         in float or exp mode.  In int mode all post-point digits are 
#X         suppressed.  If both the value and the uncertainty are zero, only 
#X         (0 +- 0) is printed.  The default PRECISION is 2.
#X         
#X         Note that you can affect the way the array is printed also by calling 
#X         numpy.set_printoptions()."""
#X 
#X         return upy2.printable.PrintableUndarray(self,
#X             stddevs=stddevs,
#X             enforce_sign_value=enforce_sign_value,
#X             enforce_sign_exponent=enforce_sign_exponent,
#X             format=format,
#X             precision=precision,
#X             infinite_precision=infinite_precision,
#X         )
#X 
#X     def __str__(self):
#X #X        """For scalar undarrays, return a useful print value of the value
#X #X        and the error.  For everything else, return some symbolic string."""
#X 
#X #        return str(self.printable())
#X         return "<undarray of shape %s>" % (self.shape)
#X 
#X     # No sensible repr(), because the object's interior is complex.


#
# uufuncs ...
#


# uufunc classes ...


class uufunc(object):
    """ uufuncs augment a numpy ufunc by propagation of
    uncertainties. """

    def __init__(self, ufunc):
        """ *ufunc* is the numpy ufunc calculating the nominal value
        of the resulting undarray. """

        self.ufunc = ufunc

    def __repr__(self):
        return "<%r uufunc>" % self.ufunc


class Unary(uufunc):
    def __call__(self, x):
        if isinstance(x, undarray):
            y = x.nominal
        else:
            y = x

        yout = self.ufunc(y)
        result = undarray(nominal=yout)
        if isinstance(x, undarray):
            result.depend(
                    other=x,
                    derivative=self._derivative(y),
            )
        return result


class Binary(uufunc):
    """The base class for binary uufuncs.  Derive binary uufunc classes
    from this class and define:

    *   :meth:`_derivative1` to provide the derivatives of the result
        w.r.t. the first operand, and

    *   likewise :meth:`_derivative2` for the derivatives w.r.t. the
        second operand.

    Opon calling the derived binary uufunc, :meth:`_derivative1` will
    only be called when the first operand is an ``undarray``, and
    likewise :meth:`_derivative2` will only be used when the second
    operand is an ``undarray``.

    The result of calling a binary uufunc is *always* an ``undarray``.
    """

    def __call__(self, x1, x2):
        """ Performs the operation on operands *x1* and *x2*. """

        if isinstance(x1, undarray):
            y1 = x1.nominal
        else:
            y1 = x1

        if isinstance(x2, undarray):
            y2 = x2.nominal
        else:
            y2 = x2

        yout = self.ufunc(y1, y2)
        result = undarray(nominal=yout)
        if isinstance(x1, undarray):
            result.depend(
                other=x1,
                derivative=self._derivative1(y1, y2),
            )
        if isinstance(x2, undarray):
            result.depend(
                other=x2,
                derivative=self._derivative2(y1, y2),
            )
        return result


# Protocol (Unary and Binary) implementations ...


def myabs(y):
    """ This function calculates the absolute value, and returns:

    *   A complex ndarray with negligible imaginary component for
        complex input;
    *   A float ndarray also for integer input.

    The second property is an (unwanted) side-effect. """

    ya = numpy.asarray(y)
    return numpy.sqrt(ya * ya.conj())

class Absolute(Unary):
    """ This implementation is probably flawed.  It shouldn't return
    Dependencies with non-zero imaginary components, as the absolute
    value is constrained to real numbers, and changing the input in
    any way never breaks this constraint. """

    def __init__(self):
        Unary.__init__(self, myabs)
            # We use :func:`myabs` because it returns complex-valued
            # ndarrays on complex-valued inputs.  This is necessary to
            # make sure the resulting undarray can hold the complex
            # Dependencies (undarray derives its dtype from the
            # nominal value).

    def _derivative(self, y):
        absolute_value = numpy.abs(y)
        absolute_prepared = absolute_value + (absolute_value == 0)
        nominal_prepared = y + (y == 0)
        normalisation_factor = absolute_prepared / nominal_prepared
            # For zero-valued input, the normalisation factor turns
            # out as 1.  This is important to make sure that the
            # dependencies are propagated without change.  For
            # non-zero input, the normalisation factor is always a
            # (possibly complex) number of unit magnitude.
            #
            # For example, consider *y* as ``0 + 2j``.  Then the
            # absolute value (2.0) results from multiplying *y* with
            # ``0 - 1j``.  Hence the normalised undarray depends on
            # the operand with a derivative of this ``0 - 1j`` figure.
            # This value is precisely the *normalisation_factor*
            # defined above: absolute value divided by *y*
            # (essentially).
            #
            # The reader might want to examine some more examples: ``1
            # + 1j``, ``5j``, ``-5``, ...
        return normalisation_factor
            # Another notation for the same outcome would be::
            #
            #   return (self * normalisation_factor).real
            #
            # with the ``.real`` statement to ignore the negligible
            # imaginary components of the product.
            #
        # For complex undarrays, the ``absolute_value`` is guaranteed
        # to be real-valued.  However, the dependencies might turn out
        # complex, when their phases differ from the phase of
        # ``self.nominal``.
        #
        #    Even in case the phases match, the resulting Dependency
        # derivatives turn out complex, although with very small
        # imaginary component.  In such a case, the user might
        # request the ``.real`` property of ``self``.


class Negative(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.negative)

    def _derivative(self, y):
        return -1


class Add(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.add)

    def _derivative1(self, y1, y2):
        return 1

    def _derivative2(self, y1, y2):
        return 1


class Subtract(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.subtract)

    def _derivative1(self, y1, y2):
        return 1

    def _derivative2(self, y1, y2):
        return -1


class Multiply(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.multiply)

    def _derivative1(self, y1, y2):
        return y2

    def _derivative2(self, y1, y2):
        return y1


class Divide(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.true_divide)

    def _derivative1(self, y1, y2):
        return numpy.true_divide(1, y2)

    def _derivative2(self, y1, y2):
        # f = y1 / y2 = y1 . y2 ^ (-1)
        #
        # d_y2 f = y1 . (-1) y2 ^ (-2)
        #
        return numpy.true_divide(-y1, y2 ** 2)


class Power(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.power)

    def _derivative1(self, y1, y2):
        # f = b ^ x
        #
        # Return: d_b (b ^ x) = d_y1 (y1 ^ y2)
        #
        #
        # df
        # -- = d_b (b ^ x)
        # db
        #    = d_b (e ^ (ln b . x))
        #
        #    =      e ^ (x ln b) . d_b (x ln b)
        #
        #    =      b ^ x . (x / b)
        #
        #    =      b ^ (x - 1) . x
        return y2 * (y1 ** (y2 - 1))

    def _derivative2(self, y1, y2):
        # f = b ^ x
        #
        # Return: d_x (b ^ x) = d_y2 (y1 ^ y2)
        #
        #
        # df
        # -- = d_x (b ^ x)
        # dx
        #    = d_x (e ^ (x ln b))
        #
        #    =      e ^ (x ln b) . d_x(x ln b)
        #
        #    =      b ^ x . (ln b)
        return (y1 ** y2) * numpy.log(y1)


# The actual uufuncs ...


unegative = Negative()
uabsolute = Absolute()

uadd = Add()
usubtract = Subtract()
umultiply = Multiply()
udivide = Divide()

upower = Power()
