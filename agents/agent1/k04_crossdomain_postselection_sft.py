"""H-17 read-only cross-family selected-version transform SFT (4 Nov 2026).
Four source-derived 16-byte before/after pairs; source SHA256 pins in result report.
Tests one-pair trained rotations+XOR and two-pair trained GF128/Z2^128 affine maps.
"""
PAIRS = [
    ("K05 node49 seq200..203 -> seq300..303", "42BFD0538052760C6FC2B743BFB00270", "FF8B78200A56E8586DCDA00EF01E4572"),
    ("K06 withdrawn B -> issued C", "D82A73E9E1DB4379759E0027C130C9BB", "5DBF40EE52FAAED9A536D3326CF0D95A"),
    ("K07 AX-7778 -> AX-7782", "AC5FBCDD1CB5C98CA234AE35DD42B16A", "8947CEDCB9CC73BAB7E87BE63302C5C9"),
    ("Printer 0420 ACK1 -> ACK2", "31C9714DD36DB2677BB9006670A9DFFD", "432475F72A62DB39F3D5693E2C937FA4"),
]
pairs = [(name, bytes.fromhex(x), bytes.fromhex(y)) for name,x,y in PAIRS]
M = (1 << 128) - 1

def mul(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        if a >> 128:
            a ^= (1 << 128) | 0x87
        b >>= 1
    return out

def power(x, exponent):
    result = 1
    while exponent:
        if exponent & 1:
            result = mul(result, x)
        x = mul(x, x)
        exponent >>= 1
    return result

def inv(x):
    assert x
    return power(x, (1 << 128) - 2)

def rotate(raw, kind, shift):
    if kind == "whole":
        n = int.from_bytes(raw, "big")
        return (((n << shift) & M) | (n >> (128-shift) if shift else 0)).to_bytes(16, "big")
    if kind == "word32":
        return b"".join((((n << shift) & 0xffffffff) | (n >> (32-shift) if shift else 0)).to_bytes(4, "big") for n in [int.from_bytes(raw[i:i+4], "big") for i in range(0,16,4)])
    if kind == "bytes-left":
        return raw[shift:] + raw[:shift]
    if kind == "bytes-right":
        return raw[-shift:] + raw[:-shift] if shift else raw
    return bytes(((n << shift) & 255) | (n >> (8-shift) if shift else 0) for n in raw)

def xorb(a,b):
    return bytes(x ^ y for x,y in zip(a,b))

rotation_models = 0
for kind, count in (("whole",128),("word32",32),("bytes-left",16),("bytes-right",16),("byte-bits",8)):
    for shift in range(count):
        pad = xorb(rotate(pairs[0][1],kind,shift), pairs[0][2])
        assert xorb(rotate(pairs[0][1],kind,shift),pad) == pairs[0][2]
        assert all(xorb(rotate(x,kind,shift),pad) != y for _,x,y in pairs[1:]), (kind,shift)
        rotation_models += 1
assert rotation_models == 200

gf_models = 0
ring_models = 0
for input_view in ("big","little"):
    for output_view in ("big","little"):
        decoded = [(int.from_bytes(x,input_view),int.from_bytes(y,output_view)) for _,x,y in pairs]
        (u0,v0),(u1,v1) = decoded[:2]
        a = mul(v0 ^ v1, inv(u0 ^ u1))
        b = v0 ^ mul(a,u0)
        assert all(mul(a,u) ^ b == v for u,v in decoded[:2])
        assert all(mul(a,u) ^ b != v for u,v in decoded[2:])
        gf_models += 1

        du = (u1 - u0) & M
        dv = (v1 - v0) & M
        k = (du & -du).bit_length() - 1
        assert not dv % (1 << k)
        modulus = 1 << (128-k)
        base_a = ((dv >> k) * pow(du >> k, -1, modulus)) % modulus
        for branch in range(1 << k):
            slope = base_a + branch * modulus
            offset = (v0 - slope*u0) & M
            assert all((slope*u+offset)&M == v for u,v in decoded[:2])
            assert all((slope*u+offset)&M != v for u,v in decoded[2:])
            ring_models += 1

# True source generator controls: four serializer layouts, recovered coefficients.
seed_a, seed_b = 0x713f2d64dc3e51aaf4128400ed13a867, 0x8f250aa4669931b1c5a7738e21537d04
for input_view in ("big","little"):
    for output_view in ("big","little"):
        u0 = int.from_bytes(pairs[0][1],input_view)
        u1 = int.from_bytes(pairs[1][1],input_view)
        v0,v1 = (mul(seed_a,u)^seed_b for u in (u0,u1))
        recovered_a = mul(v0^v1,inv(u0^u1))
        recovered_b = v0^mul(recovered_a,u0)
        assert (recovered_a,recovered_b) == (seed_a,seed_b)
        assert (mul(recovered_a,int.from_bytes(pairs[2][1],input_view))^recovered_b).to_bytes(16,output_view) == (mul(seed_a,int.from_bytes(pairs[2][1],input_view))^seed_b).to_bytes(16,output_view)

print("PASS source-derived pairs=4; 200 rotation/XOR, 4 GF128 affine, 6 Z2^128 affine complete-fitted models")
print("PASS original heldout selected K07=0; original 0420 ACK2=0; 4 planted GF128 positives")
