# Developed since: Feb 2010

import numpy
import upy.dependency

__all__ = ['Characteristic']

"""Dependence on multiple error sources."""


class Characteristic:
    """ A Characteristic stores several :class:`Dependency` instances.
    It stores all dependencies which are characteristic for an
    uncertain value. """

    #
    # Initialisation ...
    # class Characteristic cannot be made a dictionary, because the key access
    # is used to address subsets of the arrays contained.
    #

    def __init__(self, shape):
        """SHAPE is the shape of the data the Characteristic instance is
        for.  It is used when broadcasting other Characteristics coerced
        with this instance to the correct shape."""

        self.shape = shape
        self.ndim = len(self.shape)

        # Used to "simulate" several operations on the Characteristic
        # where the result shape needs to be known prior to operating
        # on the Characteristic.
        self._shape_effect_array = numpy.lib.stride_tricks.as_strided(
            numpy.zeros([], dtype=numpy.bool),
            shape=self.shape,
            strides=([0] * self.ndim),
        )
        #self._key_testing_array = numpy.zeros(shape, dtype = numpy.bool)

        self.dependencies = []

    def append(self, dependency):
        """Append another Dependency."""

        if self.shape != dependency.shape:
            raise ValueError("Shape mismatch in "
                "Characteristic.append(): self.shape = %s, "
                "dependency.shape = %s" % (self.shape,
                    dependency.shape))
        self.dependencies.append(dependency)

    def clear(self, key):
        """Clear all uncertainty information in key-access key KEY."""

        for dependency in self.dependencies:
            dependency.clear(key)
        
    #
    # Obtaining the variance ...
    #
    
    @property
    def variance(self):
        """Return the variance induced by all the dependencies stored in
        the Characteristic."""

        if len(self.dependencies) > 0:
            return numpy.asarray([dependency.variance for \
                    dependency in self.dependencies]).sum(axis=0)
        else:
            return numpy.zeros(self.shape)

    #
    # Selecting real or imaginary part ...
    #

    @property
    def real(self):
        """ Returns the real part of this Characteristic. """

        result = Characteristic(self.shape)
        for dependency in self.dependencies:
            result.append(dependency.real)

        return result

    @property
    def imag(self):
        """ Returns the imaginary part of this Characteristic. """

        result = Characteristic(self.shape)
        for dependency in self.dependencies:
            result.append(dependency.imag)

        return result

    #
    # Binary arithmetic operators ...
    #

    def add(self, other, key=None):
        """ *other* is a Characteristic instance.  *key* indexes
        *self*.  *other* will add to ``self[key]``.  Without *key*
        (or, *key* = None), *other* will be added to all of *self*.

        The operation is performed in-place. """

        # Add all source Dependencies to self ...

        for source in other.dependencies:

            # First, everything is left.
            source_remnant = source

            for target in self.dependencies:
                # Attempt to add together or to fill empty space.
                source_remnant = target.add(source_remnant, key)

                if source_remnant.is_empty():
                    # We're don with this source.
                    break

            if source_remnant.is_nonempty():
                # Well, then.  Broadcast the source_remnant to self's shape.
                broadcasted_source_remnant = upy.dependency.Dependency(
                        shape = self.shape)
                broadcasted_source_remnant.add(source_remnant, key)
                self.append(broadcasted_source_remnant)
    
    def __iadd__(self, other):
        """See .add()."""

        self.add(other)
        return self

    def __mul__(self, other):
        """Multiply all Dependencies contained with an ndarray coefficient, 
        in a new Characteristic instance."""

        # Convert OTHER to a (maybe scalar) numpy.ndarray ...

        other = numpy.asarray(other)

        result_shape = (self._shape_effect_array * other).shape
        result = Characteristic(shape=result_shape)
        for dependency in self.dependencies:
            result.append(dependency * other)
        return result

#X1        # Determine the shape of the resulting Characteristic instance 
#X1        # and broadcast() self if necessary.  If other.ndim > self.ndim,
#X1        # then broadcasting of self is necessary to get the .variance 
#X1        # attributes of the Dependencies set to the correct shape (the
#X1        # .derivative attributes would be broadcast by numpy in 
#X1        # multiplication also).
#X1
#X1        # Set default values.
#X1        self_broadcasted = self
#X1        
#X1        if self.ndim > other.ndim:
#X1            # Use self's .shape.
#X1            result_shape = self.shape
#X1            
#X1            # OTHER will be broadcast by numpy in multiplication.
#X1
#X1        elif self.ndim < other.ndim:
#X1            # Use other's .shape.
#X1            result_shape = other.shape
#X1
#X1            # Broadcast self.
#X1            self_broadcasted = self.broadcasted(shape = result_shape)
#X1
#X1        elif self.ndim == other.ndim:
#X1            # Check the shapes.
#X1            if self.shape != other.shape:
#X1                raise ValueError('Shape mismatch: Objects cannot be broadcast to a single shape.')
#X1        
#X1            # If the check doesn't fail, it doesn't matter whose shape to use.
#X1            result_shape = self.shape
#X1
#X1            # No object must be broadcast()'ed.
#X1
#X1        result = Characteristic(shape=result_shape)
#X1        
#X1        for dependency in self_broadcasted.dependencies:
#X1            result.append(dependency * other)
#X1
#X1        return result

    #
    # Reverse binary operators ...
    #

    # __radd__() and __rsub__() are not needed because only Characteristics 
    # are allowed as operands.

