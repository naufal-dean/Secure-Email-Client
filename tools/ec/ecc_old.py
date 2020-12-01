import random

class ECC:
    def __init__(self, a, b, n):
        if (4*a**3 + 27*b**2 == 0):
            print("a dan b salah")
        self.a = a
        self.b = b
        self.n = n # dalam mod
        self.Group = self.generate_grup()
        self.G = self.Group[random.randrange(0, len(self.Group))]
        self.generate_key()

    # tested, hasisl sama dengan di slide dan web
    def generate_grup(self):
        result = []
        for i in range(self.n):
            x = (i**3 + self.a*i + self.b) % self.n
            for j in range(self.n):
                if (j**2 % self.n == x):
                    result.append((i,j))
        return result

    #tested, hasil sama dengan web dan slide
    def add_points(self, P, Q):
        if (P[0] == Q[0]) and (P[1] == Q[1]):
            if (P[1] == 0):
                return (float('inf'), float('inf'))
            else:
                m = ((3*(P[0]**2) + self.a ) * pow(2*P[1], -1, self.n)) % self.n
        else:
            if (P[0] - Q[0]) == 0:
               return (float('inf'), float('inf'))
            else:
                m = ((Q[1] - P[1]) * pow(Q[0]-P[0], -1, self.n)) % self.n
        x = (m**2 - P[0] - Q[0]) % self.n
        y = (m*(P[0] - x) - P[1]) % self.n
        return (x,y)

    # tested, hasil sama degnan web dan slide
    def multiply(self, k, P):
        # print("private key :", k)
        # print("Base point : ", P)
        Q = P
        for i in range(k-1):
            Q = self.add_points(Q, P)
            if (Q == (float('inf'), float('inf'))):
                break
        return Q

    # d private key, Q public key
    def generate_key(self):
        self.d = random.randrange(1, self.n)
        self.Q = self.multiply(self.d, self.G)
        while ((self.Q==(float('inf'), float('inf'))) or (self.Q[0]%self.n == 0)):
            self.d = random.randrange(1, self.n)
            self.Q = self.multiply(self.d, self.G)

    def print_param(self):
        print("====== Parameter Curva =====")
        print("a :", self.a)
        print("b :", self.b)
        print("n :", self.n)
        print("base point (G) :", self.G)
        print("private key(d) :", self.d)
        print("public key(Q) :", self.Q)
        print("============================")

    def signing(self, hash:int):
        k = random.randrange(1, self.n)
        x1, y1 = self.multiply(k, self.G)
        while (((x1,y1)==(float('inf'), float('inf'))) or (x1%self.n == 0)):
            k = random.randrange(1, self.n)
            x1, y1 = self.multiply(k, self.G)

        r = x1 % self.n
        s = (pow(k, -1, self.n) * (hash + self.d * r) ) % self.n
        while (s == 0):
            k = random.randrange(1, self.n)
            x1, y1 = self.multiply(k, self.G)
            while (((x1,y1)==(float('inf'), float('inf'))) or (x1%self.n == 0)):
                k = random.randrange(1, self.n)
                x1, y1 = self.multiply(k, self.G)
            r = x1 % self.n
            s = (pow(k, -1, self.n) * (hash + self.d * r) ) % self.n
        print("output rs :" ,r,s)
        return (r,s)

    def verrifying(self, hash:int, r:int, s:int):
        if ((r < self.n-1) and (r > 1)):
            if ((s < self.n-1) and (s > 1)):
                print("r dan s valid")
        print("input rs :", r,s)
        w = pow(s, -1, self.n)
        u1 = (hash * w) % self.n
        u2 = (r * w) % self.n
        print("u1 :", u1)
        print("u2 :", u2)
        temp1 = self.multiply(u1, self.G)
        temp2 = self.multiply(u2, self.Q)
        print("u1*G :", temp1)
        print("u2*Q :", temp2)
        x1, y1 = self.add_points(temp1, temp2)
        print("hasil penjumlahan :",x1, y1)
        v = x1 % self.n
        print("v :", v)
        print("r :", r)
        return v==r


if __name__ == "__main__":
    ecc = ECC(1,4,23)
    ecc.print_param()
    # print(ecc.multiply(3, (10, 18)))
    x1, x2 = ecc.signing(2000)
    if ecc.verrifying(2000, x1, x2):
        print("Berhasil verifikasi")
    else :
        print("Gagal verifikasi")
