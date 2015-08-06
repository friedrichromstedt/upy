# Developed since: Jan 2010

import numpy
import upy
import upy.dependency
import upy.characteristic
import upy.printable
import warnings

__all__ = ['undarray', 'uzeros', 'asundarray']

"""The central module, implementing the uncertain ndarray: undarray."""

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

def uzeros(shape):
    """Returns a zero-undarray of shape *shape*.  All *shape* arguments 
    accepted by ``numpy.zeros()`` will be working."""

    return undarray(numpy.zeros(shape))

def zeros(shape):
    """Equivalent to :func:`uzeros`.
    
    This method will be deprecated in v0.5.  Use :func:`uzeros` instead."""

    warnings.warn(DeprecationWarning('zeros() will be deprecated in v0.5, '
        'use uzeros() instead')

    return uzeros(shape)

def asundarray(undarray_like):
    """ If *undarray_like* is *not* an :class:`undarray`, it will be
    fed to the constructor of :class:`undarray` in order to produce an
    undarray.  If, on the contrary, *undarray_like* is already an
    undarray instance, it will be returned without change. """

    if isinstance(undarray_like, undarray):
        return undarray_like
    return undarray(undarray_like)

#
# The central undarray class ...
#

class undarray:
    """Implements uncertain ndarrays.  The name is derived from
    numpy.ndarray. """

    def __init__(self,
            master = None,
            stddev = None,
            derivatives = None,
            characteristic = None,
            dtype = None,
            shape = None):
        """If *master* is an undarray, its content will be copied.
        
        If *derivatives* and *master* are not None, *derivatives* must
        be a list [(undarray instance: derivative), ...], giving the
        derivatives with that the new undarray depends on the
        undarrays.  *master* will be converted to an numpy.ndarray.

        If *stddev* and *master* aren't None, *master* and *stddev*
        will be converted to numpy.ndarrays.

        If *characteristic* and *master* are not None, *master* is
        converted to an numpy.ndarray, and the *characteristic* is
        copied.

        If *master* isn't None, but all other branches mentioned so far are not
        fulfilled, Mixed-Mode applies.  In this mode, *master* will not be 
        converted to an numpy.ndarray, but will be recursed into.  
        Nevertheless the objects comprising *master* must match the effective
        shape of the *master*.  *master* may be contain upy.undarrays.  The shape 
        of the new undarray is obtained from the first scalar element in the 
        upy.ravel()ed version of the *master* and from the lengthes of the 
        sequences containing that first element.  Scalars are objects for 
        which numpy.isscalar() returns True.  When there are shape 
        inconsistencies, an exception will occur.  If the first element is an 
        undarray, its shape will be taken into account.  In Mixed-Mode, the 
        *dtype* of the initially zero .value ndarray is either determined 
        automatically from all values contained in *master* and undarrays 
        therein, or can be given explicitly via *dtype*.  It is strongly 
        recommended to use *dtype*, because raveling large datasets can be very 
        expensive in memory and time both.
        
        If also *master* is None, *shape* is taken into account, to create a new,
        zero-valued undarray of dtype *dtype* (None means numpy.float).
        
        If none of these branches match, ValueError will be raised."""
        
        if isinstance(master, undarray):

            # Take over attributes from existing undarray ...
        
            self.value = master.value.copy()
            self.characteristic = master.characteristic.copy()

            self.shape = master.shape
            self.ndim = master.ndim

        elif derivatives is not None and master is not None:

            # Derive the new undarray from known ones ...

            self.value = numpy.asarray(master)
            self.shape = self.value.shape
            self.ndim = self.value.ndim

            # Create a new, empty Characteristic where we can fill in
            # the dependencies introduced by *derivatives*.
            self.characteristic = upy.characteristic.Characteristic(
                    shape=self.shape)

            # Fill in the dependencies.
            for (instance, derivative) in derivatives:
                self.characteristic += \
                        instance.characteristic * derivative

        elif stddev is not None and master is not None:
            
            # Constuct a new undarray ...

            # Convert to ndarrays.
            master = numpy.copy(master)
            stddev = numpy.copy(stddev)

            # Check shape.
            if master.shape != stddev.shape:
                raise ValueError("Shape mismatch between *master* and '
                    '*stddev*.  Shapes are: *master* - %s, *stddev* - %s" % \
                    (master.shape, stddev.shape))

            self.value = master

            self.shape = self.value.shape
            self.ndim = self.value.ndim
            
            # Create Dependency instance from scratch.
            dependency = upy.dependency.Dependency(
                    names=upy.id_generator.get_id(
                        shape=self.shape),
                    derivatives=stddev)

            self.characteristic = upy.characteristic.Characteristic(
                shape=self.shape,
            )
            self.characteristic.append(dependency)

        elif characteristic is not None and master is not None:
            
            # Take over characteristic ...

            self.value = numpy.asarray(master)
            self.characteristic = characteristic.copy()

            self.shape = self.value.shape
            self.ndim = self.value.ndim

        elif master is not None:

            # Construct a new undarray with an empty Characteristic.

            master = numpy.asarray(master)
            self.value = master

            self.shape = self.value.shape
            self.ndim = self.value.ndim

            self.characteristic = upy.characteristic.Characteristic(
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

            if not isinstance(shape, tuple):
                raise ValueError("SHAPE must be tuple.")

            self.value = numpy.zeros(shape, dtype=dtype)
            self.characteristic = upy.characteristic.Characteristic(
                    shape=tuple(shape))

            self.shape = self.value.shape
            self.ndim = self.value.ndim

        else:
            
            raise ValueError("Don't know how to initialise an undarray from the arguments given.")
        
    #
    # Methods to obtain net quantities ...
    #

    @property
    def variance(self):
        """Returns the variance array, i.e., sigma ** 2."""

        warnings.warn(DeprecationWarning('undarray.variance is a property '
            'since >v0.4.11b, if you call it your program will fail')
        return self.characteristic.variance

    def sigma(self):
        """Returns the sigma array, i.e., the square root of the variance.
        
        This method will be deprecated in v0.5, use :meth:`~undarray.stddev` 
        instead."""

        warnings.warn(DeprecationWarning('undarray.sigma() will be deprecated '
            'in v0.5, use undarray.stddev instead')
        return numpy.sqrt(self.variance)

    def dispersion(self):
        """Returns the dispersion, i.e., the sigma.
        
        This method will be deprecated in v0.5, use :meth:`~undarray.stddev`
        instead."""

        warnings.warn(DeprecationWarning('undarray.dispersion() will be '
            'deprecated in v0.5, use undarray.stddev instead')
        return numpy.sqrt(self.variance)
    
    @property
    def stddev(self):
        """Returns the standard deviation."""
        
        return numpy.sqrt(self.variance)

    def error(self):
        """Returns the error, i.e., 2 * sigma.
        
        This method will be deprecated in v0.5, use ``2 * ua.stddev`` 
        instead."""

        warnings.warn(DeprecationWarning('undarray.error() will be '
            'deprecated in v0.5, use 2 * undarray.stddev instead')

        return 2 * self.stddev
    
    def uncertainty(self, sigmas):
        """Returns ``sigmas * self.stddev``.
        
        This method will be deprecated by v0.5, please use explicit
        multiplication instead."""

        warnings.warn(DeprecationWarning('undarray.uncertainty() will be '
            'deprecated by v0.5, please use explicit multiplication instead')

        return sigmas * self.stddev

    def weight(self):
        """Returns a numpy.ndarray suitable for weighting this undarray.
        The weights are 1.0 / .variance().  When a variance element is
        zero, the used variance is 1.0.
        
        This method will be deprecated in v0.5, use ``1 / ua.variance()``
        directly."""
        
        warnings.warn(DeprecationWarning('undarray.weight() will be '
            'deprecated in v0.5, use 1 / ua.variance() instead')
        
        # Calculate the variance used.
        used_variance = self.variance()
        used_variance += 1.0 * (used_variance == 0.0)

        # Calculate the weight from the variance.
        return 1.0 / used_variance

    #
    # Binary arithmetics ...
    #

    def __add__(self, other):
        if isinstance(other, undarray):
            return undarray(
                    object = self.value + other.value,
                    derivatives = [(self, 1.0), (other, 1.0)])
        else:
            return undarray(
                    object = self.value + other,
                    derivatives = [(self, 1.0)])

    def __sub__(self, other):
        if isinstance(other, undarray):
            return undarray(
                    object = self.value - other.value,
                    derivatives = [(self, 1.0), (other, -1.0)])
        else:
            return undarray(
                    object = self.value - other,
                    derivatives = [(self, 1.0)])

    def __mul__(self, other):
        if isinstance(other, undarray):
            return undarray(
                    object = self.value * other.value,
                    derivatives = [(self, other.value), (other, self.value)])
        else:
            return undarray(
                    object = self.value * other,
                    derivatives = [(self, other)])

    def __div__(self, other):
        if isinstance(other, undarray):
            return self * (1.0 / other)
        else:
            return self * (1.0 / numpy.asarray(other))

    def __pow__(self, other):
        if isinstance(other, undarray):
            self_pow_other = self.value ** other.value
            return undarray(
                    object = self_pow_other,
                    derivatives = \
                        [(self, self.value ** (other.value - 1) * other.value),
                         (other, self_pow_other * numpy.log(self.value))])

        else:
            other = numpy.asarray(other)
            return undarray(
                    object = self.value ** other,
                    derivatives = \
                        [(self, self.value ** (other - 1) * other)])

    #
    # Reverse binary arithmetics ...
    #

    def __radd__(self, other):
        # OTHER is not an undarray.
        return undarray(
                object = other + self.value,
                derivatives = [(self, 1.0)])

    def __rsub__(self, other):
        # OTHER is not an undarray.
        return undarray(
                object = other - self.value,
                derivatives = [(self, -1.0)])

    def __rmul__(self, other):
        # OTHER is not an undarray.
        return undarray(
                object = other * self.value,
                derivatives = [(self, other)])

    def __rdiv__(self, other):
        # OTHER is not an undarray.
        other = numpy.asarray(other)
        return undarray(
                object = other / self.value,
                derivatives = [(self, -other / self.value ** 2)])

    def __rpow__(self, other):
        # OTHER is not an undarray.
        other_pow_self = other ** self.value
        return undarray(
                object = other_pow_self,
                derivatives = \
                        [(self, other_pow_self * numpy.log(other))])

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
                object = -self.value,
                derivatives = [(self, -1)])

    def __abs__(self):
        """This works for real-valued undarrays."""
        
        # Calculate an inversion mask ...

        inversion_mask = numpy.ones(shape = self.value.shape)
        inversion_mask -= 2 * (self.value < 0)

        # Invert values which must be inverted, and invert also the dependency
        # of this values on the error source ...

        return self * inversion_mask
    
    #
    # Casts to int, float, ... are impossible, because we have ndarray values.
    #

    #
    # Comparison operators ...
    #

    def __lt__(self, other):
        if isinstance(other, undarray):
            return self.value < other.value
        else:
            return self.value < other

    def __le__(self, other):
        if isinstance(other, undarray):
            return self.value <= other.value
        else:
            return self.value <= other

    def __gt__(self, other):
        if isinstance(other, undarray):
            return self.value > other.value
        else:
            return self.value > other

    def __ge__(self, other):
        if isinstance(other, undarray):
            return self.value >= other.value
        else:
            return self.value >= other

    def __eq__(self, other):
        if isinstance(other, undarray):
            return self.value == other.value
        else:
            return self.value == other

    def __ne__(self, other):
        if isinstance(other, undarray):
            return self.value != other.value
        else:
            return self.value != other
    
    #
    # Keying methods ...
    #
    
    def __getitem__(self, key):
        """Returns the given subset of the undarray array, by applying the
        KEY both to the value and the Characteristic. """

        return undarray(
                object=self.value[key],
                characteristic = self.characteristic[key])

    def __setitem__(self, key, value):
        """ Updates the given subset of the undarray array, by
        replacing the value's subset and the Characteristic's subset
        indexed by *key*. """

        # Handle scalar indices ...
        if key is None:
            key = ()
        elif not isinstance(key, tuple):
                # If *key* is None, it shall stay None.  *None* is a
                # special key to :meth:`Dependency.add` resulting in
                # indexing the whole object (``key = ()``).
            key = (key,)

        if isinstance(value, undarray):
            # Update with a undarray subset ...

            # The possibility of broadcasting *value* is a feature.
            # The code performing the broadcast for
            # ``self.characteristic`` is in dependency.py,
            # :meth:`Dependency.add`.

            # Possibly "upgrade" ``self.value``\ 's dtype  ...
            if self.value.dtype != value.value.dtype:
                self.value = self.value + numpy.zeros([],
                    dtype=value.value.dtype)
                    # cf. dependency.py: Dependency.add().
            # From now on, the dtype of ``self.value`` is large enough
            # to hold the *value*\ 's nominal value.

            # Update the respective subsets ...

            self.value[key] = value.value
            self.characteristic[key] = value.characteristic

        elif isinstance(value, numpy.ndarray):
            # Set errorless values from the ndarray *value* ...

            # The ability to broadcast *value* is a feature; in that
            # case *value*\ 's shape differs from ``self.shape``.  We
            # do not apply any check as numpy will complain itself
            # when the shape of *value* is too large.  Since we use
            # key assignment, the shape of ``self.value`` and of
            # ``self.characteristic`` cannot grow during the
            # operation.

            if self.value.dtype != value.dtype:
                self.value = self.value + numpy.zeros([],
                    dtype=value.dtype)
            self.characteristic.clear(key)
            self.value[key] = value
        
        else:
            # Update in mixed-mode ...

            if len(key) == self.ndim:

                # We have reached the innermost level, set the values ...
                #
                # VALUE is definitely not an undarray.
                value = numpy.asarray(value)
                self[key] = value
                    # With *value* now being an instance of
                    # ``numpy.ndarray``, the corresponding branch
                    # above is used.

            else:
                    
                # VALUE is definitely not an undarray.

                # Iterate through VALUE ...

                # Check length.
                if len(value) != self.shape[len(key)]:
                    raise ValueError('Shape mismatch.')

                # Iterate.
                for idx in xrange(0, len(value)):
                    subkey = tuple(list(key) + [idx])
                    self[subkey] = value[idx]
        
    def __len__(self):
        return len(self.value)

    #
    # ndarray methods, alphabetically sorted ...
    #
    
    def argmax(self, *args, **kwargs):
        """Refer to numpy.argmax() for documentation of the functionality."""

        return self.value.argmax(*args, **kwargs)

    def argmin(self, *args, **kwargs):
        """Refer to numpy.argmin() for documentation of the functionality."""

        return self.value.argmin(*args, **kwargs)

    def argsort(self, *args, **kwargs):
        """Refer to numpy.argsort() for documentation of the functionality."""

        return self.value.argsort(*args, **kwargs)

    def clip(self, a, a_min, a_max):
        """Refer to numpy.clip() for documentation of the functionality.
        
        The errors of the clipped values will be set to zero and any
        dependency stored before in them will be removed.  Thus the clipped
        values are then exact.
        
        Returned is a copy."""

        # Retrieve the clipped value.
        clipped_value = self.value.clip(a_min, a_max)

        # Retrieve the mask of values where to set the error to 0.0.
        changed_mask = (self.value != clipped_value)
        
        # Retrieve the clipped undarray ...

        # Work on a copy.
        copy = self.copy()

        # Set the value of the undarray to the clipped values.
        copy.value = clipped_value

        # Clear the error for all masked elemeents.
        copy.characteristic.clear(changed_mask)

    def compress(self, *compress_args, **compress_kwargs):
        """Refer to numpy.compress() for documentation of the functionality."""

        object = self.value.compress(
                *comress_args, **compress_kwargs)
        return undarray(
                object=object,
                characteristic=self.characteristic.compress(
                    new_shape=object.shape,
                    *compress_args, **compress_kwargs))

    def copy(self):
        """Returns a copy of the undarray.  Note that only the data is
        copied, and no new names for the dependencies are created.  This
        means, that the undarray will bahave in all arithmetics the same as
        the original, except for that it has its own memory.
        
        This behaviour is choosen, because there may happen too many
        complications with lost intercorrelations when the data would be
        dropped and replaced by new names completely.  Also, it cannot be
        decided at this program level which correlation to keep and which
        to "copy", i.e., to replicate with new names."""

        return undarray(
                object=self.value.copy(),
                characteristic=self.characteristic.copy())

    def cumprod(self, axis=None):
        """Calculate the cumulative product along axis AXIS.  If AXIS is not
        given, perform the operation on the flattened array."""

        if axis is None:
            # Promote the call to the flattened array.
            return self.flatten().cumprod(axis=0)
        
        else:
            # Perform an axis-wise operation ...

            # Calculate the resulting shape.  Cut out the index at position
            # AXIS from the .shape attribute.
            result_shape = numpy.\
                    concatenate((self.shape[:axis], self.shape[axis + 1:]))

            # Prepare the result undarray.
            result = uzeros(result_shape)
            
            # Perform the cumulative product calculation.

            # Calculate the index position prefix:
            index_position_prefix = numpy.zeros(axis)

            cumprod = 1.0  # Placeholder which will be immediately replaced
            for index in xrange(0, self.shape[axis]):
                # Calculate the index where to take data from and where to
                # put data:
                #
                # This indices are the same.  When AXIS == 0, 
                # *index_position_prefix* == [].  I.e., put data in the first
                # coordinate, and take data from the first coordinate.  When
                # *axis* == 1, *index_position_prefix* == [0].  I.e., put data
                # in the second coordinate, and take data from the second
                # coordinate.
                index_position = numpy.\
                        concatenate((index_position_prefix, [index]))

                # Retrieve the current element:
                current_element = self[index_position]

                # Multiply the CUMPROD variable by the current element.
                cumprod *= current_element

                # Put the newly calculated element:
                result[index_position] = cumprod

            # We're done!
            return result

    def flatten(self, *flatten_args, **flatten_kwargs):
        """Returns a copy with flatten()'ed arrays."""

        object = self.value.flatten(
                *flatten_args, **flatten_kwargs)
        return undarray(
                object = object,
                characteristic = self.characteristic.flatten(
                    new_shape = object.shape,
                    *flatten_args, **flatten_kwargs))

    def repeat(self, *repeat_args, **repeat_kwargs):
        """Returns a copy with repeat()'ed arrays."""

        object = self.value.repeat(
                *repeat_args, **repeat_kwargs)
        return undarray(
                object = object,
                characteristic = self.characteristic.repeat(
                    new_shape = object.shape,
                    *repeat_args, **repeat_kwargs))

    def reshape(self, *reshape_args, **reshape_kwargs):
        """Returns a copy with reshape()'ed arrays."""

        object = self.value.reshape(
                *reshape_args, **reshape_kwargs)
        return undarray(
                object = object,
                characteristic = self.characteristic.reshape(
                    new_shape = object.shape,
                    *reshape_args, **reshape_kwargs))

    def transpose(self, *transpose_args, **transpose_kwargs):
        """Returns a copy with transpos()'ed arrays."""

        object = self.value.transpose(
                *transpose_args, **transpose_kwargs)
        return undarray(
                object = object,
                characteristic = self.characteristic.transpose(
                    new_shape = object.shape,
                    *transpose_args, **transpose_kwargs))

    #
    # String conversion ...
    #
    
    def printable(self, sigmas = None,
            enforce_sign_value = None, enforce_sign_exponent = None,
            format = None,
            precision = None, infinite_precision = None):
        """Return a printable object created from this undarray instance.
        
        SIGMA sigmas will be displayed as uncertainty (default 2).  
        
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
        be used instead, giving the number of digits behind the point, either 
        in float or exp mode.  In int mode all post-point digits are 
        suppressed.  If both the value and the uncertainty are zero, only 
        (0 +- 0) is printed.  The default PRECISION is 2.
        
        Note that you can affect the way the array is printed also by calling 
        numpy.set_printoptions()."""

        return upy.printable.PrintableUndarray(self,
                sigmas = sigmas,
                enforce_sign_value = enforce_sign_value,
                enforce_sign_exponent = enforce_sign_exponent,
                format = format,
                precision = precision,
                infinite_precision = infinite_precision)

    def __str__(self):
        """For scalar undarrays, return a useful print value of the value
        and the error.  For everything else, return some symbolic string."""

        return str(self.printable())

    # No sensible repr(), because the object's interior is complex.
