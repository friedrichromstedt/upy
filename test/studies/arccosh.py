# Developed since: May 2020

import random
import numpy


def investigate(position, prediction):
    """ Investigate the correctness of the symbolic prediction
    *prediction* of the derivative of ``arccosh`` at position
    *position*. """
    # This function borrows code deliberately from the Test Suite.

    specimen = numpy.arccosh
    epsilon = 1e-4

    position0 = position
    position1 = position + epsilon
    position1j = position + epsilon * 1j

    value0 = specimen(position0)
    value1 = specimen(position1)
    value1j = specimen(position1j)

    approximation1 = (value1 - value0) / epsilon
    approximation1j = -1j * (value1j - value0) / epsilon

    approximation_uncertainty = abs(approximation1j - approximation1)
    mean_approximation = (approximation1 + approximation1j) / 2

    relative_approximation_uncertainty = \
            approximation_uncertainty / abs(mean_approximation)
    if relative_approximation_uncertainty > 0.01:
        print("F   ({position.real: .3f}, {position.imag: .3f})".
                format(position=position))
#        raise DerivativeApproximationError(
#                ("The approximation of {specimen} "
#                 "couln't be approximated successfully at "
#                 "{position}.  Relative approximation uncertainty: "
#                 "{rel:.3f}").\
#                format(specimen=specimen, position=position,
#                    rel=relative_approximation_uncertainty)
#        )
        return False

    difference = numpy.abs(prediction - mean_approximation)
    if difference > 2 * approximation_uncertainty:
        print(("NOK ({position.real: .3f}, {position.imag: .3f})"
               " ({q.real: .3f}, {q.imag: .3f})").
                format(position=position,
                        q=(mean_approximation / prediction)))
#        raise DerivativeVerificationError(
#            ('Could not verify the derivative of '
#             '{specimen} at {position}.  Prediction: {prediction}, '
#             'approximation: {approximation} with uncertainty '
#             '{uncertainty}, Excess: {excess:.2f}').\
#            format(specimen=specimen, position=position,
#                prediction=prediction,
#                approximation=mean_approximation,
#                uncertainty=approximation_uncertainty,
#                excess=(difference / approximation_uncertainty))
#        )
    else:
        print("OK  ({position.real: .3f}, {position.imag: .3f})".
                format(position=position))
        return True

# Do some investigations and collect results ...

print("Investigating behaviour with complex univariate input ...")

ok = []
nok = []

random.seed( 710)
for i in range(50):
    z = random.gauss(0, 1) + 1j * random.gauss(0, 1)
    if investigate(position=z, prediction=(1 / numpy.sqrt(z ** 2 - 1))):
        ok.append(z)
    else:
        nok.append(z)

print("")
print("OK:")
for z in ok:
    print("({z.real: .3f}, {z.imag: .3f})".format(z=z))

print("")
print("NOK:")
for z in nok:
    print("({z.real: .3f}, {z.imag: .3f})".format(z=z))

# From the OK/NOK investigations, I got the impression that the
# failure of prediction depends on the sign of the position's real
# component.  So I tried to verify this ...

print("")
print("Trying to narrow down to x < 0 ...")

def narrow():
    """ Try to narrow failure of derivative prediction down to the
    sign of the position's real component. """

    narrowed = True
    random.seed( 724)
    for i in range(1000):
        x = random.gauss(0, 1)
        y = random.gauss(0, 1)
        z = x + 1j * y

        correct = investigate(
                position=z, prediction=(1 / numpy.sqrt(z ** 2 - 1)))
        expected = (x > 0)  # The prediction is expected to be correct.

        if (not correct and expected) or (correct and not expected):
            narrowed = False

    if narrowed:
        print("Narrowed failure down to x < 0.")
    else:
        print("Could not narrow failure down to x < 0.")

narrow()  # This narrows failure successfully down to x < 0.

# For arguments with zero imaginary component the prediction is wrong
# for apparently x < -1:

print("")
print("Testing positions without imaginary component:")

random.seed( 752)
for i in range(50):
    x = random.gauss(0, 1) + 0j
    investigate(position=x, prediction=(1 / numpy.sqrt(x ** 2 - 1)))

print("Apparently failure for x < -1.")

print("")
print("Testing positions with a small imaginary component:")

random.seed( 757)
for i in range(20):
    x = random.gauss(0, 1) + 0.01j
    investigate(position=x, prediction=(1 / numpy.sqrt(x ** 2 - 1)))

print("Failure apparently for x < 0.")

print("")
print("Testing independence of ``cosh`` on the sign of an arbitrary argument:")

random.seed(1330)
for i in range(20):
    z = random.gauss(0, 1) + 1j * random.gauss(0, 1)
    if not numpy.allclose(numpy.cosh(z), numpy.cosh(-z)):
        print("{i:2d} NOK: ({z.real: .3f}, {z.imag: .3f})".format(i=i, z=z))
    else:
        print("{i:2d}  OK: ({z.real: .3f}, {z.imag: .3f})".format(i=i, z=z))

print("Apparently ``cosh`` is invariant under argument sign swap.")
