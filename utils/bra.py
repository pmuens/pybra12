import numpy as np
from math import ceil, log2

from utils.core import powers_of_two, bit_decomp, draw_from_integer, draw_from_normal
from utils.regev import secret_keygen as regev_secret_keygen
from utils.regev import public_keygen as regev_public_keygen
from utils.regev import encrypt as regev_encrypt
from utils.regev import decrypt as regev_decrypt


def keygen(L, n, q):
    sks = [regev_secret_keygen(n, q) for _ in range(L + 1)]  # NOTE: We're adding `+ 1` here because range is exclusive
    pk = regev_public_keygen(sks[0], n, q)
    evks = []
    for i, _ in enumerate(sks):
        # Shifting one index such that we omit the first `sk` which we've explicitly computed a `pk` for
        i = i + 1
        if i == len(sks):
            break
        sk_curr = sks[i]
        sk_prev = sks[i - 1]
        v_prev = np.insert(sk_prev, 0, 1)
        # See https://www.math3ma.com/blog/the-tensor-product-demystified for a good explanation
        sk_prev_h = np.tensordot(bit_decomp(v_prev, q), bit_decomp(v_prev, q), axes=0).flatten()
        evk = switch_keygen(sk_prev_h, sk_curr, q)
        # --- Tests ---
        assert sk_prev_h.shape == (((n + 1) * ceil(log2(q))) ** 2,)
        evks.append(evk)
    sk = sks[L]
    return pk, evks, sk


def encrypt(pk, m, n, q):
    return regev_encrypt(pk, m, n, q)


def decrypt(sk, c, q):
    return regev_decrypt(sk, c, q)


def add(evk, c_1, c_2, q):
    num_zeros = len(c_1) - 1
    addition = powers_of_two(c_1 + c_2, q)
    trivial_c = powers_of_two(np.array([1] + [0] * num_zeros), q)
    c_add_h = np.tensordot(addition, trivial_c, axes=0).flatten()
    return switch_key(evk, c_add_h, q)


def mult(evk, c_1, c_2, q):
    c_1_p = powers_of_two(c_1, q)
    c_2_p = powers_of_two(c_2, q)
    c_mul_h = np.tensordot(c_1_p, c_2_p, axes=0).flatten()
    result = np.round(2 / q * c_mul_h)
    return switch_key(evk, result, q)


# Allows to switch ciphertexts under `s` into ciphertexts under `(1, t)`
def switch_keygen(s, t, q):
    s_bin = powers_of_two(s, q)
    n_s = s.shape[0]
    n_h_s = s_bin.shape[0]
    n_t = t.shape[0]
    A = draw_from_integer((n_h_s, n_t), q)
    e = draw_from_normal(n_h_s, q)
    b = (A.dot(t) + e + s_bin) % q
    P = np.column_stack((b, -A))
    # --- Tests ---
    c_s = draw_from_integer(n_s, q)
    c_t = switch_key(P, c_s, q)
    assert np.dot(c_s, s) % q == (np.dot(c_t, np.insert(t, 0, 1)) - np.dot(bit_decomp(c_s, q), e)) % q
    return P


def switch_key(evk, c, q):
    return evk.T.dot(bit_decomp(c, q)) % q


# --- Tests ---
def tests():
    n = 3
    q = 2 ** 16
    L = 1
    # --- Key Switching ---
    # `s` is the secret key we use for our "original" encryption
    _, _, sk = keygen(L, n, q)
    # `t` is the new key we want to encrypt our ciphertext under
    _, _, tk = keygen(L, n, q)
    evk = switch_keygen(sk, tk, q)
    assert evk.shape == (n * ceil(log2(q)), n + 1)
    # --- Keygen ---
    pk, evks, sk = keygen(L, n, q)
    assert len(evks) == L
    # --- Add ---
    # 0 + 0
    m_1 = 0
    m_2 = 0
    c_1 = encrypt(pk, m_1, n, q)
    c_2 = encrypt(pk, m_2, n, q)
    result = add(evks[-1], c_1, c_2, q)
    p = decrypt(sk, result, q)
    assert result.shape == (n + 1,)
    assert p == (m_1 + m_2) % 2
    # 1 + 0
    m_1 = 1
    m_2 = 0
    c_1 = encrypt(pk, m_1, n, q)
    c_2 = encrypt(pk, m_2, n, q)
    result = add(evks[-1], c_1, c_2, q)
    p = decrypt(sk, result, q)
    assert result.shape == (n + 1,)
    assert p == (m_1 + m_2) % 2
    # 1 + 1
    m_1 = 1
    m_2 = 1
    c_1 = encrypt(pk, m_1, n, q)
    c_2 = encrypt(pk, m_2, n, q)
    result = add(evks[-1], c_1, c_2, q)
    p = decrypt(sk, result, q)
    assert result.shape == (n + 1,)
    assert p == (m_1 + m_2) % 2
    # --- Mult ---
    # 0 * 0
    m_1 = 0
    m_2 = 0
    c_1 = encrypt(pk, m_1, n, q)
    c_2 = encrypt(pk, m_2, n, q)
    result = mult(evks[-1], c_1, c_2, q)
    p = decrypt(sk, result, q)
    assert result.shape == (n + 1, )
    assert p == (m_1 * m_2) % 2
    # 1 * 0
    m_1 = 1
    m_2 = 0
    c_1 = encrypt(pk, m_1, n, q)
    c_2 = encrypt(pk, m_2, n, q)
    result = mult(evks[-1], c_1, c_2, q)
    p = decrypt(sk, result, q)
    assert result.shape == (n + 1, )
    assert p == (m_1 * m_2) % 2
    # 1 * 1
    m_1 = 1
    m_2 = 1
    c_1 = encrypt(pk, m_1, n, q)
    c_2 = encrypt(pk, m_2, n, q)
    result = mult(evks[-1], c_1, c_2, q)
    p = decrypt(sk, result, q)
    assert result.shape == (n + 1, )
    assert p == (m_1 * m_2) % 2


if __name__ == '__main__':
    tests()