#    def __rmul__(self, other):
#        """Multiply all Dependencies contained with a coefficient, in a new
#        Characteristic instance.  .shape is maintained."""
#
#        # Well, use this ...
#
#        return Characteristic.__mul__(self, other)
    __rmul__ = __mul__      # much quicker and identical to the old code.

    #
    # Augmented arithmetics will be emulated by using standard
    # arithmetics ...
    #

    #
    # Keying methods ...
    #
    
#X    def __getitem__(self, (shape, key)):
#X        """Argument is not directly the key, but the tuple (SHAPE, KEY).
#X        I.e., call self[new_shape, key].  This is permissible, because
#X        the undarray can determine the shape from the key when applied to the
#X        undarray's .value.  Return the given subset of all Dependencies 
#X        contained.  Return value will be a Characteristic."""
    def __getitem__(self, key):
        """ Returns the portion of *self* indexed by *key*. """

        result_shape = self._shape_effect_array[key].shape
        result = Characteristic(shape=result_shape)
        for dependency in self.dependencies:
            result.append(dependency[key])
        return result

    def __setitem__(self, key, value):
        """VALUE is supposed to be an Characteristic instance.  First clear
        the given subset, then add VALUE to self in-place."""

        self.clear(key)
        self.add(value, key)

    def __len__(self):
        """This fails for scalar Characteristics, what is should do in fact."""

        return self.shape[0]
        
    #
    # ndarray methods ...
    #
    
    def compress(self, *compress_args, **compress_kwargs):
        """ Returns a Characteristic with compress()'ed dependencies.
        """

        result_shape = self._shape_effect_array.compress(
            *compress_args, **compress_kwargs).shape
        result = Characteristic(shape=result_shape)
        for dependency in self.dependencies:
            result.append(dependency.compress(
                *compress_args, **compress_kwargs))
        return result

    def copy(self):
        """Returns a Characteristic with copy()'ed Dependency instances."""

        result = Characteristic(shape=self.shape)
        for dependency in self.dependencies:
            result.append(dependency.copy())
        return result

    def flatten(self, *flatten_args, **flatten_kwargs):
        """Returns a copy with flatten()'ed Dependency instances.  The 
        arguments are handed over to the Dependencies' methods. """

        result_shape = self._shape_effect_array.flatten(
            *flatten_args, **flatten_kwargs).shape
        result = Characteristic(shape=result_shape)
        for dependency in self.dependencies:
            result.append(dependency.flatten(
                *flatten_args, **flatten_kwargs))
        return result

    def repeat(self, *repeat_args, **repeat_kwargs):
        """Returns a copy with repeat()'ed Dependency instances.  The
        arguments are handed over to the Dependencies' methods. """

        result_shape = self._shape_effect_array.repeat(
            *repeat_args, **repeat_kwargs).shape
        result = Characteristic(shape=result_shape)
        for dependency in self.dependencies:
            result.append(dependency.repeat(
                *repeat_kwargs, **repeat_kwargs))
        return result

    def reshape(self, *reshape_args, **reshape_kwargs):
        """Returns a copy with reshape()'ed Dependency instances.  The
        arguments are handed over to the Dependencies' methods. """

        result_shape = self._shape_effect_array.reshape(
            *reshape_args, **reshape_kwargs).shape
        result = Characteristic(shape=result_shape)
        for dependency in self.dependencies:
            result.append(dependency.reshape(
                *reshape_args, **reshape_kwargs))
        return result
    
    def transpose(self, *transpose_args, **transpose_kwargs):
        """Returns a copy with transpose()'ed Dependency instances.  The
        arguments are handed over to the Dependencies' methods. """

        result_shape = self._shape_effect_array.transpose(
            *transpose_args, **transpose_kwargs).shape
        result = Characteristic(shape=result_shape)
        for dependency in self.dependencies:
            result.append(dependency.transpose(
                *transpose_args **transpose_kwargs))
        return result

    #
    # Special array methods ...
    #

#XX    def broadcast(self, shape):
#XX        """Broadcasts the Characteristic to shape SHAPE by broadcast()'ing
#XX        the contained Dependencies.  Thus, for documentation, see
#XX        Dependency.broadcast().
#XX        
#XX        This method acts in-place."""
#XX        
#XX        # Emulate the in-place behaviour by replacing the dependencies.
#XX        dependencies = self.dependencies
#XX        self.dependencies = []
#XX
#XX        for dependency in dependencies:
#XX            self.append(dependency.broadcasted(shape))
# broadcasting in-place is not a good idea since the shape
# *self.shape* changes as well ...

# ``self.broadcasted()`` was used before in ``__mul__()``, but it is
# no longer in use there.  ``self.broadcasted()`` has been no-where
# else in use.
#X    def broadcasted(self, shape):
#X        """Broadcasts the Characteristic to shape SHAPE by broadcast()'ing
#X        the contained Dependencies.  Thus, for documentation, see
#X        Dependency.broadcast().
#X        
#X        This method acts not in-place."""
#X
#X        result = Characteristic(shape = shape)
#X        for dependency in self.dependencies:
#X            result.append(dependency.broadcasted(shape))
#X
#X        return result
