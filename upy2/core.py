# Developed since: Jan 2010

"""The central upy2 module, implementing the uncertain ndarray:
:class:`undarray`."""

import numpy
import upy2
import upy2.dependency
import upy2.characteristic
import upy2.typesetting.protocol
import upy2.context
#import upy2.printable
import warnings

__all__ = ['undarray', 'uzeros', 'asuarray', 'U', 'u', 'ucopy']

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
        """ Provides an undarray with zero nominal value and a
        dispersion based on *error*.  *error* is interpreted as a
        multiple of the standard deviation as defined on
        initialisation time. """

        stddev = numpy.asarray(error) / self.stddevs
        return undarray(
            nominal=numpy.zeros_like(stddev),
            stddev=stddev,
        )

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
        
#X        if isinstance(master, undarray):
#X
#X            # Take over attributes from existing undarray ...
#X        
#X            self.value = master.value.copy()
#X            self.characteristic = master.characteristic.copy()
#X
#X            self.shape = master.shape
#X            self.ndim = master.ndim
#X
#X        elif derivatives is not None and master is not None:

        # Attributes to initialise:
        #
        # - self.nominal
        # - self.shape
        # - self.ndim
        # - self.characteristic

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

            self.shape = self.nominal.shape
            self.ndim = self.nominal.ndim

            self.characteristic = upy2.characteristic.Characteristic(
                shape=self.shape,
            )
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

            self.shape = self.nominal.shape
            self.ndim = self.nominal.ndim

            self.characteristic = upy2.characteristic.Characteristic(
                shape=self.shape,
            )

        else:
            
            raise ValueError("Cannot initialise an undarray from the arguments given.")
        
    #
    # Properties ...
    #

    @property
    def real(self):
        """ Returns the real component of *self*.  This pertains to
        the nominal value as well as the Characteristic. """

        return undarray(
            nominal=self.nominal.real.copy(),
            characteristic=self.characteristic.real,
        )

    @property
    def imag(self):
        """ Returns the imaginary component of *self*.  This pertains to
        the nominal value as well as the Characteristic. """

        return undarray(
            nominal=self.nominal.imag.copy(),
            characteristci=self.characteristic.imag,
        )

    @property
    def variance(self):
        """Returns the variance array, i.e., stddev ** 2."""

#?        warnings.warn(DeprecationWarning('undarray.variance is a property '
#?            'since >v0.4.11b, if you call it your program will fail')
        return self.characteristic.variance

#?    def sigma(self):
#?        """Returns the sigma array, i.e., the square root of the variance.
#?        
#?        This method will be deprecated in v0.5, use :meth:`~undarray.stddev` 
#?        instead."""
#?
#?        warnings.warn(DeprecationWarning('undarray.sigma() will be deprecated '
#?            'in v0.5, use undarray.stddev instead')
#?        return numpy.sqrt(self.variance)
#?
#?    def dispersion(self):
#?        """Returns the dispersion, i.e., the sigma.
#?        
#?        This method will be deprecated in v0.5, use :meth:`~undarray.stddev`
#?        instead."""
#?
#?        warnings.warn(DeprecationWarning('undarray.dispersion() will be '
#?            'deprecated in v0.5, use undarray.stddev instead')
#?        return numpy.sqrt(self.variance)
    
    @property
    def stddev(self):
        """Returns the standard deviation."""
        
        return numpy.sqrt(self.variance)
            # In case of complex dependencies, retrieving
            # self.variance will fail when in the code path of
            # the :class:`Dependency` instance exhibiting complex
            # derivatives.

