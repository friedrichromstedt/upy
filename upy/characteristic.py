# Developed since: Feb 2010

import numpy
import upy.dependency

__all__ = ['Characteristic']

"""Dependence on multiple error sources."""


class Characteristic:
    """A Characteristic is a dictionary of error source names and 
    dependencies on that sources.  Read-only attributes:
        
    .dependencies - {source's name: Dependency instance}"""

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

        # Used for finding out the target space in add().
        self._shape_effect_array = numpy.lib.stride_tricks.as_strided(
            numpy.zeros([], dtype=numpy.bool),
            shape=self.shape,
            strides=([0] * self.ndim),
        )
        #self._key_testing_array = numpy.zeros(shape, dtype = numpy.bool)

        self.dependencies = []

    def append(self, dependency):
        """Append another Dependency."""

        assert(self.shape == dependency.shape)
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
        *self*.  *other* will add to ``self[key]``.

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

        # Determine the shape of the resulting Characteristic instance 
        # and broadcast() self if necessary.  If other.ndim > self.ndim,
        # then broadcasting of self is necessary to get the .variance 
        # attributes of the Dependencies set to the correct shape (the
        # .derivative attributes would be broadcast by numpy in 
        # multiplication also).

        # Set default values.
        self_broadcasted = self
        
        if self.ndim > other.ndim:
            # Use self's .shape.
            result_shape = self.shape
            
            # OTHER will be broadcast by numpy in multiplication.

        elif self.ndim < other.ndim:
            # Use other's .shape.
            result_shape = other.shape

            # Broadcast self.
            self_broadcasted = self.broadcasted(shape = result_shape)

        elif self.ndim == other.ndim:
            # Check the shapes.
            if self.shape != other.shape:
                raise ValueError('Shape mismatch: Objects cannot be broadcast to a single shape.')
        
            # If the check doesn't fail, it doesn't matter whose shape to use.
            result_shape = self.shape

            # No object must be broadcast()'ed.

        result = Characteristic(shape=result_shape)
        
        for dependency in self_broadcasted.dependencies:
            result.append(dependency * other)

        return result

    #
    # Reverse binary operators ...
    #

    # __radd__() and __rsub__() are not needed because only Characteristics 
    # are allowed as operands.

    def __rmul__(self, other):
        """Multiply all Dependencies contained with a coefficient, in a new
        Characteristic instance.  .shape is maintained."""

        # Well, use this ...

        return Characteristic.__mul__(self, other)

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
        shape = self._shape_effect_array[key].shape

        result = Characteristic(shape)

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
    
    def compress(self, new_shape, *compress_args, **compress_kwargs):
        """Returns a copy with compress()'ed Dependency instances.  The
        arguments are handed over to the Dependencies' methods.  NEW_SHAPE is
        the new shape."""

        result = Characteristic(shape=new_shape)
        for dependency in self.dependencies:
            result.append(dependency.compress(
                *compress_args, **compress_kwargs))
        return result

    def copy(self):
        """Returns a copy with copy()'ed Dependency instances."""

        result = Characteristic(shape=self.shape)
        for dependency in self.dependencies:
            result.append(dependency.copy())
        return result

    def flatten(self, new_shape, *flatten_args, **flatten_kwargs):
        """Returns a copy with flatten()'ed Dependency instances.  The 
        arguments are handed over to the Dependencies' methods.  NEW_SHAPE is
        the new shape."""

        result = Characteristic(shape = new_shape)
        for dependency in self.dependencies:
            result.append(dependency.flatten(
                *flatten_args, **flatten_kwargs))
        return result

    def repeat(self, new_shape, *repeat_args, **repeat_kwargs):
        """Returns a copy with repeat()'ed Dependency instances.  The
        arguments are handed over to the Dependencies' methods.  NEW_SHAPE is
        the new shape."""

        result = Characteristic(shape = new_shape)
        for dependency in self.dependencies:
            result.append(dependency.repeat(
                *repeat_kwargs, **repeat_kwargs))
        return result

    def reshape(self, new_shape, *reshape_args, **reshape_kwargs):
        """Returns a copy with reshape()'ed Dependency instances.  The
        arguments are handed over to the Dependencies' methods.  NEW_SHAPE is
        the new shape."""

        result = Characteristic(shape = new_shape)
        for dependency in self.dependencies:
            result.append(dependency.reshape(
                *reshape_args, **reshape_kwargs))
        return result
    
    def transpose(self, shape, *transpose_args, **transpose_kwargs):
        """Returns a copy with transpose()'ed Dependency instances.  The
        arguments are handed over to the Dependencies' methods.  SHAPE is
        the new shape."""

        result = Characteristic(shape = shape)
        for dependency in self.dependencies:
            result.append(dependency.transose(
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

    def broadcasted(self, shape):
        """Broadcasts the Characteristic to shape SHAPE by broadcast()'ing
        the contained Dependencies.  Thus, for documentation, see
        Dependency.broadcast().
        
        This method acts not in-place."""

        result = Characteristic(shape = shape)
        for dependency in self.dependencies:
            result.append(dependency.broadcasted(shape))

        return result
