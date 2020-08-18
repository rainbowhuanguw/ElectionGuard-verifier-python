import hashlib
from typing import (
    Union,
    Sequence
)
from project import constants


# main hash function
def hash_elems(*a):
    h = hashlib.sha256()
    h.update("|".encode("utf-8"))

    for x in a:

        if not x:
            # This case captures empty lists and None, nicely guaranteeing that we don't
            # need to do a recursive call if the list is empty. So we need a string to
            # feed in for both of these cases. "None" would be a Python-specific thing,
            # so we'll go with the more JSON-ish "null".
            hash_me = "null"

        elif isinstance(x, str):
            # strings are iterable, so it's important to handle them before the following check
            hash_me = x
        elif isinstance(x, Sequence):
            # The simplest way to deal with lists, tuples, and such are to crunch them recursively.
            hash_me = str(hash_elems(*x))
        else:
            hash_me = str(x)
        h.update((hash_me + "|").encode("utf-8"))

    # Note: the returned value will range from [1,Q), because zeros are bad
    # for some of the nonces. (g^0 == 1, which would be an unhelpful thing
    # to multiply something with, if you were trying to encrypt it.)

    # Also, we don't need the checked version of int_to_q, because the
    # modulo operation here guarantees that we're in bounds.
    # return int_to_q_unchecked(
    #     1 + (int.from_bytes(h.digest(), byteorder="big") % Q_MINUS_ONE)
    # )

    return int.from_bytes(h.digest(), byteorder="big") % (constants.SMALL_PRIME - 1)
