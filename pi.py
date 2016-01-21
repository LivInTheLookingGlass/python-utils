def pi_digits():
    """generator for digits of pi"""
    k, a, b, a1, b1 = 2, 4, 1, 12, 4
    while True:
        p, q, k = k * k, 2 * k + 1, k + 1
        a, b, a1, b1 = a1, b1, p * a + q * a1, p * b + q * b1
        d, d1 = a / b, a1 / b1
        while d == d1:
            yield int(d)
            a, a1 = 10 * (a % b), 10 * (a1 % b1)
            d, d1 = a / b, a1 / b1


def pi(precision, rounding=True):
    """Returns pi to an arbitrary precision"""
    from decimal import Decimal, DecimalTuple
    gen = pi_digits()
    tup = [next(gen) for x in range(precision + 1)]
    if next(gen) >= 5 and rounding:
        tup[len(tup) - 1] += 1
        r = 1
        while tup[len(tup) - r] == 10:
            tup[len(tup) - r] = 0
            tup[len(tup) - (r + 1)] += 1
            r += 1
    return Decimal(DecimalTuple(sign=0, digits=tuple(tup), exponent=-precision))
