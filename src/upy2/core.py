# Developed since: Jan 2010

""" The central upy2 module, implementing the uncertain ndarray:
:class:`undarray`. """

import numpy
import upy2
import upy2.dependency
import upy2.typesetting.protocol
import upy2.sessions

__all__ = ['undarray', 'uzeros', 'asuarray', 'ucopy', 'U', 'u',
    'upositive', 'unegative', 'uabsolute', 'usqrt', 'usquare',
    'usin', 'ucos', 'utan', 'uarcsin', 'uarccos', 'uarctan',
    'usinh', 'ucosh', 'utanh', 'uarcsinh', 'uarccosh', 'uarctanh',
    'uexp', 'uexp2', 'ulog', 'ulog2', 'ulog10',
    'uadd', 'usubtract', 'umultiply', 'udivide', 'upower',
    'uarctan2']

typesetting_session = upy2.sessions.byprotocol(
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

class U(upy2.sessions.Protocol):
    def __init__(self, stddevs):
        """ "Uncertainty" (``U``) Session managers provide *standard
        deviations* based on *uncertainties*.  The *uncertainties* are
        a multiple of the standard deviations with the factor given by
        the *stddevs* argument. """

        upy2.sessions.Protocol.__init__(self)

        self.stddevs = stddevs

    def provide(self, uncertainty):
        """ Provides an undarray with zero nominal value and with
        uncertainty based on *uncertainty*.  *uncertainty* is
        interpreted as a multiple of the standard deviation as defined
        on initialisation time. """

        stddev = numpy.true_divide(uncertainty, self.stddevs)
        nominal = numpy.zeros_like(stddev)
        return undarray(nominal=nominal, stddev=stddev)

    def __call__(self, uncertainty):
        """ Convenience method to provide a short-hand for
        :meth:`provide`.

        Example::

            u5 = U(5)
            ua = nominal +- u5(five_sigma_uncertainty)

        Writing ``.provide(...)`` is not needed to ensure readability
        and hence the syntax can be made more terse by pruning the
        explicit call to :meth:`provide`. """

        return self.provide(uncertainty)

upy2.sessions.define(U)

# Access to the "U" Session:

U_session = upy2.sessions.byprotocol(U)

def u(uncertainty):
    return U_session.current().provide(uncertainty)


#
# The central undarray class ...
#


def withoptout(fn):
    def augmented(self, other, *args, **kwargs):
        if hasattr(other, '__array_ufunc__') and \
                other.__array_ufunc__ is None:
            return NotImplemented
        return fn(self, other, *args, **kwargs)
    return augmented


class undarray(object):
    """Implements uncertain ndarrays.  The name is derived from
    :class:`numpy.ndarray`. """

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
        within the new ``undarray`` nor with elements of other
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
                    names=upy2.guid_generator.generate_idarray(
                        shape=self.shape),
                    derivatives=stddev,
                    dtype=dtype,
            )   # The Dependency constructor does not necessarily copy
                # the data given.
            self.append(dependency)

    def append(self, dependency):
        """ Append an instance of :class:`Dependency` to the list of
        Dependencies in this :class:`undarray`.  Both the shape as
        well as the dtype of *dependency* need to match the shape and
        the dtype of *self* *accurately*. """

        if not self.shape == dependency.shape:
            raise ValueError(
                    ('Cannot append a Dependency of shape {0} '
                     'to a {1}-shaped undarray').format(
                    dependency.shape, self.shape))
        if not self.dtype == dependency.dtype:
            raise ValueError(
                    ('Cannot append a Dependency of dtype {0} '
                     'to a {1}-dtyped undarray').format(
                    dependency.dtype, self.dtype))
        self.dependencies.append(dependency)

    def clear(self, key):
        """ Abandon all uncertainty information in the subset of
        *self* specified by *key*. """

        for dependency in self.dependencies:
            dependency.clear(key)

    def scaled(self, factor):
        """ This method implements the operation ``ua * factor``,
        where *factor* isn't another undarray.  This is used to
        implement multiplication within :class:`Multiply`. """

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
            # ``.real`` returns a View.
        for dependency in self.dependencies:
            result.append(dependency.real)
        return result

    @property
    def imag(self):
        """ Returns the imaginary component of *self*.  This pertains
        to the nominal value as well as to the Dependencies. """

        result = undarray(self.nominal.imag.copy())
            # ``.imag`` returns a View.
        for dependency in self.dependencies:
            result.append(dependency.imag)
        return result

    def conjugate(self):
        """ Returns the conjugate of *self*. """

        result = undarray(self.nominal.conj())
            # ``.conj`` returns a copy of the real component.
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

        if not numpy.isrealobj(self.nominal):
            raise ValueError(
                    'Refusing to calculate the variance of a '
                    'non-real undarray')

        result = numpy.zeros(shape=self.shape, dtype=self.dtype)
        for dependency in self.dependencies:
            result += dependency.variance
        return result
    
    @property
    def stddev(self):
        """ Returns the standard deviation. """
        
        return numpy.sqrt(self.variance)
            # Obtaining the variance for non-real undarrays will fail.

    #
    # numpy :meth:`__array_ufunc__` protocol ...
    #

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if method != '__call__':
            return NotImplemented
        if len(kwargs) > 0:
            return NotImplemented

        if len(inputs) == 1:
            (A,) = inputs
            # A is always *self*, i.e, a :class:`undarray` instance.
        else:
            (A, B) = inputs

        if ufunc is numpy.positive:
            return self
        elif ufunc is numpy.negative:
            return unegative(A)
        elif ufunc is numpy.absolute:
            return uabsolute(A)

        elif ufunc is numpy.add:
            return uadd(A, B)
        elif ufunc is numpy.subtract:
            return usubtract(A, B)
        elif ufunc is numpy.multiply:
            return umultiply(A, B)
        elif ufunc is numpy.divide:
            return udivide(A, B)
        elif ufunc is numpy.power:
            return upower(A, B)
        
        elif ufunc is numpy.sqrt:
            return usqrt(A)
        elif ufunc is numpy.square:
            return usquare(A)

        elif ufunc is numpy.sin:
            return usin(A)
        elif ufunc is numpy.cos:
            return ucos(A)
        elif ufunc is numpy.tan:
            return utan(A)

        elif ufunc is numpy.arcsin:
            return uarcsin(A)
        elif ufunc is numpy.arccos:
            return uarccos(A)
        elif ufunc is numpy.arctan:
            return uarctan(A)

        elif ufunc is numpy.sinh:
            return usinh(A)
        elif ufunc is numpy.cosh:
            return ucosh(A)
        elif ufunc is numpy.tanh:
            return utanh(A)

        elif ufunc is numpy.arcsinh:
            return uarcsinh(A)
        elif ufunc is numpy.arccosh:
            return uarccosh(A)
        elif ufunc is numpy.arctanh:
            return uarctanh(A)

        elif ufunc is numpy.exp:
            return uexp(A)
        elif ufunc is numpy.exp2:
            return uexp2(A)

        elif ufunc is numpy.log:
            return ulog(A)
        elif ufunc is numpy.log2:
            return ulog2(A)
        elif ufunc is numpy.log10:
            return ulog10(A)

    #
    # Binary arithmetics ...
    #

    @withoptout
    def __add__(self, other):
        return numpy.add(self, other)

    @withoptout
    def __sub__(self, other):
        return numpy.subtract(self, other)

    @withoptout
    def __mul__(self, other):
        return numpy.multiply(self, other)

    @withoptout
    def __div__(self, other):
        return numpy.divide(self, other)

    @withoptout
    def __truediv__(self, other):
        return numpy.divide(self, other)

    @withoptout
    def __pow__(self, other):
        return numpy.power(self, other)

    #
    # Reflected binary arithmetics ...
    #

    @withoptout
    def __radd__(self, other):
        return numpy.add(other, self)

    @withoptout
    def __rsub__(self, other):
        return numpy.subtract(other, self)

    @withoptout
    def __rmul__(self, other):
        return numpy.multiply(other, self)

    @withoptout
    def __rdiv__(self, other):
        return numpy.divide(other, self)

    @withoptout
    def __rtruediv__(self, other):
        return numpy.divide(other, self)

    @withoptout
    def __rpow__(self, other):
        return numpy.power(other, self)

    #
    # Augmented arithmetics will be emulated ...
    #

    #
    # Unary operators ...
    #

    def __pos__(self):
        return numpy.positive(self)

    def __neg__(self):
        return numpy.negative(self)

    def __abs__(self):
        return numpy.absolute(self)

    def positive(self):
        return numpy.positive(self)

    def negative(self):
        return numpy.negative(self)

    def absolute(self):
        return numpy.absolute(self)

    def sqrt(self):
        return numpy.sqrt(self)

    def square(self):
        return numpy.square(self)

    def sin(self):
        return numpy.sin(self)

    def cos(self):
        return numpy.cos(self)

    def tan(self):
        return numpy.tan(self)

    def arcsin(self):
        return numpy.arcsin(self)

    def arccos(self):
        return numpy.arccos(self)

    def arctan(self):
        return numpy.arctan(self)

    # I am intentionally *not* defining :meth:`arctan2`.  It would
    # work in ``numpy.arctan2(ua, <...>)`` with an uncertain quantity
    # ``ua``; however, it would *not* work with ``numpy.arctan2(<...>,
    # ua)``, most specifically, it won't work in ``numpy.arctan2(b,
    # ua)`` with an ndarray ``b``.  Use ``upy2.uarctan2`` directly.

    def sinh(self):
        return numpy.sinh(self)

    def cosh(self):
        return numpy.cosh(self)

    def tanh(self):
        return numpy.tanh(self)

    def arcsinh(self):
        return numpy.arcsinh(self)

    def arccosh(self):
        return numpy.arccosh(self)

    def arctanh(self):
        return numpy.arctanh(self)

    def exp(self):
        return numpy.exp(self)

    def exp2(self):
        return numpy.exp2(self)

    def log(self):
        return numpy.log(self)

    def log2(self):
        return numpy.log2(self)

    def log10(self):
        return numpy.log10(self)
    
    #
    # Casts to int, float etc. aren't supported.
    #

    #
    # Comparison operators remain unimplemented by intention.
    #
    
    #
    # Keying methods ...
    #
    
    def __getitem__(self, key):
        """ Returns the given subset of the undarray, by applying
        *key* both to the nominal value as well as to the
        Dependencies. """

        result = undarray(nominal=self.nominal[key].copy())
        for dependency in self.dependencies:
            result.append(dependency[key])

        return result

    def __setitem__(self, key, value):
        """ Replace the portion of *self* indexed by *key* with
        *value*.

        If *value* is not an ``undarray``, it will be treated as the
        replacement for the specified portion of *self*'s nominal
        value.

        *value* might be broadcast to fit the portion of *self*
        indexed by *key*. """

        self.clear(key)

        if isinstance(value, undarray):
            self.nominal[key] = value.nominal
                # Since we use key assignment, the shape of
                # ``self.nominal`` cannot grow.
            self.copy_dependencies(source=value, key=key)
        else:
            self.nominal[key] = value

    def __len__(self):
        return len(self.nominal)

    #
    # ndarray methods, alphabetically sorted ...
    #

    def compress(self, *compress_args, **compress_kwargs):
        """ Returns a copy with compressed nominal value and
        Dependencies, see ``numpy.compress``. """

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
        """ Returns a copy of the undarray.  Note that only the data is
        copied, and no new names for the dependencies are created.  This
        means, that the undarray will bahave in all arithmetics the same as
        the original, except for that it has its own memory. """

        result = undarray(nominal=self.nominal.copy())
        for dependency in self.dependencies:
            result.append(dependency.copy())
        return result

    def flatten(self, *flatten_args, **flatten_kwargs):
        """ Returns a copy with *flattened* nominal value and
        Dependencies, see ``numpy.ndarray.flatten``. """

        result = undarray(
            nominal=self.nominal.flatten(
                *flatten_args, **flatten_kwargs
            ))
        for dependency in self.dependencies:
            result.append(dependency.flatten(
                *flatten_args, **flatten_kwargs
            ))
        return result

    # Notice also the comment beneath the definition of
    # :meth:`Dependency.flatten`.

    def repeat(self, *repeat_args, **repeat_kwargs):
        """ Returns a copy with *repeated* nominal value and
        Dependencies, see ``numpy.repeat``. """

        result = undarray(
            nominal=self.nominal.repeat(
                *repeat_args, **repeat_kwargs
            ))
        for dependency in self.dependencies:
            result.append(dependency.repeat(
                *repeat_args, **repeat_kwargs
            ))
        return result

    def reshape(self, *reshape_args, **reshape_kwargs):
        """ Returns a copy with *reshaped* nominal value and
        Dependencies, see ``numpy.repeat``. """

        result = undarray(
            nominal=self.nominal.reshape(
                *reshape_args, **reshape_kwargs
            ).copy())
        for dependency in self.dependencies:
            result.append(dependency.reshape(
                *reshape_args, **reshape_kwargs
            ))
        return result

    def transpose(self, *transpose_args, **transpose_kwargs):
        """ Returns a copy with *transposed* nominal value and
        Dependencies, see ``numpy.transpose``. """

        result = undarray(
            nominal=self.nominal.transpose(
                *transpose_args, **transpose_kwargs
            ).copy())
        for dependency in self.dependencies:
            result.append(dependency.transpose(
                *transpose_args, **transpose_kwargs
            ))
        return result

    #
    # String conversion ...
    #

    def __str__(self):
        """ Returns the string representation of *self* according to
        the typesetting session. """

        typesetter = typesetting_session.current()
        return typesetter.typeset(self)

    def __repr__(self):
        return "<{shape}-shaped {dtype}-typed undarray>".format(
                shape=self.shape, dtype=self.dtype)


