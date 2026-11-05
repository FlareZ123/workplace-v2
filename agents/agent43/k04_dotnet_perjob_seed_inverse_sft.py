"""Source-conditioned inversion of the .NET Framework Random(int).NextBytes issuer.
Requires NumPy. Never uses selected printer row129 for fitting.
Run from repository root: python agents/agent43/k04_dotnet_perjob_seed_inverse_sft.py
"""
from pathlib import Path
import hashlib
import re
import numpy as np

MOD = (1 << 31) - 1
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def sample(seed, count=16):
    """Exact historical .NET seeded subtractive raw 31-bit samples."""
    mj = 161803398 - abs(seed)
    state = [0] * 56
    state[55] = mj
    mk = 1
    for i in range(1, 55):
        j = (21 * i) % 55
        state[j] = mk
        mk = mj - mk
        if mk < 0:
            mk += MOD
        mj = state[j]
    for _ in range(4):
        for i in range(1, 56):
            state[i] -= state[1 + (i + 30) % 55]
            if state[i] < 0:
                state[i] += MOD
    a, b = 0, 21
    outputs = []
    for _ in range(count):
        a = 1 if a + 1 == 56 else a + 1
        b = 1 if b + 1 == 56 else b + 1
        value = state[a] - state[b]
        if value == MOD:
            value -= 1
        if value < 0:
            value += MOD
        state[a] = value
        outputs.append(value)
    return outputs


BASE = sample(0, 32)
COEFF = [(s - b) % MOD for s, b in zip(sample(1, 32), BASE)]
INVERSE = pow(COEFF[0], -1, MOD)


def inverse_first_four(packet):
    """Enumerate ~2^23 candidate raw sample0 values; invert modulo 2^31-1."""
    first = packet[0]
    upper = (MOD - 1 - first) // 256 + 1
    matches = []
    for start in range(0, upper, 1_000_000):
        count = min(1_000_000, upper - start)
        y = np.arange(start, start + count, dtype=np.int64) * 256 + first
        seeds = ((y - BASE[0]) * INVERSE) % MOD
        good = np.ones(count, dtype=bool)
        for j in range(1, 4):
            good &= (((seeds * COEFF[j] + BASE[j]) % MOD) & 255) == packet[j]
            if not good.any():
                break
        matches.extend(int(v) for v in seeds[good] if v <= 1_800_000_000)
    return matches


def main():
    for seed in (0, 1, 42, 20261003, 123456789, 1800000000):
        assert all((COEFF[i] * seed + BASE[i]) % MOD == x
                   for i, x in enumerate(sample(seed, 32)))
        data = bytes(v & 255 for v in sample(seed))
        found = inverse_first_four(data)
        assert seed in found, (seed, found)
        print(f"positive seed={seed} four-byte candidates={len(found)}: PASS")

    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    rows = [bytes.fromhex(m.group(1)) for line in raw.decode().splitlines()
            if (m := re.search(r"PAYLOAD=([0-9A-F]{32})", line))]
    assert len(rows) == 133
    for i in (0, 8, 64, 127, 128, 130, 131, 132):
        seeds = inverse_first_four(rows[i])
        complete = [s for s in seeds
                    if bytes(x & 255 for x in sample(s)) == rows[i]]
        print(f"source row={i} four-byte candidates={len(seeds)} "
              f"exact-sixteen-byte fits={complete}")
        assert complete == []
    print("NO_MATCH for 8 intact printer packets in affine-valid seed domain "
          "[0,1800000000]; selected row129 never inspected.")


if __name__ == "__main__":
    main()
