import numpy as np
from math import ceil, log2
from numpy.testing import assert_array_equal


def draw_from_binary(size):
    return np.random.randint(0, 2, size).astype(int)


def draw_from_integer(size, modulus):
    return np.random.randint(0, modulus, size).astype(int) % modulus


def draw_from_normal(size, modulus, loc=0, scale=2):
    return np.random.normal(loc, scale, size).astype(int) % modulus


def bit_decomp(vector, q):
    l = ceil(log2(q))
    result = []
    for elem in vector:
        for i in range(l):
            result.append((elem // 2 ** i) % 2)
    return np.array(result)


def powers_of_two(vector, q):
    l = ceil(log2(q))
    result = []
    for elem in vector:
        for i in range(l):
            result.append((elem * 2 ** i) % q)
    return np.array(result)


# --- Tests ---
def tests():
    q = 2 ** 16
    x = np.array([1, 2, 3, 4])
    n = len(x)
    # --- Bit Decomposition ---
    x_p = bit_decomp(x, q)
    assert x_p.shape == (n * ceil(log2(q)),)
    assert_array_equal(x_p, np.array([
        1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]))
    # --- Powers of Two ---
    x_p = powers_of_two(x, q)
    assert x_p.shape == (n * ceil(log2(q)),)
    assert_array_equal(x_p, np.array([
        1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048,
        4096, 8192, 16384, 32768, 2, 4, 8, 16, 32, 64, 128, 256,
        512, 1024, 2048, 4096, 8192, 16384, 32768, 0, 3, 6, 12, 24,
        48, 96, 192, 384, 768, 1536, 3072, 6144, 12288, 24576, 49152, 32768,
        4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192,
        16384, 32768, 0, 0
    ]))
    # -- Dot Product of Bit Decomposition and Powers of Two ---
    x = np.array([1, 2, 3, 4])
    y = np.array([5, 6, 7, 8])
    assert_array_equal(np.dot(x, y) % q, (np.dot(bit_decomp(x, q), powers_of_two(y, q))) % q)


if __name__ == '__main__':
    tests()
