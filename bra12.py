from dataclasses import dataclass

from utils.bra import keygen, encrypt, decrypt, add, mult


@dataclass
class Context:
    n: int
    q: int
    L: int


class Bra12:
    def __init__(self, ctx):
        self.ctx = ctx
        pk, evks, sk = keygen(ctx.L, ctx.n, ctx.q)
        self.pk = pk
        self.evks = evks
        self.sk = sk

    def encrypt(self, message):
        ciphertext = encrypt(self.pk, message, self.ctx.n, self.ctx.q)
        return Ciphertext(ciphertext, self.evks, self.ctx.q)

    def decrypt(self, ciphertext):
        return decrypt(self.sk, ciphertext.inner, self.ctx.q)


class Ciphertext:
    def __init__(self, inner, evks, q):
        self.inner = inner
        self.evks = evks
        self.q = q

    def __add__(self, other):
        evk = self.evks[-1]
        return Ciphertext(
            add(evk, self.inner, other.inner, self.q),
            # Remove the key we've used used above (NOTE: An operation might not equal one circuit level)
            self.evks[:-1],
            self.q
        )

    def __mul__(self, other):
        evk = self.evks[-1]
        return Ciphertext(
            mult(evk, self.inner, other.inner, self.q),
            # Remove the key we've used used above (NOTE: An operation might not equal one circuit level)
            self.evks[:-1],
            self.q
        )
