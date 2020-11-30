import collections
import random


def extended_gcd(a, b):
    if a == 0:  # base
        return (b, 0, 1)
    g, y, x = extended_gcd(b % a, a)  # recc
    return (g, x - (b // a) * y, y)

def mod_inverse(a, m):
    a = a % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:  # not exists
        raise Exception('Modular inverse not exists!')
    return x % m


Point = collections.namedtuple('Point', ['x', 'y'])


class ECC:
    def __init__(self, a, b, p):
        # initial check
        assert (4 * a ** 3 + 27 * b ** 2 != 0)
        # properties
        self.a = a
        self.b = b
        self.p = p
        self.Group = self.generate_group()
        self.n = len(self.Group) + 1
        self.G = self.Group[random.randrange(0, len(self.Group))]
        self.generate_key()

    # tested, hasil sama dengan di slide dan web
    def generate_group(self):
        result = []
        for i in range(self.p):
            x = (i**3 + self.a*i + self.b) % self.p
            for j in range(self.p):
                if (j**2 % self.p == x):
                    result.append(Point(i, j))
        return result

    def get_identity_point(self):
        return Point(float('inf'), float('inf'))

    def is_identity_point(self, P: Point):
        return P == self.get_identity_point()

    # tested, hasil sama dengan web dan slide
    def add_points(self, P: Point, Q: Point) -> Point:
        # TODO: remove
        assert isinstance(P, Point)
        assert isinstance(Q, Point)

        # addition with identity point
        if self.is_identity_point(P):
            return Q
        if self.is_identity_point(Q):
            return P
        # calculate gradient m
        if P == Q:
            if (P.y == 0):
                return self.get_identity_point()
            else:
                # m = ((3*(P.x**2) + self.a ) * pow(2 * P.y, -1, self.p)) % self.p
                m = ((3 * (P.x ** 2) + self.a) * mod_inverse(2 * P.y, self.p)) % self.p
        else:
            if (P.x - Q.x) == 0:
               return self.get_identity_point()
            else:
                # m = ((Q.y - P.y) * pow(Q.x - P.x, -1, self.p)) % self.p
                m = ((Q.y - P.y) * mod_inverse(Q.x - P.x, self.p)) % self.p
        # calculate x y
        x = (m ** 2 - P.x - Q.x) % self.p
        y = (m * (P.x - x) - P.y) % self.p
        return Point(x, y)

    # tested, hasil sama degnan web dan slide
    def multiply2(self, k: int, P: Point) -> Point:
        # TODO: remove
        assert isinstance(P, Point)

        Q = P
        for i in range(k-1):
            Q = self.add_points(Q, P)
        return Q

    # tested, hasil sama degnan web dan slide
    def multiply(self, k: int, P: Point) -> Point:
        # TODO: remove
        assert isinstance(P, Point)

        X, Q = P, self.get_identity_point()
        while k:
            if k & 1:
                Q = self.add_points(Q, X)
            X = self.add_points(X, X)
            k >>= 1
        return Q

    # d private key, Q public key
    def generate_key(self):
        self.d = random.randrange(1, self.n)
        self.Q = self.multiply(self.d, self.G)
        while (self.is_identity_point(self.Q) or (self.Q.x % self.n == 0)):
            self.d = random.randrange(1, self.n)
            self.Q = self.multiply(self.d, self.G)

    def __str__(self):
        res = ""
        res += "========== Parameter Curva =========\n"
        res += "a: " + str(self.a) + "\n"
        res += "b: " + str(self.b) + "\n"
        res += "n: " + str(self.n) + "\n"
        res += "base point (G): " + str(self.G) + "\n"
        res += "private key (d): " + str(self.d) + "\n"
        res += "public key (Q): " + str(self.Q) + "\n"
        res += "====================================\n"
        return res


class ECDSA:
    def __init__(self, curve: ECC):
        # TODO: remove
        assert isinstance(curve, ECC)

        self.curve = curve

    def sign(self, hash: int) -> (int, int):
        # calculate z: L_n leftmost byte of hash, n is bit_length of self.curve.n
        z = hash >> max(0, (hash.bit_length() - self.curve.n.bit_length()))
        while True:
            # generate random number k from [1, n - 1]
            k = random.randrange(1, self.curve.n)
            # calculate point (x1, y1) = k x G
            x1, y1 = self.curve.multiply(k, self.curve.G)
            # check 1
            r = x1 % self.curve.n
            if r == 0: continue
            # check 2
            k_inv = mod_inverse(k, self.curve.n)
            s = (k_inv * (z + (r * self.curve.d))) % self.curve.n
            if s == 0: continue
            # valid
            break
        return (r, s)

    def verify(self, hash: int, r: int, s: int) -> bool:
        # check r and s in [1, n - 1]
        if not all(list((1 <= r, s < self.curve.n))):
            return False
        # calculate z: L_n leftmost byte of hash, n is bit_length of self.curve.n
        z = hash >> max(0, (hash.bit_length() - self.curve.n.bit_length()))
        # calculate u1 = zs^-1 and u2 = rs^-1
        # s_inv = pow(s, -1, self.curve.n)
        s_inv = mod_inverse(s, self.curve.n)
        u1 = (z * s_inv) % self.curve.n
        u2 = (r * s_inv) % self.curve.n
        # calculate point (x1, y1) = u1 x G + u2 x Q
        temp1 = self.curve.multiply(u1, self.curve.G)
        temp2 = self.curve.multiply(u2, self.curve.Q)
        x1, y1 = self.curve.add_points(temp1, temp2)
        # check if (x1, y1) == O
        if self.curve.is_identity_point(Point(x1, y1)):
            return False
        # check r == x1 mod n
        return r == x1 % self.curve.n

    def sign_old(self, hash: int):
        k = random.randrange(1, self.curve.n)
        x1, y1 = self.curve.multiply(k, self.curve.G)
        while (((x1, y1) == (float('inf'), float('inf'))) or (x1 % self.curve.n == 0)):
            k = random.randrange(1, self.curve.n)
            x1, y1 = self.curve.multiply(k, self.curve.G)

        r = x1 % self.curve.n
        # s = (pow(k, -1, self.curve.n) * (hash + self.curve.d * r) ) % self.curve.n
        s = (mod_inverse(k, self.curve.n) * (hash + self.curve.d * r)) % self.curve.n
        while (s == 0):
            k = random.randrange(1, self.curve.n)
            x1, y1 = self.curve.multiply(k, self.curve.G)
            while (((x1,y1)==(float('inf'), float('inf'))) or (x1%self.curve.n == 0)):
                k = random.randrange(1, self.curve.n)
                x1, y1 = self.curve.multiply(k, self.curve.G)
            r = x1 % self.curve.n
            # s = (pow(k, -1, self.curve.n) * (hash + self.curve.d * r) ) % self.curve.n
            s = (mod_inverse(k, self.curve.n) * (hash + self.curve.d * r) ) % self.curve.n
        print("output rs :", r, s)
        return (r, s)

    def verify_old(self, hash: int, r: int, s: int):
        if ((r < self.curve.n-1) and (r > 1)):
            if ((s < self.curve.n-1) and (s > 1)):
                print("r dan s valid")
        print("input rs :", r,s)
        # w = pow(s, -1, self.curve.n)
        w = mod_inverse(s, self.curve.n)
        u1 = (hash * w) % self.curve.n
        u2 = (r * w) % self.curve.n
        print("u1 :", u1)
        print("u2 :", u2)
        temp1 = self.curve.multiply(u1, self.curve.G)
        temp2 = self.curve.multiply(u2, self.curve.Q)
        print("u1*G :", temp1)
        print("u2*Q :", temp2)
        x1, y1 = self.curve.add_points(temp1, temp2)
        print("hasil penjumlahan :",x1, y1)
        v = x1 % self.curve.n
        print("v :", v)
        print("r :", r)
        return v==r


if __name__ == "__main__":
    ecc = ECC(1, 4, 23)
    print(ecc)
    # print(ecc.multiply(3, Point(10, 18)))

    # for i in range(35):
    #     print(i)
    #     print(ecc.multiply(i, Point(0, 21)))

    ecdsa = ECDSA(ecc)
    r, s = ecdsa.sign(2000)

    if ecdsa.verify(2000, r, s):
        print("Berhasil verifikasi")
    else :
        print("Gagal verifikasi")

    # ecc = ECC(1, 6, 11)
    # print(ecc)
    # r = ecc.add_points(Point(2, 4), Point(5, 9))
    # print(r)
    # r = ecc.multiply(2, Point(2, 4))
    # print(r)
