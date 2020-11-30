def lshift_wrap(inp : bytes, n : int):
    inp_num = int.from_bytes(inp, byteorder='big')
    inp_bin = "{0:b}".format(inp_num)
    res_bin = inp_bin[n:] + inp_bin[:n]

    return int(res_bin, 2).to_bytes(len(inp), byteorder='big')

def rshift_wrap(inp : bytes, n : int):
    inp_num = int.from_bytes(inp, byteorder='big')
    inp_bin = "{0:b}".format(inp_num)
    res_bin = inp_bin[len(inp_bin) - n:] + inp_bin[:len(inp_bin) - n]

    return int(res_bin, 2).to_bytes(len(inp), byteorder='big')

def reverse_bit(inp : bytes):
    inp_num = int.from_bytes(inp, byteorder='big')
    inp_bin = "{0:b}".format(inp_num)

    return int(inp_bin[::-1], 2).to_bytes(len(inp), byteorder='big')
    
def xor_b(b1 : bytes, b2 : bytes):
    return bytes([_a ^ _b for _a, _b in zip(b1, b2)])

def and_b(b1 : bytes, b2 : bytes):
    return bytes([_a & _b for _a, _b in zip(b1, b2)])

def append_bytes(b1 : bytes, b2 : bytes):
    b1_num = int.from_bytes(b1, byteorder='big')
    b1_bin = "{0:b}".format(b1_num)
    b2_num = int.from_bytes(b2, byteorder='big')
    b2_bin = "{0:b}".format(b2_num)

    return int(b1_bin + b2_bin, 2).to_bytes(len(b1) + len(b2), byteorder='big')

def msg_split(msg : bytes):
    arr_msg = [msg[i:i+8] for i in range(0, len(msg), 8)]

    if len(arr_msg[-1]) < 8:
        arr_msg[-1] += b'\x00' * (8 - len(arr_msg[-1]))

    return arr_msg

