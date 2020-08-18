import random
from project import constants


def is_prime(num: int, k: int) -> bool:
    """
    implements Miller-Rabin algorithm to test the primality of a number
    :param num: a positive integer
    :param k: the number of iterations, impacting accuracy; the larger the number, the higher accuracy will be
    :return: True if it's a prime, False otherwise
    """
    # Corner cases
    if num <= 1 or num == 4:
        return False
    if num <= 3:
        return True

    # Find r such that n = 2^d * r + 1 for some r >= 1
    d = num - 1
    while d % 2 == 0:
        d //= 2

    # Iterate given number of 'k' times
    for i in range(k):
        if not __miller_test(d, num):
            return False

    return True


def __miller_test(d: int, num: int) -> bool:
    """
    find a odd number of d such that num - 1 = d * 2^r
    :param d: an odd number that num - 1 = d * 2^r for r >= 1
    :param num: the number needs to be check against
    :return: True if num is prime, False if it's a composite
    """

    # Pick a random number in [2..n-2]
    # Corner cases make sure that n > 4
    a = 2 + random.randint(1, num - 4)

    # Compute a^d % n
    x = pow(a, d, num)

    if x == 1 or x == num - 1:
        return True

    # Keep squaring x while one of the following doesn't happen
    # (i) d does not reach n-1
    # (ii) (x^2) % n is not 1
    # (iii) (x^2) % n is not n-1
    while d != num - 1:
        x = (x * x) % num
        d *= 2

        if x == 1:
            return False
        if x == num - 1:
            return True

    # Return composite
    return False


def equals(a, b) -> bool:
    """
    compares two values and check if their values are equal
    @input: two integers a, b
    @output: True if a, b have same values, False otherwise
    """
    a, b = int(a), int(b)

    return a == b


def is_divisor(a, b) -> bool:
    """
    check if a is a divisor of b
    :param a: a positive integer
    :param b: b positive integer
    :return: True if a is a divisor of b, False otherwise
    """
    a, b = int(a), int(b)

    return a % b == 0


def is_within_range(num, lower_bound: int, upper_bound: int) -> bool:
    """
    check if a number is within a range bounded by upper and lower bound
    :param num: target number needs to be checked against
    :param lower_bound: exclusive lower bound
    :param upper_bound: exclusive upper bound
    :return:  True if number is within this range, False otherwise
    """
    num = int(num)

    if upper_bound < lower_bound:
        raise ValueError("bounds are incorrect")

    return lower_bound < num < upper_bound


def is_within_set_zq(num) -> bool:
    """
    check if a number is within set Zq,
    :param num: target number needs to be checked against
    :return:  True if  0 <= num < q , False otherwise
    """
    num = int(num)

    # exclusive bounds, set lower bound to -1
    return is_within_range(num, 0 - 1, constants.SMALL_PRIME)


def is_within_set_zrp(num) -> bool:
    """
    check if a number is within set Zrp, 0 < num < p and num ^ q mod p = 1
    :param num: target number needs to be checked against
    :return: True if  0 < num < p and num ^ q mod p = 1 , False otherwise
    """
    num = int(num)

    return is_within_range(num, 0, constants.LARGE_PRIME) and equals(
        pow(num, constants.SMALL_PRIME, constants.LARGE_PRIME), 1)


def mod(dividend, divisor) -> int:
    """
    compute the modulus number by calculating dividend % divisor
    :param dividend: dividend, the number in front
    :param divisor: divisor, the number behind
    :return: dividend % divisor
    """
    dividend, divisor = int(dividend), int(divisor)

    return dividend % divisor


def multiply(a, b, mod_num=1) -> int:
    """

    :param a:
    :param b:
    :param mod_num:
    :return:
    """
    a, b = int(a), int(b)
    if a >= mod_num:
        a = a % mod_num
    if b >= mod_num:
        b = b % mod_num

    return a * b % mod_num
