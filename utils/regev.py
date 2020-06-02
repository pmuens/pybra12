import numpy as np
from math import log2
from random import choice
from numpy.testing import assert_array_equal

from utils.core import draw_from_binary, draw_from_integer, draw_from_normal


def secret_keygen(n, q):
    return draw_from_integer(n, q)


def public_keygen(s, n, q):
    N = (n + 1) * int((log2(q) + 1))
    A = draw_from_integer((N, n), q)
    e = draw_from_normal(N, q)
    b = (A.dot(s) + e) % q
    P = np.column_stack((b, -A))
    # --- Tests ---
    # Prepend a 1 to the secret key
    v = np.insert(s, 0, 1)
    # We should be able to extract the error from the Public key via the Secret Key
    assert_array_equal(P.dot(v) % q, e)
    return P


def encrypt(pk, m, n, q):
    N = (n + 1) * int(log2(q) + 1)
    r = draw_from_binary(N)
    # Embed `m` at MSB position into a binary vector
    m = np.array([m] + [0] * n)
    c = (pk.T.dot(r) + q // 2 * m) % q
    return c


def decrypt(sk, c, q):
    # Prepend 1 to the secret key
    v = np.insert(sk, 0, 1)
    return int((round(2 * ((c.dot(v) % q) / q))) % 2)


# --- Tests ---
def tests():
    n = 3
    q = 2 ** 16
    # --- Secret Key generation ---
    sk = secret_keygen(n, q)
    assert sk.shape == (n,)
    # --- Public Key generation ---
    sk = secret_keygen(n, q)
    pk = public_keygen(sk, n, q)
    assert pk.shape == ((n + 1) * (log2(q) + 1), n + 1)
    # --- Encryption ---
    sk = secret_keygen(n, q)
    pk = public_keygen(sk, n, q)
    c = encrypt(pk, 1, n, q)
    assert c.shape == (n + 1,)
    # --- Decryption ---
    sk = secret_keygen(n, q)
    pk = public_keygen(sk, n, q)
    m = choice((0, 1))
    c = encrypt(pk, m, n, q)
    p = decrypt(sk, c, q)
    assert m == p


if __name__ == '__main__':
    tests()