#?    def error(self):
#?        """Returns the error, i.e., 2 * sigma.
#?        
#?        This method will be deprecated in v0.5, use ``2 * ua.stddev`` 
#?        instead."""
#?
#?        warnings.warn(DeprecationWarning('undarray.error() will be '
#?            'deprecated in v0.5, use 2 * undarray.stddev instead')
#?
#?        return 2 * self.stddev
#?    
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
        if isinstance(other, undarray):
            return undarray(
                nominal=(self.nominal + other.nominal),
                derivatives=[(self, 1.0), (other, 1.0)],
            )
        else:
            return undarray(
                nominal=(self.nominal + other),
                derivatives=[(self, 1.0)],
            )

    def __sub__(self, other):
        if isinstance(other, undarray):
            return undarray(
                nominal=(self.nominal - other.nominal),
                derivatives=[(self, 1.0), (other, -1.0)],
            )
        else:
            return undarray(
                nominal=(self.nominal - other),
                derivatives=[(self, 1.0)],
            )

    def __mul__(self, other):
        if isinstance(other, undarray):
            return undarray(
                nominal=(self.nominal * other.nominal),
                derivatives=[(self, other.nominal), (other, self.nominal)],
            )
        else:
            return undarray(
                nominal=(self.nominal * other),
                derivatives=[(self, other)],
            )

    def __div__(self, other):
        if isinstance(other, undarray):
            return self * (1.0 / other)
                          # calls other.__rdiv__()
        else:
            return self * (1.0 / numpy.asarray(other))

    def __pow__(self, other):
        # f = b ^ x         b = self    x = other
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
        if isinstance(other, undarray):
            self_pow_other = self.nominal ** other.nominal
            return undarray(
                nominal=self_pow_other,
                derivatives=\
                    [(self, self.nominal ** (other.nominal - 1) * \
                        other.nominal),
                     (other, self_pow_other * numpy.log(self.nominal))],
            )

        else:
            other = numpy.asarray(other)
            return undarray(
                nominal=(self.nominal ** other),
                derivatives=[(self, self.nominal ** (other - 1) * other)],
            )

    #
    # Reflected binary arithmetics ...
    #

    def __radd__(self, other):
        # *other* is not an undarray.
        other=numpy.asarray(other)
        return undarray(
            nominal=(other + self.nominal),
            derivatives=[(self, 1.0)],
        )

    def __rsub__(self, other):
        # *other* is not an undarray.
        other=numpy.asarray(other)
        return undarray(
            nominal=(other - self.nominal),
            derivatives=[(self, -1.0)],
        )

    def __rmul__(self, other):
        # *other* is not an undarray.
        other=numpy.asarray(other)
        return undarray(
            nominal=(other * self.nominal),
            derivatives=[(self, other)],
        )

    def __rdiv__(self, other):
        # *other* is not an undarray.
        other=numpy.asarray(other)
        #
        # f = other / self = other . self ^ (-1)
        #
        # d_self f = other . (-1) . self ^ (-2) 
        #
        return undarray(
            nominal=(other / self.nominal),
            derivatives=[(self, -other / self.nominal ** 2)],
        )

    def __rpow__(self, other):
        # *other* is not an undarray.
        other=numpy.asarray(other)
        other_pow_self = other ** self.nominal
        # See :meth:`__pow__`.
        return undarray(
            nominal=other_pow_self,
            derivatives=[(self, other_pow_self * numpy.log(other))],
        )

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
            nominal=(-self.nominal),
            derivatives=[(self, -1)])

    def __abs__(self):
        absolute_value = numpy.abs(self.nominal)
        nominal_prepared = self.nominal + (self.nominal == 0)
        normalisation_factor = absolute_value / nominal_prepared
            # Consider *self.nominal* as 0 + 1j.  Then the absolute
            # value (1.0) results from multiplying *self.nominal* with
            # 0 - 1j.  Hence the normalised undarray depends on the
            # previous *self.nominal* with a derivative of this 0 - 1j
            # figure.  This value is precisely the
            # *normalisation_factor* defined above: absolute value
            # divided by *self.nominal*.
            #
            # The reader might want to verify this finding by more
            # examples: 1 + 1j, 5j, -5, ...
            #
            # When an element of self.nominal is zero, its absolute
            # value is zero as well, and the 1.0 introduced in
            # ``nominal_prepared`` is effectless:  The normalisation
            # factor turns out as zero.
        return undarray(
            nominal=absolute_value,
            derivatives=[(self, normalisation_factor)],
                # Notice that *normalisation_factor* is not a scalar.
        )
            # Another notation for the same outcome would be::
            #
            #   return (self * normalisation_factor).real
            #
            # with the ``.real`` statement to ignore the negligible
            # imaginary components of the product.
            #
        # For complex undarrays, the ``absolute_value`` is guaranteed
        # to be real-valued.  However, the dependencies might turn out
        # complex, when their phase differs from the phase of
        # ``self.nominal``.
        #
        #    Even in case the phases match, the resulting Dependency
        # derivatives turn out complex, although with very small
        # imaginary component.  In such a case, the user might
        # request the ``.real`` property of ``self``.

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
        """Returns the given subset of the undarray array, by applying
        *key* both to the nominal value as well as to the
        Characteristic. """

        return undarray(
            nominal=self.nominal[key],
            characteristic = self.characteristic[key],
        )

    def __setitem__(self, key, value):
        """ Updates the given subset of the undarray, by replacing the
        subset of the nominal value and the Characteristic's subset
        indexed by *key*.  *value* can be an ``undarray`` instance; if
        it isn't it will be passed through ``numpy.asarray``. """

