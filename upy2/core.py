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
    'unegative', 'uabsolute', 'usqrt', 'usquare',
    'usin', 'ucos', 'utan', 'uarcsin', 'uarccos', 'uarctan',
    'usinh', 'ucosh', 'utanh', 'uarcsinh', 'uarccosh', 'uarctanh',
    'uexp', 'uexp2', 'ulog', 'ulog2', 'ulog10',
    'uadd', 'usubtract', 'umultiply', 'udivide', 'upower',
    'uarctan2']

typesetting_context = upy2.context.byprotocol(
    upy2.typesetting.protocol.Typesetter)

#
# Some convenience functions ...
#

def uzeros(shape, dtype=None):
    """ Returns a zero-undarray of shape *shape* and optionally using
    dtype *dtype*.  All *shape* arguments accepted by
    ``numpy.zeros()`` will work. """

    return undarray(shape=shape, dtype=dtype)

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
            dtype=None,
            shape=None):
        """ To initialise an :class:`undarray` instance, a
        specification of the nominal value is required.  This can be
        given in two ways:

        1.  By providing *nominal*; or
        2.  by providing *shape*.

        In either way, the ``dtype`` of the resulting ``undarray`` can
        be overridded by *dtype*.  Providing *shape* and leaving
        *nominal* ``None`` will create a zero-filled nominal value.
        *shape* is ignored when *nominal* is given.  The shape of the
        nominal value ndarray will serve as the shape of the
        ``undarray``.

        Optionally, *stddev* can be provided to define initial
        uncertainties of the new ``undarray``.  There will be no
        correlation of the uncertainties created this way, neither
        within in new ``undarray`` nor with elements of other
        ``undarray`` instances.  The shape of *stddev* needs to
        coincide with the shape of the ``undarray`` created. """

        if nominal is None and shape is not None:
            nominal = numpy.zeros(shape=shape, dtype=dtype)

        if nominal is None:
            raise ValueError("Missing nominal value specification")

        self.dependencies = []
        self.nominal = numpy.asarray(nominal, dtype=dtype)
        self.shape = self.nominal.shape
        self.dtype = self.nominal.dtype
        self.ndim = self.nominal.ndim

        if stddev is not None:
            # Create a Dependendy instance from scratch.
            dependency = upy2.dependency.Dependency(
                    names=upy2.id_generator.get_idarray(
                        shape=self.shape),
                    derivatives=stddev,
            )   # The Dependency constructor doesn't copy the data
                # given.
            self.append(dependency)

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

    def scaled(self, factor):
        """ This method implements the operation ``ua * factor``,
        where *factor* isn't another undarray.  This is used to
        implement multiplication within :class:`Multiply`. """

        factor_dtype = numpy.result_type(factor)
        result_dtype = numpy.result_type(factor_dtype, self.dtype)

        result = undarray(nominal=(self.nominal * factor))

        for dependency in self.dependencies:
            result.append(dependency * factor)

        return result

    def copy_dependencies(self, source, key=None):
        """ *source* is an ``undarray`` whose ``Dependencies`` will be
        incorporated into *self*.  *key* indexes *self* and determines
        the location where the ``Dependencies`` of *source* will be
        added. """

        # Check dtype compatibility ...

        if not numpy.can_cast(source.dtype, self.dtype):
            raise ValueError(
                    ('Cannot incorporate the dependencies of an '
                     '{0}-dtype undarray into an {1}-dtype undarray')\
                             .format(source.dtype, self.dtype))

        # Incorporate the Dependecies of *source* ...

        for dependency in source.dependencies:
            # First, everything is left:
            remnant = dependency

            for target in self.dependencies:
                if remnant.is_empty():
                    # This source has been exhausted.
                    break
                # Attempt to add on same name or to fill empty space:
                remnant = target.add(remnant, key)

            if remnant.is_nonempty():
                # Append the *remnant* to a new empty Dependency of
                # self's shape.
                broadcasted_remnant = \
                    upy2.dependency.Dependency(
                        shape=self.shape,
                        dtype=self.dtype,
                    )
                broadcasted_remnant.add(remnant, key)
                self.append(broadcasted_remnant)

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

    def conjugate(self):
        """ Returns the conjugate of *self*. """

        result = undarray(self.nominal.conj())
        for dependency in self.dependencies:
            result.append(dependency.conj())
        return result

    def conj(self):
        """ Short-hand for ``self.conjugate()``. """

        return self.conjugate()

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

    def __truediv__(self, other):
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

    def __rtruediv__(self, other):
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

    def positive(self):
        return upositive(self)

    def negative(self):
        return unegative(self)

    def absolute(self):
        return uabsolute(self)

    def sqrt(self):
        return usqrt(self)

    def square(self):
        return self ** 2

    def sin(self):
        return usin(self)

    def cos(self):
        return ucos(self)

    def tan(self):
        return utan(self)

    def arcsin(self):
        return uarcsin(self)

    def arccos(self):
        return uarccos(self)

    def arctan(self):
        return uarctan(self)

    def sinh(self):
        return usinh(self)

    def cosh(self):
        return ucosh(self)

    def tanh(self):
        return utanh(self)

    def arcsinh(self):
        return uarcsinh(self)

    def arccosh(self):
        return uarccosh(self)

    def arctanh(self):
        return uarctanh(self)

    def exp(self):
        return uexp(self)

    def exp2(self):
        return uexp2(self)

    def log(self):
        return ulog(self)

    def log2(self):
        return ulog2(self)

    def log10(self):
        return ulog10(self)
    
    #
    # Casts to int, float, ... are impossible, because we have ndarray
    # values.
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
            result.copy_dependencies(self._source(x))
        return result

    def _source(self, x):
        """ Derive the source of uncertainties of the nominal value
        based on the operand *x* of the operation.  *x* is an
        ``undarray``. """

        raise NotImplementedError('Virtual method called')


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
            result.copy_dependencies(self._source1(x1, y2))
        if isinstance(x2, undarray):
            result.copy_dependencies(self._source2(y1, x2))
        return result

    def _source1(self, x1, y2):
        """ Return the uncertainty source arising from the first
        operand *x1* given the nominal value *y2* of the second
        operand.  *x1* is guaranteed to be an ``undarray``. """

        raise NotImplementedError('Virtual method called')

    def _source2(self, y1, x2):
        """ Return the uncertainty source arising from the second
        operand *x2* given the nominal value *y1* of the first
        operand.  *x2* is guaranteed to be an ``undarray``. """

        raise NotImplementedError('Virtual method called')


