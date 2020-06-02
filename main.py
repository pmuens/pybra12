import sys

from bra12 import Context, Bra12
from utils.core import tests as tests_utils_core
from utils.regev import tests as tests_utils_regev
from utils.bra import tests as tests_utils_bra


def main():
    n = 3
    q = 2 ** 16
    L = 1
    ctx = Context(n, q, L)
    bra = Bra12(ctx)
    # Addition 1
    m_1 = 0
    m_2 = 0
    c_1 = bra.encrypt(m_1)
    c_2 = bra.encrypt(m_2)
    res = bra.decrypt(c_1 + c_2)
    print(f'{m_1} + {m_2} = {res}')
    assert res == (m_1 + m_2) % 2
    # Addition 2
    m_1 = 0
    m_2 = 1
    c_1 = bra.encrypt(m_1)
    c_2 = bra.encrypt(m_2)
    res = bra.decrypt(c_1 + c_2)
    print(f'{m_1} + {m_2} = {res}')
    assert res == (m_1 + m_2) % 2
    # Multiplication 1
    m_1 = 1
    m_2 = 0
    c_1 = bra.encrypt(m_1)
    c_2 = bra.encrypt(m_2)
    res = bra.decrypt(c_1 * c_2)
    print(f'{m_1} * {m_2} = {res}')
    assert res == (m_1 * m_2) % 2
    # Multiplication 2
    m_1 = 1
    m_2 = 1
    c_1 = bra.encrypt(m_1)
    c_2 = bra.encrypt(m_2)
    res = bra.decrypt(c_1 * c_2)
    print(f'{m_1} * {m_2} = {res}')
    assert res == (m_1 * m_2) % 2
    # Multiplication 3
    m_1 = 0
    m_2 = 0
    c_1 = bra.encrypt(m_1)
    c_2 = bra.encrypt(m_2)
    res = bra.decrypt(c_1 * c_2)
    print(f'{m_1} * {m_2} = {res}')
    assert res == (m_1 * m_2) % 2


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    if len(sys.argv) > 1 and 'test' in sys.argv[1]:
        tests_utils_core()
        tests_utils_regev()
        tests_utils_bra()
        print('Success: 3/3')
