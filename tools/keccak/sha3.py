from binascii import hexlify, unhexlify 
import numpy as np
 
 
RHO = [
     1,  3,  6, 10, 15, 21,
    28, 36, 45, 55,  2, 14,
    27, 41, 56,  8, 25, 43,
    62, 18, 39, 61, 20, 44]
PI = [
    10,  7, 11, 17, 18, 3,
     5, 16,  8, 21, 24, 4,
    15, 23, 19, 13, 12, 2,
    20, 14, 22,  9,  6, 1]
ROUND_CONSTANTS = np.array([
    0x0000000000000001, 0x0000000000008082,
    0x800000000000808a, 0x8000000080008000,
    0x000000000000808b, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009,
    0x000000000000008a, 0x0000000000000088,
    0x0000000080008009, 0x000000008000000a,
    0x000000008000808b, 0x800000000000008b,
    0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080,
    0x000000000000800a, 0x800000008000000a,
    0x8000000080008081, 0x8000000000008080,
    0x0000000080000001, 0x8000000080008008],
    dtype=np.uint64)
 
def rotate_left(x, s):
    return ((np.uint64(x) << np.uint64(s)) ^ (np.uint64(x) >> np.uint64(64 - s)))
 
 
class Sha3:
    # menggunakan standar fips202
    def __init__(self):
        # sha3 rate = 200-( 512 // 8)
        self.rate = 136
        # sha3 pad
        self.pad_byte = 0x06
        # offset state
        self.cnt = 0
        self.state = np.zeros(25, dtype=np.uint64)
        self.buffer = np.zeros(200, dtype=np.uint8)
    
    def absorb(self, b):
        length = len(b)
        i = 0
        while length > 0:
            diff = self.rate - self.cnt
            to_be_absorbed = min(diff, length)
            # untuk setiap blok berukuran rate, di-xor
            self.buffer[self.cnt:self.cnt + to_be_absorbed] ^= np.frombuffer(b[i:i+to_be_absorbed], dtype=np.uint8)
            self.cnt += to_be_absorbed
            # menangani kalau sudah habis statenya
            if self.cnt == self.rate:
                self.permute()
            length -= to_be_absorbed
            i += to_be_absorbed
    
    def squeeze(self, n):
        # inisialisasi z kosong
        z = b''
        while n > 0:
            diff = self.rate - self.cnt
            to_be_squeezed = min(diff, n)
            # append z dengan r bit pertama dari state
            z += self.state.view(dtype=np.uint8)[self.cnt:self.cnt + to_be_squeezed].tobytes()
            self.cnt += to_be_squeezed
            # menangani kalau sudah habis statenya
            if self.cnt == self.rate:
                self.permute()
            n -= to_be_squeezed
        return z
    
    def pad(self):
        self.buffer[self.cnt] ^= self.pad_byte
        self.buffer[self.rate - 1] ^= 0x80
        self.permute()
    
    def permute(self):
        # f-1600
        self.state ^= self.buffer.view(dtype=np.uint64)
        for i in range(len(self.state)-1):
            temp = np.zeros(5, dtype=np.uint64)
            # Parity
            for j in range(5):
                temp[j] = 0
                for k in range(0, 25, 5):
                    temp[j] ^= self.state[j + k]
            # Theta
            for j in range(5):
                t = rotate_left(temp[(j + 1) % 5], 1) ^ temp[(j + 4) % 5]
                for k in range(0, 25, 5):
                    self.state[k + j] ^= t
            # Rho dan pi
            t = self.state[1]
            for j in range(24):
                temp[0] = self.state[PI[j]]
                self.state[PI[j]] = rotate_left(t, RHO[j])
                t = temp[0]
            for j in range(0, 25, 5):
                for k in range(5):
                    temp[k] = self.state[j + k]
                for k in range(5):
                    self.state[j + k] = (temp[(k + 2) % 5] & (~temp[(k + 1) % 5])) ^ temp[k]
            self.state[0] ^= ROUND_CONSTANTS[i]
        # kembali ke 0 buat offset state pada absorb dan squeeze
        self.cnt = 0
        # 0 kan semua
        self.buffer[:] = 0
 
    def get_hex_digest(self, b):
        # returns hex
        bytes_input = bytes(b.lower(), 'utf-8')
        self.absorb(unhexlify(hexlify(bytes_input)))
        self.pad()
        ret = self.squeeze((200 - self.rate) // 2)
        return hexlify(ret)
    
    def get_int_digest(self, b):
        # returns integer
        hex_digest = self.get_hex_digest(b)
        return int(hex_digest, 16)



if __name__ == '__main__':
    Sha3_256 = Sha3()
    
    msg = "memez is luv"
    digest = "6b71180fa829da6775e6b00193ad033593156eb0e34c0ffbd43103615025ccf6"
    d = bytes(digest.lower(), 'utf-8')
    h = Sha3_256.get_hex_digest(msg)
    i = Sha3_256.get_int_digest(msg)
    print(i)
    if h != d:
        print("salah")
        print(h, digest.lower())
    else:
        print("benar")
        print(h, d)
        print(i)
