# Developed since: September 2015
#
# Built upon 'decimal2.py', part of upy v0.4.11b, developed since
# August 2008.

""" Number analysis module. """

import math
import upy2.sessions
import upy2.typesetting.protocol


def get_position_of_leftmost_digit(number):
    """ Returns the position of the leftmost digit of *number* in
    decimal representation.  Positions <= 0 are before the point,
    positions > 0 are behind the point.  For *number* == 0, ``None``
    is returned.

    For a certain digit position *pos*, the weight of this digit is
    given by::
   
      weight = 10 ** -pos  .
   
    All digits non-right of the digit at position *pos* represent a
    multiple of this weight.  For some nonnegative value *val*, the
    expression::
   
      value % weight
   
    returns a number whose decimal representation consists in
    principle of all digits right of *pos*.  For example, 1.11 % 1 =
    0.11, and 1.11 % 0.1 = 0.01.  Because not all numbers with a
    finite decimal representation are representable by a finite
    binary representation, this calculations hold only "in
    principle" on a machine working with binary numbers.
   
    When *weight* is larger than *value*, the expression ``value %
    weight`` returns *value* unchanged.  *weight* is larger than
    *value* iff. all digits in the decimal representation of *value*
    non-right of *pos* are zero.  In this case the expression:
   
      value - value % weight
   
    is precisely zero, because ``value % weight`` is equal precisely
    to *value* in that case.  The expression ``value - value %
    weight == 0`` can be used to identify the case that the decimal
    representation of *value* has zero-digits at all positions
    non-right of the position *pos*.

    We use this indicator, to find the position of the left-most
    non-zero digit of *number*:
   
     1.   Begin the search at some arbitrary position.
   
     2.   Move left (decrease *pos*) until there are no longer
          digits non-right of *pos*.
   
     3.   Move right (increase *pos*) until there are digits
          non-right to *pos*.

          At this point, we are at the position of the left-most
          non-zero digit of *number*.
   
    When *number* is zero, it does not feature any non-zero digits,
    and hence does not exhibit a left-most non-zero digit.  We return
    ``None`` in that case. """

    if number == 0:
        return None
    number = abs(number)

    pos = 0
    while (number - number % (10 ** -pos)) != 0:
        pos -= 1
    while (number - number % (10 ** -pos)) == 0:
        pos += 1
    return pos


class TypesetNumber:
    """ Holds the typeset ingredients for a decimal fp number
    representation. """
    
    def __init__(self, left, point, right):
        self.left = left
        self.point = point
        self.right = right

    def __str__(self):
        return self.left + self.point + self.right

# There is no need for a class storing typeset results of integer
# numbers, because these can cleanly be represented by a plain string.
# For the same reason, the class name 'TypesetNumber' does not need to
# be augmented by 'fp' (floating-point), because there is no typeset
# result class for integer numbers.


convention_session = upy2.sessions.byprotocol(
        upy2.typesetting.protocol.Convention)

