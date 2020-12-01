import random

from . import Point
from .util import mod_inverse


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

    def generate_group(self) -> list:
        result = []
        for i in range(self.p):
            x = (i**3 + self.a*i + self.b) % self.p
            for j in range(self.p):
                if (j**2 % self.p == x):
                    result.append(Point(i, j))
        return result

    def get_identity_point(self) -> Point:
        return Point(float('inf'), float('inf'))

    def is_identity_point(self, P: Point) -> bool:
        return P == self.get_identity_point()

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

    def generate_key(self):
        # d private key
        self.d = random.randrange(1, self.n)
        # Q public key
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