# Protocol (Unary and Binary) implementations ...


class Positive(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.positive)

    def _source(self, x):
        return x


class Negative(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.negative)

    def _source(self, x):
        return x.scaled(-1)


class Absolute(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.abs)

    def _source(self, x):
        y = x.nominal
        return (x * numpy.sqrt(y.conj() / y)).real


class Sqrt(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.sqrt)

    def _source(self, x):
        y = x.nominal
        return x * (0.5 / numpy.sqrt(y))


class Square(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.square)

    def _source(self, x):
        y = x.nominal
        return x * (2 * y)


class Sin(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.sin)

    def _source(self, x):
        y = x.nominal
        return x * numpy.cos(y)


class Cos(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.cos)

    def _source(self, x):
        y = x.nominal
        return x * (-numpy.sin(y))


class Tan(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.tan)

    def _source(self, x):
        y = x.nominal
        return x * (1 + numpy.tan(y) ** 2)


# numpy does not support the cotangens ``cot``.


class Arcsin(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.arcsin)

    def _source(self, x):
        y = x.nominal
        return x / numpy.sqrt(1 - y ** 2)


class Arccos(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.arccos)

    def _source(self, x):
        y = x.nominal
        return x / (-numpy.sqrt(1 - y ** 2))


class Arctan(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.arctan)

    def _source(self, x):
        y = x.nominal
        return x / (1 + y ** 2)


class Arctan2(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.arctan2)

    def _source1(self, x1, y2):
        y1 = x1.nominal
        return x1 * (-y2 / (y1 ** 2 + y2 ** 2))

    def _source2(self, y1, x2):
        y2 = x2.nominal
        return x2 * (y1 / (y1 ** 2 + y2 ** 2))