class NumberTypesetter:
    def __init__(self, typeset_positive_sign=None, ceil=None):
        """ Plusses before positive numbers will only be printed when
        *typeset_positive_sign* is true.  Per default such positive
        signs won't be typeset.
        
        When *ceil* is true, discarded portions of the number (due to
        the *precision* handed over to :meth:`typesetfp` or
        :meth:`typesetint`) will increase the absolute value of the
        number represented by the typesetting result.  The default for
        *ceil* is ``False``. """

        if typeset_positive_sign is None:
            typeset_positive_sign = False
        if ceil is None:
            ceil = False

        self.typeset_positive_sign = typeset_positive_sign
        self.ceil = ceil

    def typesetfp(self, number, precision):
        """ Returns a decimal representation of *number* as an
        instance of :class:`TypesetNumber` with a certain precision.

        The rightmost nonzero digit of the representation is at
        position *precision* with decimal weigth 10 ** -(*precision*).
        With *precision* = 2, two digits after the point will be
        typeset.  With *precision* = -1, one digit before the point
        will be zeroed.  With *precision* = 0, all digits before the
        point will be typeset. """

        # Calculate the sign ...

        if number < 0:
            absolute = -number
            sign = convention_session.current().get_negative()
        else:
            absolute = number
            if self.typeset_positive_sign:
                sign = '+'
            else:
                sign = ''

        # Calculate the integer value containing the counting digits
        # ...
        #
        # When e.g. precision = 2, *absolute* needs to be multiplied
        # by 10 ** 2.
        #
        # When e.g. precision = -1, *absolute* needs to be multiplied
        # by 10 ** (-1) prior to int conversion.

        if not self.ceil:
            digitstream_number = int(round(
                absolute * 10 ** (precision)))
        else:
            digitstream_number = int(math.ceil(
                absolute * 10 ** (precision)))

        # Calculate counting digits ...

        digitstream = str(digitstream_number)

        # Typeset the number ...

        if precision <= 0:
            # Append zeros.
            #
            # *digitstream* contains all digits up to the digit at
            # position *precision*.  For *precision* = 0,
            # *digitstream* contains all digits of the result.  For
            # *precision* = -1, one zero needs to be appended to
            # obtain all digits of the typeset number.
            full = digitstream + '0' * -precision

            left = sign + full
            point = ''
            right = ''
        else:
            # precision > 0
            #
            # Prepend zeros.
            #
            # The rightmost digit of *digitstream* represents the
            # digit at *precision*.  There are *precision* digits
            # behind the point. We need a string of at least length
            # *precision* + 1 (at least one digit before the
            # point).
            minimum_length = precision + 1
            full = '0' * (minimum_length - len(digitstream)) + \
                digitstream
            # When *digitstream* already contains at least
            # (*precision* + 1) digits, ``minimum_lenth -
            # len(digitstream)`` is nonpositive.  Multiplying a string
            # ('0') by a nonpositive number returns an empty string.

            # Split the stream.
            #
            # When *precision* = 1, one digit at the r.h.s. needs to
            # be separated.  When *precision* = 2, two digits at the
            # r.h.s. need to be separated.  *precision* is always > 0
            # in this ``else`` branch.
            left = sign + full[:-precision]     # *precision* is > 0.
            point = '.'
            right = full[-precision:]

        return TypesetNumber(left=left, point=point, right=right)

    def typesetint(self, number, precision):
        """ Returns a integer decimal representation of *number* as a
        plain string.

        The interpretation of *precision* is as it is in
        :meth:`typesetfp`, with the exception, that *precision* is
        limited to nonpositive values (*precision* <= 0).
        
        Given *precision* <= 0, typesetting *number* as an integer
        yields a result identical to the ``.left`` attribute of the
        ``TypesetNumber`` instance returned when passing *number*
        through :meth:`typesetfp`.  Most notably, rounding and the
        ``ceil`` mode determined at initialisation will be respected.
        This applies both to typesetting integer numbers when
        *precision* < 0 as well as to round'ing or ceil'ing floating
        point numbers w.r.t. their fractional part.
        
        Providing *precision* > 0 is a ``ValueError``. """

        if precision > 0:
            raise ValueError("Typesetting integers requires a "
                "nonpositive precision")

        # Calculate the sign ...

        if number < 0:
            absolute = -number
            sign = convention_session.current().get_negative()
        else:
            absolute = number
            if self.typeset_positive_sign:
                sign = '+'
            else:
                sign = ''

        # Calculate the integer value containing the counting digits
        # ...
        #
        # When e.g. precision = -1, *absolute* needs to be multiplied
        # by 10 ** (-1) prior to int conversion.

        if not self.ceil:
            digitstream_number = int(round(
                absolute * 10 ** (precision)))
        else:
            digitstream_number = int(math.ceil(
                absolute * 10 ** (precision)))

        # Calculate counting digits ...

        digitstream = str(digitstream_number)

        # Typeset the number ...

        # Append zeros.
        #
        # *digitstream* contains all digits up to digits at
        # position *precision*.  For *precision* = 0,
        # *digitstream* contains all digits of the result.  For
        # *precision* = -1, one zero needs to be appended to
        # obtain all digits of the typeset number.
        full = sign + digitstream + '0' * -precision

        return full
