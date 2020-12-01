import random

from ec import ECC, ECDSA, Point


if __name__ == "__main__":
    # n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    # x = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    # y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    # G = Point(x, y)
    # ecc = ECC(0, 7, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F, n=n, G=G)

    ecc = ECC.load_key("test_keys/kunci.pub", True)
    print(ecc)

    ecc = ECC.load_key("test_keys/kunci.pri", False)
    print(ecc)

    ecc = ECC.load_key("test_keys/kunci_no_n.pub", True)
    print(ecc)

    ecc = ECC.load_key("test_keys/kunci_no_n.pri", False)
    print(ecc)

    ecc = ECC(1, 4, 23)
    print(ecc)

    ecdsa = ECDSA(ecc)
    r, s = ecdsa.sign(12391023112093805123092410293810251203810238120938401293)

    if ecdsa.verify(12391023112093805123092410293810251203810238120938401293, r, s):
        print("Berhasil verifikasi")
    else :
        print("Gagal verifikasi")
