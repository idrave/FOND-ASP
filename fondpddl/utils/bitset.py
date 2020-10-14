from __future__ import annotations
from typing import Union
class BitMask:
    def __init__(self, bits=bytearray()):
        self.bits = bits
        self.length = len(bits) * 8

    def __len__(self):
        return self.length
    
    def __getitem__(self, index):
        if index < 0:
            raise ValueError('BitSet: index must be positive')
        if index >= self.length:
            return False
        mask = 1 << (index % 8)
        return bool(self.bits[index // 8] & mask)

    def __iter__(self):
        self.iter = -1
        return self

    def __next__(self):
        self.iter += 1
        if self.iter < len(self):
            return self[self.iter]
        raise StopIteration

    def __repr__(self):
        return "<{}>".format(", ".join("{:d}".format(value) for value in self))


class BitSet(BitMask):
    def __init__(self, length=0):
        if length < 0:
            raise ValueError('BitSet: length must be positive')
        self.bits = bytearray(b"\x00" * ((length + 7) // 8))
        self.length = length

    @classmethod
    def from_bitmask(cls, bitmask: BitMask) -> BitSet:
        bs = cls(length=len(bitmask))
        bs.bits = bitmask.bits
        return bs

    def resize(self, length):
        if length < 0:
            raise ValueError('BitSet: length must be positive')
        if length > self.length:
            self.bits.extend(bytearray(b"\x00" * ((length + 7) // 8 - len(self.bits))))
        elif length < self.length:
            del self.bits[(length + 7) // 8 : ]
            if length > 0:
                self.bits[-1] &= 0xff >> (-length % 8)
        self.length = length

    def __setitem__(self, index, value):
        if index < 0:
            raise ValueError('BitSet: index must be positive')
        if index >= self.length:
            self.resize(index + 1)
        value = int(bool(value)) << (index % 8)
        mask = 0xff ^ (1 << (index % 8))
        self.bits[index // 8] &= mask
        self.bits[index // 8] |= value


class StaticBitSet(BitMask):
    def __init__(self, bits: Union[bytearray, BitMask]):
        if isinstance(bits, BitMask):
            bits = bits.bits
        n_bytes = len(bits)
        last = 0
        for i in range(n_bytes):
            if bits[n_bytes-i-1] != 0:
                last = n_bytes-i
                break
        bits = bits[:last]
        super().__init__(bits)

    def __hash__(self):
        return hash(bytes(self.bits))

    def __eq__(self, other):
        if not isinstance(other, StaticBitSet):
            raise NotImplementedError
        return self.bits == other.bits

