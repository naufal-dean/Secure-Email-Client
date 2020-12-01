import random

from . import Point, get_identity_point, is_identity_point
from .util import mod_inverse


class ECC:
    def __init__(self, a, b, p, n=None, G:Point=None, auto_genkey=True):
        # initial check
        assert (4 * a ** 3 + 27 * b ** 2 != 0)
        # properties
        self.a = a
        self.b = b
        self.p = p
        if n and G:
            self.n = n
            self.G = G
        else:
            self.Group = self.generate_group()
            self.n = len(self.Group) + 1
            self.G = self.Group[random.randrange(0, len(self.Group))]
        if auto_genkey:
            self.generate_key()

    def generate_group(self) -> list:
        result = []
        for i in range(self.p):
            x = (i**3 + self.a*i + self.b) % self.p
            for j in range(self.p):
                if (j**2 % self.p == x):
                    result.append(Point(i, j))
        return result

    def add_points(self, P: Point, Q: Point) -> Point:
        # TODO: remove
        assert isinstance(P, Point)
        assert isinstance(Q, Point)

        # addition with identity point
        if is_identity_point(P):
            return Q
        if is_identity_point(Q):
            return P
        # calculate gradient m
        if P == Q:
            if (P.y == 0):
                return get_identity_point()
            else:
                # m = ((3*(P.x**2) + self.a ) * pow(2 * P.y, -1, self.p)) % self.p
                m = ((3 * (P.x ** 2) + self.a) * mod_inverse(2 * P.y, self.p)) % self.p
        else:
            if (P.x - Q.x) == 0:
               return get_identity_point()
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

        X, Q = P, get_identity_point()
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
        while (is_identity_point(self.Q) or (self.Q.x % self.n == 0)):
            self.d = random.randrange(1, self.n)
            self.Q = self.multiply(self.d, self.G)

    def __str__(self):
        res = ""
        res += "========== Parameter Curva =========\n"
        res += "a: " + str(self.a) + "\n"
        res += "b: " + str(self.b) + "\n"
        res += "n: " + str(self.n) + "\n"
        res += "p: " + str(self.p) + "\n"
        res += "base point (G): " + str(self.G) + "\n"
        res += "private key (d): " + str(self.d) + "\n"
        res += "public key (Q): " + str(self.Q) + "\n"
        res += "====================================\n"
        return res

    def save_file(self, filename:str):
        #filename without extension
        # .priv
        # a b p
        # Gx Gy
        # d

        # .pub
        # a b p
        # Gx Gy
        # Qx Qy

        pri = open(filename + ".pri", "w")
        pri.write(str(self.a) + " " + str(self.b) + " " + str(self.p) + "\n")
        pri.write(str(self.G.x) + " " + str(self.G.y) + "\n")
        pri.write(str(self.d))
        pri.close()
        pub = open(filename + ".pub", "w")
        pub.write(str(self.a) + " " + str(self.b) + " " + str(self.p) + "\n")
        pub.write(str(self.G.x) + " " + str(self.G.y) + "\n")
        pub.write(str(self.Q.x) + " " + str(self.Q.x))
        pub.close()

    def load_key(self, filename:str, is_public:bool):
        f = open(filename, "r")
        line_1 = f.readline().split(" ")
        self.a = int(line_1[0])
        self.b = int(line_1[1])
        self.p = int(line_1[2])
        line_2 = f.readline().split(" ")
        self.G = Point(int(line_2[0]), int(line_2[1]))
        if is_public:
            line_3 = f.readline().split(" ")
            self.Q = Point(int(line_3[0]), int(line_3[1]))
        else:
            self.d = int(f.readline())
        f.close()