#XX        # Handle scalar indices ...
#XX        if key is None:
#XX            key = ()
#XX        elif not isinstance(key, tuple):
#XX                # If *key* is None, it shall stay None.  *None* is a
#XX                # special key to :meth:`Dependency.add` resulting in
#XX                # indexing the whole object (``key = ()``).
#XX            key = (key,)

        if isinstance(value, undarray):
            # Update with a undarray subset ...

            # The possibility of broadcasting *value* is a feature.
            # The code performing the broadcast for
            # ``self.characteristic`` is in dependency.py,
            # :meth:`Dependency.add`.

            # Possibly "upgrade" ``self.value``\ 's dtype  ...
            if self.nominal.dtype != value.nominal.dtype:
                self.nominal = self.nominal + numpy.zeros([],
                    dtype=value.nominal.dtype)
                    # cf. dependency.py: Dependency.add().
            # From now on, the dtype of ``self.nominal`` is large enough
            # to hold the *value*\ 's nominal value.

            # Update the respective subsets ...

            self.nominal = numpy.asarray(self.nominal)
                # Turn "true" scalars into scalar ndarrays prior to
                # item assignment.
            self.nominal[key] = value.nominal
            self.characteristic[key] = value.characteristic

#XX        elif isinstance(value, numpy.ndarray):
        else:
            value = numpy.asarray(value)
                # We do not copy because the *value* isn't stored
                # anywhere inside this ``undarray`` instance; it is
                # used in a key assignment below.
            # Set errorless values from the ndarray *value* ...

            # The ability to broadcast *value* is a feature; in that
            # case *value*\ 's shape differs from ``self.shape``.  We
            # do not apply any check as numpy will complain itself
            # when the shape of *value* is too large.  Since we use
            # key assignment, the shape of ``self.nominal`` and of
            # ``self.characteristic`` cannot grow during the
            # operation.

            if self.nominal.dtype != value.dtype:
                self.nominal = self.nominal + numpy.zeros([],
                    dtype=value.dtype)
            self.characteristic.clear(key)
            self.nominal = numpy.asarray(self.nominal)
                # Turn "true" scalars into scalar ndarrays prior to
                # item assignment.
            self.nominal[key] = value
#XX        
#XX        else:
#XX            # Update in mixed-mode ...
#XX
#XX            if len(key) == self.ndim:
#XX
#XX                # We have reached the innermost level, set the values ...
#XX                #
#XX                # VALUE is definitely not an undarray.
#XX                value = numpy.asarray(value)
#XX                self[key] = value
#XX                    # With *value* now being an instance of
#XX                    # ``numpy.ndarray``, the corresponding branch
#XX                    # above is used.
#XX
#XX            else:
#XX                    
#XX                # VALUE is definitely not an undarray.
#XX
#XX                # Iterate through VALUE ...
#XX
#XX                # Check length.
#XX                if len(value) != self.shape[len(key)]:
#XX                    raise ValueError('Shape mismatch.')
#XX
#XX                # Iterate.
#XX                for idx in xrange(0, len(value)):
#XX                    subkey = tuple(list(key) + [idx])
#XX                    self[subkey] = value[idx]
        
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

        return undarray(
            nominal=self.nominal.compress(
                *comress_args, **compress_kwargs
            ),
            characteristic=self.characteristic.compress(
                *compress_args, **compress_kwargs
            ),
        )

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

        return undarray(
            nominal=self.nominal.copy(),
            characteristic=self.characteristic.copy(),
        )
            

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

        return undarray(
            nominal=self.nominal.flatten(
                *flatten_args, **flatten_kwargs
            ),
            characteristic=self.characteristic.flatten(
                *flatten_args, **flatten_kwargs
            ),
        )

    def repeat(self, *repeat_args, **repeat_kwargs):
        """Returns a copy with repeat()'ed arrays."""

        return undarray(
            nominal=self.nominal.repeat(
                *repeat_args, **repeat_kwargs
            ),
            characteristic=self.characteristic.repeat(
                *repeat_args, **repeat_kwargs
            ),
        )

    def reshape(self, *reshape_args, **reshape_kwargs):
        """Returns a copy with reshape()'ed arrays."""

        return undarray(
            nominal=self.nominal.reshape(
                *reshape_args, **reshape_kwargs
            ),
            characteristic=self.characteristic.reshape(
                *reshape_args, **reshape_kwargs
            ),
        )

    def transpose(self, *transpose_args, **transpose_kwargs):
        """Returns a copy with transpos()'ed arrays."""

        return undarray(
            nominal=self.nominal.transpose(
                *transpose_args, **transpose_kwargs
            ),
            characteristic=self.characteristic.transpose(
                *transpose_args, **transpose_kwargs
            ),
        )

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
