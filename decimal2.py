# Developed since: Aug 2008

import math

"""Supplies various operations with numbers in decimal system."""


class IntPlus:
    """Represents number in Z+ = Z + {Infinity}.  Read-only attributes:
    
    .z - The number.
    .infinite - The instance represents Infinity."""

    def __init__(self, z = None, infinite = None):
        """Initialise from number Z, or specify infinite as true."""

        if infinite:
            self.infinite = True
            self.z = None
        else:
            self.z = z
            self.infinite = False

    def __str__(self):
        if self.infinite:
            return "infinite"
        else:
            return str(self.z)

    def __repr__(self):
        if self.infinite:
            return "IntPlus(infinite = True)"
        else:
            return "IntPlus(z = %r)" % self.z


class DecimalStrings:
    """Holds the result of formatting a number."""

    def __init__(self, str_left, str_point, str_right):
        self.str_left = str_left
        self.str_point = str_point
        self.str_right = str_right

    def __str__(self):
        return self.str_left + self.str_point + self.str_right


class DecimalNumber:
    """Calculates the leftmost digit, and formats real numbers.  All values 
    given to __init__() are read-write, except for .precision, which must be
    set via .set_precision(), and .exponent, which must be set via 
    .set_exponent()."""

    def __init__(self, 
            value, 
            precision = None,
            exponent = None, 
            infinite_precision = None,
            enforce_sign = None,
            ceil = None,
            width_sign = None,
            width_left = None,
            width_point = None,
            width_right = None):
        """VALUE is the value to be formatted.  INFINITE_PRECISION is the 
        number of digits used when emulating infinite precision 
        (default 15).  EXPONENT is the power of ten separated up from the
        VALUE.  Example: VALUE = 12.3 and EXPONENT = 1 -> 1.23e1.  Strings 
        returned represent .value_without_exponent up to digit with weight 
        10 ** PRECISION.  If ENFORCE_SIGN is True, return a '+' in front of 
        positive numbers.  If CEIL is True, discarded portions of the number 
        will always increase the value represented by the string.  When
        calculating the parts of the string, WIDTH_* are used.  By default
        IntPlus(infinite = True) is used as PRECISION.  WIDTH_SIGN forces the
        sign to have a certain width, this means, the sign string will be 
        padded with whitespace, right justified.  WIDTH_LEFT is the width of 
        the sign string plus the string before the point, right justified.  
        WIDTH_POINT is the width of the point, center justified.  WIDTH_RIGHT
        is the width of the post-point string, left justified."""

        if exponent is None:
            exponent = 0
        if infinite_precision is None:
            infinite_precision = -15
        if width_sign is None:
            width_sign = 0
        if width_left is None:
            width_left = 0
        if width_point is None:
            width_point = 0
        if width_right is None:
            width_right = 0

        self.value = value
        self.infinite_precision = infinite_precision

        self.enforce_sign = enforce_sign
        self.ceil = ceil

        self.width_sign = width_sign
        self.width_left = width_left
        self.width_point = width_point
        self.width_right = width_right

        self.set_exponent(exponent)
        self.set_precision(precision)

    def set_exponent(self, exponent):
        """Set the exponent to EXPONENT.  It must be integer."""

        self.exponent = exponent
        self.value_without_exponent = self.value * 10 ** (-exponent)

    def set_precision(self, precision):
        """Set the precision to PRECISION.  If it is an IntPlus instance, it
        will be taken over, else an IntPlus instance will be created."""

        if isinstance(precision, IntPlus):
            self.precision = precision
        elif precision is None:
            self.precision = IntPlus(z = self.infinite_precision)
        else:
            self.precision = IntPlus(z = precision)

    def get_leftmost_digit(self, guess = None):
        """The position of the leftmost digit of .value_without_exponent in 
        decimal representation.  A position of zero means, that the leftmost 
        digit is the digit with weight 10 ** 0.  Other return values RETURN 
        mean, that the leftmost non-zero digit has weight 10 ** RETURN.  Thus 
        nonnegative RETURNs are before the point in "fixed-point" 
        representation, and negative RETURNs will be behind the point.
        
        To obtain a real value with the leftmost non-zero digit at weight 1, 
        use the expression VALUE * 10 ** (-RETURN).
        
        Note that the return value is an instance of class IntPlus, which may
        represent infinity too (in case .value_without_exponent == 0).
        
        You can supply an initial position of the search via GUESS."""

        if self.value == 0:
            return IntPlus(infinite = True)
        
        # When we are at a certain digit position, the expression:
        #
        #       10 ** exponent
        #
        # represents this digit.  Thus the expression:
        #
        #       value % (10 ** exponent)
        #
        # gives the part of the value right of this digit.  Example: For
        # VALUE = 12.3, and EXPONENT = 0, 12.3 % (10 ** 0) = 12.3 % 1 = 0.3.
        # Thus subtracting this expression eliminates all this parts of the
        # value, and leaves the part of the value non-right of the digit:
        #
        #       value - value % (10 ** exponent)    (1)
        #
        # For the example above: 12.3 - 12.3 % (10 ** 0) = 12.3 - 0.3 = 12.0
        # Thus, the expression (1) is nonzero, if and only if there are 
        # digits in VALUE non-right of the digit given by EXPONENT.
        
        # There are at each position two cases:
        #
        # 1.  (1) is nonzero.  There are digits non-right of the position.  
        #     This means, the digit is itself non-left of the leftmost digit.  
        # 1.  (1) is zero.  There are no digits non-right of the position.
        #     All digits are right of the position.  This means, the digit is 
        #     left of the leftmost digit.
        #
        # Examples for VALUE = 12.3:  EXPONENT = 2 -> zero, position left
        # of leftmost digit.  EXPONENT = 1 -> nonzero, non-left.  EXPONENT = 0
        # -> nonzero, position 0 non-left of leftmost digit.

        # To ensure that the resulting position is /exactly/ at the left-most
        # digit, the following approach suffices:
        #
        # 1.  Go right until (1) is nonzero.  This means, go right until we
        #     are non-left of the leftmost digit.
        # 2.  Go left until (1) is zero.  This means, go left until we are
        #     left of the leftmost digit.
        #
        # Because after (1.), we are non-left of the leftmost digit, (2.) 
        # breaks when we are at the rightmost position left of the digit, 
        # which is /next left to/ the position of the digit.
        #
        # 3.  Go one step right.

        # Find out the initial position ...
        
        if guess is None:
            # As a first guess, use the position at weight 1.
            exponent = 0
        else:
            # Use the guess given.
            exponent = guess

        # Use abs() because the % operations do nonsense else ...

        value = abs(self.value_without_exponent)

        # Go right until (1) is nonzero ...
        
        while (value - value % (10 ** exponent)) == 0:
            exponent -= 1
    
        # Go left until (1) is zero ...

        while (value - value % (10 ** exponent)) != 0:
            exponent += 1

        # Go one step right ...

        exponent -= 1

        return IntPlus(z = exponent)

    def get_strings(self):
        """Return the string representing this DecimalNumber.  Note that
        the string will represent .value_without_exponent, and not .value."""

        # Calculate the value to use and the string of the sign ...

        if self.value_without_exponent < 0:
            abs_value = -self.value_without_exponent
            str_sign = '-'
        else:
            abs_value = self.value_without_exponent
            if self.enforce_sign:
                str_sign = '+'
            else:
                str_sign = ''

        str_sign = str_sign.rjust(self.width_sign)
        
        # Find out how many digits behind the point to display ...
    
        if self.precision.infinite:
            precision = self.infinite_precision
        else:
            precision = self.precision.z

        # Calculate the integer value to use as digit stream ...

        if not self.ceil:
            digitstream_number = int(round(abs_value * 10 ** (-precision)))
        else:
            digitstream_number = int(math.ceil(abs_value * 10 ** (-precision)))

        # Calculate the digit stream ...

        str_digitstream = str(digitstream_number)

        # Calculate the left and right part of the string ...

        if precision >= 0:
            # Append zeros.
            str_left = str_digitstream + '0' * precision
            str_right = ''
            str_point = ''
        
        elif precision < 0:
            # Prepend zeros.
            str_digitstream = '0' * (-precision + 1 - \
                    len(str_digitstream)) + str_digitstream

            # Split stream.
            str_left = str_digitstream[:precision]
            str_right = str_digitstream[precision:]
            str_point = '.'
        
        # Put the sign in front of the str_left, and rjust the sum of both.
        str_sign_left = (str_sign + str_left).rjust(self.width_left)
        str_point = str_point.center(self.width_point)
        str_right = str_right.ljust(self.width_right)
        
        return DecimalStrings(
                str_left = str_sign_left,
                str_point = str_point,
                str_right = str_right)

    def __str__(self):

        return str(self.get_strings())
