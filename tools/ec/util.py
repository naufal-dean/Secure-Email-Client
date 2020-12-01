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