class Sinh(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.sinh)

    def _source(self, x):
        y = x.nominal
        return x * numpy.cosh(y)


class Cosh(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.cosh)

    def _source(self, x):
        y = x.nominal
        return x * (-numpy.sinh(y))


class Tanh(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.tanh)

    def _source(self, x):
        y = x.nominal
        return x * (1 - numpy.tanh(y) ** 2)


class Arcsinh(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.arcsinh)

    def _source(self, x):
        y = x.nominal
        return x / numpy.sqrt(y ** 2 + 1)


class Arccosh(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.arccosh)

    def _source(self, x):
        y = x.nominal
        return x / (-numpy.sqrt(y ** 2 - 1))


class Arctanh(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.arctanh)

    def _source(self, x):
        y = x.nominal
        return x / (1 - y ** 2)


class Exp(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.exp)

    def _source(self, x):
        # f = exp(x)
        # d_x f = exp(x)
        y = x.nominal
        return x * numpy.exp(y)


class Exp2(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.exp2)

    def _source(self, x):
        # f = 2^x
        # d_x f = d_x exp(log(2) x)
        #   = log 2 2^x
        #   = log 2 f
        y = x.nominal
        return x * (numpy.log(2) * numpy.exp2(y))


class Log(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.log)

    def _source(self, x):
        # f = ln x
        # d_x f = 1 / x
        y = x.nominal
        return x / y


class Log2(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.log2)

    def _source(self, x):
        # f = ln_2 x = ln x / ln 2
        # d_x f = 1 / (x * ln 2)
        y = x.nominal
        return x / (y * numpy.log(2))


class Log10(Unary):
    def __init__(self):
        Unary.__init__(self, numpy.log10)

    def _source(self, x):
        # f = ln_10 x = ln x / ln 10
        # d_x f = 1 / (x * ln 10)
        y = x.nominal
        return x / (y * numpy.log(10))


class Add(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.add)

    def _source1(self, x1, y2):
        return x1

    def _source2(self, y1, x2):
        return x2


class Subtract(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.subtract)

    def _source1(self, x1, y2):
        return x1

    def _source2(self, y1, x2):
        return -x2


class Multiply(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.multiply)

    def _source1(self, x1, y2):
        return x1.scaled(y2)
            # Writing ``x1 * y2`` would lead to infinite recursion.

    def _source2(self, y1, x2):
        return x2.scaled(y1)


class Divide(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.true_divide)

    def _source1(self, x1, y2):
        # f = y1 / y2
        #
        # d_y1 f = 1 / y2
        #
        return x1 * (1.0/y2)
            # Writing ``x1 / y2`` would result in an infinite
            # recursion.

    def _source2(self, y1, x2):
        # f = y1 / y2 = y1 . y2 ^ (-1)
        #
        # d_y2 f = y1 . (-1) y2 ^ (-2)
        #
        y2 = x2.nominal
        return x2 * numpy.true_divide(-y1, y2 ** 2)


class Power(Binary):
    def __init__(self):
        Binary.__init__(self, numpy.power)

    def _source1(self, x1, y2):
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

        y1 = x1.nominal
        return x1 * (y2 * (y1 ** (y2 - 1)))

    def _source2(self, y1, x2):
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

        y2 = x2.nominal
        return x2 * ((y1 ** y2) * numpy.log(y1))


# The actual uufuncs ...


upositive = Positive()
unegative = Negative()
uabsolute = Absolute()
usqrt = Sqrt()
usquare = Square()
usin = Sin()
ucos = Cos()
utan = Tan()
uarcsin = Arcsin()
uarccos = Arccos()
uarctan = Arctan()
usinh = Sinh()
ucosh = Cosh()
utanh = Tanh()
uarcsinh = Arcsinh()
uarccosh = Arccosh()
uarctanh = Arctanh()
uexp = Exp()
uexp2 = Exp2()
ulog = Log()
ulog2 = Log2()
ulog10 = Log10()

uadd = Add()
usubtract = Subtract()
umultiply = Multiply()
udivide = Divide()
upower = Power()
uarctan2 = Arctan2()
