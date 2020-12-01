import enum

from . import util


SBOX = [
    [b'\x30', b'\x56', b'\x0f', b'\x04', b'\x3b', b'\x40', b'\x12', b'\xb2', b'\x97', b'\x21', b'\xdd', b'\x7f', b'\xda', b'\x20', b'\xd2', b'\x2a'],
    [b'\xd4', b'\xe0', b'\x11', b'\x83', b'\x40', b'\xfa', b'\xc7', b'\x06', b'\x08', b'\x44', b'\x82', b'\x54', b'\x10', b'\xa2', b'\xae', b'\x5f'],
    [b'\x95', b'\xc8', b'\x9e', b'\xb1', b'\x3a', b'\x00', b'\x31', b'\x98', b'\xf5', b'\xbf', b'\x0e', b'\x92', b'\x57', b'\xd5', b'\x04', b'\x94'],
    [b'\x31', b'\xf4', b'\x6c', b'\x21', b'\x96', b'\x76', b'\xa5', b'\xf8', b'\xf6', b'\x35', b'\xf5', b'\x86', b'\x39', b'\x1e', b'\xf9', b'\xf0'],
    [b'\x2f', b'\x7a', b'\x66', b'\xae', b'\x51', b'\x04', b'\x72', b'\x9c', b'\xb1', b'\x6a', b'\xc7', b'\xb0', b'\x52', b'\xcb', b'\x33', b'\x7b'],
    [b'\x00', b'\xc3', b'\x97', b'\x03', b'\x3c', b'\xd6', b'\x16', b'\xcd', b'\xfa', b'\x2e', b'\xe2', b'\xbc', b'\xdd', b'\x91', b'\xc0', b'\x1d'],
    [b'\x15', b'\x3a', b'\x4f', b'\x4a', b'\x17', b'\x19', b'\xe5', b'\x09', b'\x6b', b'\x1b', b'\x3a', b'\x31', b'\xfb', b'\x0e', b'\x37', b'\xc8'],
    [b'\xb0', b'\x29', b'\x2f', b'\x72', b'\x7d', b'\xc3', b'\xba', b'\xf3', b'\x2b', b'\xe2', b'\x61', b'\x0e', b'\x42', b'\x94', b'\x2d', b'\x40'],
    [b'\xe3', b'\xcd', b'\x18', b'\x94', b'\xe8', b'\x13', b'\x1a', b'\x2e', b'\x68', b'\x75', b'\x22', b'\x5c', b'\x44', b'\x9c', b'\x6a', b'\x77'],
    [b'\xa0', b'\xd8', b'\xbe', b'\xf9', b'\x88', b'\xb1', b'\x51', b'\x5a', b'\x69', b'\x44', b'\x65', b'\x7d', b'\x1f', b'\x80', b'\xdf', b'\x25'],
    [b'\x25', b'\x64', b'\xcb', b'\x76', b'\x7c', b'\x2d', b'\x99', b'\x0d', b'\x00', b'\x55', b'\xdf', b'\xe5', b'\xf3', b'\x4e', b'\xd0', b'\xc5'],
    [b'\x74', b'\xdb', b'\x5b', b'\xd7', b'\x60', b'\x79', b'\x0e', b'\xda', b'\x4f', b'\x8d', b'\x9b', b'\xc3', b'\x7c', b'\x58', b'\x8d', b'\x5c'],
    [b'\xce', b'\xe8', b'\xd1', b'\x36', b'\x66', b'\x48', b'\x33', b'\x49', b'\x5f', b'\x7c', b'\x6d', b'\x5a', b'\xaa', b'\x36', b'\x12', b'\xfa'],
    [b'\x35', b'\x16', b'\x9c', b'\x37', b'\x23', b'\x12', b'\xbc', b'\xce', b'\x9b', b'\x34', b'\x12', b'\x09', b'\x11', b'\xab', b'\xbb', b'\xdc'],
    [b'\x48', b'\xe5', b'\xbf', b'\xc0', b'\x66', b'\x47', b'\x57', b'\x8a', b'\xb0', b'\x5c', b'\x7a', b'\xfe', b'\x25', b'\x14', b'\x49', b'\x77'],
    [b'\x07', b'\x67', b'\x2c', b'\x51', b'\xaf', b'\xfa', b'\x7f', b'\x8a', b'\xdd', b'\x0c', b'\xcc', b'\x1e', b'\xcd', b'\x66', b'\x33', b'\xff']
]

class Mode(enum.Enum):
    ECB = 1
    CBC = 2
    CTR = 3