#
# uufuncs ...
#


# uufunc classes ...


class uufunc(object):
    """ uufuncs augment a numpy ufunc by propagation of uncertainties.
    """

    def __init__(self, ufunc):
        """ *ufunc* is the numpy ufunc calculating the nominal value
        of the resulting undarray. """

        self.ufunc = ufunc

    def __str__(self):
        return "<{} uufunc>".format(self.ufunc)

    def __repr__(self):
        return "<{!r} uufunc>".format(self.ufunc)


class Unary(uufunc):
    """ The base class for unary uufuncs.  Derive unary uufunc classes
    from this class and define :meth:`_source`.

    Upon calling the derived unary uufunc, :meth:`_source` will only
    be called when the operand is an ``undarray`.

    The result of calling an unary uufunc is *always* an ``undarray``.
    """

    def __call__(self, x):
        """ Performs the operation on operand *x*.  If *x* is not an
        instance of :class:`undarray`, it will be passed through
        :func:`numpy.asarray`. """

        if isinstance(x, undarray):
            y = x.nominal
        else:
            y = numpy.asarray(x)

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
    """ The base class for binary uufuncs.  Derive binary uufunc
    classes from this class and define :meth:`_source1` and
    :meth:`_source2`.

    Upon calling the derived binary uufunc, :meth:`_source1` will only
    be called when the first operand is an ``undarray``, and likewise
    :meth:`_source2` will only be used when the second operand is an
    ``undarray``.

    The result of calling a binary uufunc is *always* an ``undarray``.
    """

    def __call__(self, x1, x2):
        """ Performs the operation on operands *x1* and *x2*.  If the
        operands are not instances of :class:`undarray`, they will be
        passed through :func:`numpy.asarray`. """

        if isinstance(x1, undarray):
            y1 = x1.nominal
        else:
            y1 = numpy.asarray(x1)

        if isinstance(x2, undarray):
            y2 = x2.nominal
        else:
            y2 = numpy.asarray(x2)

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
        operand.  *x1* is guaranteed to be an ``undarray``, *y2* is
        guaranteed to be an ``ndarray``. """

        raise NotImplementedError('Virtual method called')

    def _source2(self, y1, x2):
        """ Return the uncertainty source arising from the second
        operand *x2* given the nominal value *y1* of the first
        operand.  *x2* is guaranteed to be an ``undarray``, *y1* is
        guaranteed to be an ``ndarray`. """

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
