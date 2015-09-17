# Developed since: September 2015
# Build upon 'decimal2.py', part of upy v0.4.11b, developed since
# August 2008.

""" Number analysis module. """


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
   
    When *weight* is larger than *val*, the expression ``value %
    weight`` returns *value* unchanged.  *weight* is larger than
    *val* iff. all digits in the decimal representation of *val*
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
   
     2.   Move right (increase *pos*) until there are digits
          non-right to *pos*.
   
     3.   Move left (decrease *pos*) until there are no longer
          digits non-right of *pos*.
   
          At this point, we are one digit left of the left-most
          non-zero digit of *number*.
   
     4.   The position of the left-most non-zero digit of *number*
          is hence one digit right of the position resulting from
          (3.).
   
    When *number* is zero, it does not feature any non-zero digits,
    and hence does not exhibit a left-most non-zero digit.  We return
    ``None`` in that case. """

    if number == 0:
        return None
    number = abs(number)

    pos = 0
    while (number - number % (10 ** -pos)) == 0:
        pos += 1
    while (number - number % (10 ** -pos)) != 0:
        pos -= 1
    return pos