class STRAIT:
    def __init__(self, key : str, mode : Mode):
        assert len(key) == 32

        self.mode = mode
        self.key = bytes(key, 'UTF-8')

        self.cur_round_key = None
        self.factor1 = None
        self.factor2 = None
        self.factor3 = None

        self.generate_feistel_iter()

    def init_message_buffers(self, msg):
        # Init message
        if isinstance(msg, str):
            self.msg = bytes(msg, 'UTF-8')
        else:
            self.msg = msg

        self.msg_parts = util.msg_split(self.msg)

    def generate_feistel_iter(self):
        xor_half = util.xor_b(self.key[:4], self.key[4:])
        n_mod = int.from_bytes(
            util.lshift_wrap(xor_half, 5), byteorder='big'
        )

        self.feistel_iter = 10 + n_mod % 11

    def encrypt(self, msg, IV : str = None):
        self.init_message_buffers(msg)
        enc = b''

        if self.mode == Mode.ECB:
            for word in self.msg_parts:
                enc += self.feistel_network_enc(word)

        elif self.mode == Mode.CBC:
            assert len(IV) == 8
            prev = bytes(IV, 'UTF-8')
            for word in self.msg_parts:
                enc_word = self.feistel_network_enc(
                    util.xor_b(word, prev)
                )
                enc += enc_word
                prev = enc_word

        elif self.mode == Mode.CTR:
            assert len(IV) == 8
            nonce = int.from_bytes(bytes(IV, 'UTF-8'), byteorder='big')
            cnt = 0
            for word in self.msg_parts:
                enc_nonce = self.feistel_network_enc(
                    int(nonce + cnt).to_bytes(8, byteorder='big')
                )
                enc += util.xor_b(enc_nonce, word)
                cnt += 1

        return enc

    def decrypt(self, msg, IV : str = None):
        self.init_message_buffers(msg)
        dec = b''

        if self.mode == Mode.ECB:
            for word in self.msg_parts:
                dec += self.feistel_network_dec(word)

        elif self.mode == Mode.CBC:
            assert len(IV) == 8
            prev = bytes(IV, 'UTF-8')
            for word in self.msg_parts:
                dec_word = self.feistel_network_dec(word)
                dec += util.xor_b(prev, dec_word)
                prev = word

        elif self.mode == Mode.CTR:
            assert len(IV) == 8
            nonce = int.from_bytes(bytes(IV, 'UTF-8'), byteorder='big')
            cnt = 0
            for word in self.msg_parts:
                dec_nonce = self.feistel_network_enc(
                    int(nonce + cnt).to_bytes(8, byteorder='big')
                )
                dec += util.xor_b(dec_nonce, word)
                cnt += 1

        return dec.rstrip(b'\x00')

    def sbox(self, inp : bytes):
        res_byte = b''
        for byte in inp:
            x = byte >> 4
            y = byte & 0xf
            res_byte = SBOX[x][y] + res_byte

        return res_byte

    def generate_factors_from_key(self):
        first_64 = self.cur_round_key[:8]
        second_64 = self.cur_round_key[8:16]
        third_64 = self.cur_round_key[16:24]
        fourth_64 = self.cur_round_key[24:]

        intermed_1 = self.sbox(util.rshift_wrap(first_64, 3))
        intermed_2 = self.sbox(util.lshift_wrap(second_64, 5))
        intermed_3 = util.rshift_wrap(self.sbox(third_64), 7)
        intermed_4 = util.lshift_wrap(self.sbox(fourth_64), 11)

        self.factor1 = util.xor_b(intermed_1, intermed_4)
        self.factor2 = util.xor_b(intermed_2, intermed_3)

    def generate_factor3(self, msg_block : bytes):
        assert len(msg_block) == 4
        # Generating msg_block + pad
        msg_subbed = self.sbox(msg_block)
        pad = util.and_b(
            msg_block,
            util.xor_b(self.factor1[:4], self.factor2[4:])
        )

        msg_s_padded = util.append_bytes(msg_subbed, pad)

        # Generate factor3
        self.factor3 = util.xor_b(
            util.xor_b(
                msg_s_padded,
                self.sbox(self.factor1)
            ),
            self.transpose_fac2()
        )

    def feistel_func(self, msg_part : bytes):
        assert len(msg_part) == 4
        self.generate_factors_from_key()
        self.generate_factor3(msg_part)

        fhalf_fac3 = self.factor3[:4]
        shalf_fac3 = self.factor3[4:]

        return util.reverse_bit(
            util.xor_b(
                fhalf_fac3,
                util.lshift_wrap(shalf_fac3, 5)
            )
        )

    def feistel_network_enc(self, msg_block : bytes):
        assert len(msg_block) == 8
        cur_msg_block = msg_block
        for i in range(self.feistel_iter):
            # Generate round key for current iteration
            self.cur_round_key = util.lshift_wrap(self.key, i % len(self.key))

            inp_lbyte = cur_msg_block[:4]
            inp_rbyte = cur_msg_block[4:]
            out_rbyte = util.xor_b(
                inp_lbyte,
                self.feistel_func(inp_rbyte)
            )
            cur_msg_block = inp_rbyte + out_rbyte

        return cur_msg_block

    def feistel_network_dec(self, msg_block : bytes):
        assert len(msg_block) == 8
        cur_msg_block = msg_block
        for i in range(self.feistel_iter):
            # Generate round key for current iteration
            self.cur_round_key = util.lshift_wrap(self.key, self.feistel_iter - 1 - (i % len(self.key)))

            inp_lbyte = cur_msg_block[:4]
            inp_rbyte = cur_msg_block[4:]
            out_lbyte = util.xor_b(
                inp_rbyte,
                self.feistel_func(inp_lbyte)
            )
            cur_msg_block = out_lbyte + inp_lbyte

        return cur_msg_block

    # NOT IMPLEMENTED YET
    def transpose_fac2(self):
        return self.factor2

if __name__ == '__main__':
    # Check mode
    print(Mode.CBC == Mode.CBC)

    pt = 'huehuehufhuehuequngqangqing'
    key = 'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEF'
    iv = '12345678'

    print(f'key: {key}\niv: {iv}\nmode: {Mode.CBC}\n')

    # Check encryption
    a = STRAIT(key, Mode.CBC)
    cip = a.encrypt(pt, iv)

    # Check decryption
    dc = a.decrypt(cip, iv)

    print(f'Plaintext: {pt}\nEncrypted: {cip}\nDecrypted: {dc}')
