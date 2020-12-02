import re
from hashlib import md5
from tools.ec import ECC, ECDSA, Point
from tools.keccak import Sha3

def get_text_plain(message):
    text = ''
    for part in message.bodystructure.serial_message():
        if part.is_text() and part.is_plain():
            text += message.part(part)
            break
    return text


def check_digital_signature(text, a, b, p, Qx, Qy, n, Gx, Gy):
    match = re.findall(r'^(.*)\n\n<ds>(.*)</ds>$', text, re.DOTALL)
    if len(match) == 0:
        return False
    message, ds = match[0]
    print(message)
    print(ds)
    r, s = ds.split(',')
    r = int(r)
    s = int(s)
    curva = ECC(a, b, p, n, Point(Gx, Gy))
    curva.set_Q(Point(Qx, Qy))
    ecdsa = ECDSA(curva)
    return ecdsa.verify(Sha3().get_int_digest(message), r, s )

def generate_digital_signature(text, a, b, p, d, n, Gx, Gy):
    hash_int = Sha3().get_int_digest(text.decode('utf-8'))
    curve = ECC(a,b,p,n,Point(Gx, Gy))
    curve.set_d(d)
    ecdsa = ECDSA(curve)
    r, s = ecdsa.sign(hash_int)
    return bytes( (str(r) + "," + str(s)), 'utf-8')
