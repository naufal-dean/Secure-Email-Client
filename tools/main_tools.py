import random

from ec import ECC, ECDSA


if __name__ == "__main__":
    ecc = ECC(1, 4, 23)
    ecc.load_key("kunci.pri", False)
    print(ecc)

    # ecdsa = ECDSA(ecc)
    # r, s = ecdsa.sign(2000)

    # if ecdsa.verify(2000, r, s):
    #     print("Berhasil verifikasi")
    # else :
    #     print("Gagal verifikasi")
