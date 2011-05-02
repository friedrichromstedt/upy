# Copyright (c) 2010 Friedrich Romstedt <friedrichromstedt@gmail.com>
# See also <www.friedrichromstedt.org> (if e-mail has changed)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
        self.key_testing_array = numpy.zeros(shape, dtype = numpy.bool)

        self.dependencies = []

    def append(self, dependency):
        """Append just another Dependency without further asking."""

        self.dependencies.append(dependency)

    def clear(self, key):
        """Clear all uncertainty information in key-access key KEY."""

        for dependency in self.dependencies:
            dependency.clear(key)
        
    #
    # Obtaining the variance ...
    #
    
    def get_variance(self):
        """Return the variance induced by all the dependencies stored in
        the Characteristic."""

        if len(self.dependencies) > 0:
            return numpy.asarray([dependency.get_variance() for \
                    dependency in self.dependencies]).sum(axis = 0)
        else:
            return numpy.zeros(self.shape)

    #
    # Binary arithmetic operators ...
    #

    def add(self, other, key = None):
        """OTHER must be a Characteristic instance.  Add dependencies on
        the same error source together.  self and the OTHER Characteristic 
        instance will be .broadcast()'ed to the .shape with the largest .ndim 
        before being added together.  Broadcasting is necessary because not
        both Characteristics must depend on all Dependencies, thus some 
        Dependencies would be taken over, leaving their shape unchanged, and
        thus compromising data integrity, because there will be no numpy
        broadcasting mechanism bringing the operands to common shape.  KEY is 
        the portion of self where OTHER applies.  KEY must be either a scalar,
        or a tuple.
        
        For the functionality of .broadcast(), see Dependency.broadcast().
        
        This method acts in-place."""
        
        if key is None:
            # Indice everything.
            key = ()
        elif not isinstance(key, tuple):
            # Make shure also scalar indices are interpreted as tupels (idx,).
            key = (key,)

        # Determine the shape of the resulting Characteristic instance ...

        # Determine the portion of self left by KEY.
        key_testing_array = self.key_testing_array[key]
        self_shape_used = key_testing_array.shape
        self_ndim_used = key_testing_array.ndim
        
        # Set default values.
        other_broadcasted = other

        if self_ndim_used > other.ndim:
            # Use self's .shape.
            result_shape = self_shape_used
            
            # Broadcast OTHER.  (not in-place)
            other_broadcasted = other.broadcasted(shape = result_shape)

        elif self_ndim_used < other.ndim:
            raise NotImplementedError('This feature should not be needed.')

        elif self_ndim_used == other.ndim:
            # Check the shapes.
            if tuple(self_shape_used) != tuple(other.shape):
                raise ValueError('Shape mismatch: Objects cannot be broadcast to a single shape (shapes %s, %s).' % (self_shape_used, other.shape))
        
            # If the check doesn't fail, it doesn't matter whose shape to use.
            result_shape = self_shape_used

            # No object must be broadcast()'ed.

        # Add all source Dependencies to self ...

        for source in other_broadcasted.dependencies:

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

        result = Characteristic(shape = result_shape)
        
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
    
    def __getitem__(self, (shape, key)):
        """Argument is not directly the key, but the tuple (SHAPE, KEY).
        I.e., call self[new_shape, key].  This is permissible, because
        the undarray can determine the shape from the key when applied to the
        undarray's .value.  Return the given subset of all Dependencies 
        contained.  Return value will be a Characteristic."""

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

    def broadcast(self, shape):
        """Broadcasts the Characteristic to shape SHAPE by broadcast()'ing
        the contained Dependencies.  Thus, for documentation, see
        Dependency.broadcast().
        
        This method acts in-place."""
        
        # Emulate the in-place behaviour by replacing the dependencies.
        dependencies = self.dependencies
        self.dependencies = []

        for dependency in dependencies:
            self.append(dependency.broadcasted(shape))

    def broadcasted(self, shape):
        """Broadcasts the Characteristic to shape SHAPE by broadcast()'ing
        the contained Dependencies.  Thus, for documentation, see
        Dependency.broadcast().
        
        This method acts not in-place."""

        result = Characteristic(shape = shape)
        for dependency in self.dependencies:
            result.append(dependency.broadcasted(shape))

        return result
