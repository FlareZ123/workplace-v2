"""SFT: Lehmer64 exact 128bit state inverse and H-17 K04 two-request flanks."""
from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2] / 'resources'
SPOOL = ROOT / 'evidence/print/spool-reconstruction.log'
PIN = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
A = 0xDA942042E4DD58B5
B = 1 << 64
MOD = 1 << 128
LIMIT = 1_000_000


def next_state(state):
    return state * A % MOD


def invert(first, second):
    quotient = (second - A * first) % B
    if quotient >= A:
        return []
    lo = (quotient * B + A - 1) // A
    hi = ((quotient + 1) * B - 1) // A
    return [first * B + tail for tail in range(lo, min(hi, B - 1) + 1)
            if next_state(first * B + tail) >> 64 == second]


def pack(a, b, endian, swap):
    parts = [a, b]
    if swap:
        parts.reverse()
    return b''.join(v.to_bytes(8, endian) for v in parts)


def unpack(packet, endian, swap):
    parts = [int.from_bytes(packet[i:i+8], endian) for i in (0, 8)]
    if swap:
        parts.reverse()
    return parts


def find(before, after, endian, swap, last):
    first, second = unpack(before, endian, swap)
    later, later2 = unpack(after, endian, swap)
    states = invert(first, second)
    matches = []
    for state in states:
        current = state
        for offset in range(last + 1):
            if offset >= 4 and current >> 64 == later:
                if next_state(current) >> 64 == later2:
                    matches.append((offset, state))
            current = next_state(current)
    return states, matches


def source():
    raw = SPOOL.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    selected = {}
    for line in raw.decode().splitlines():
        if 'JOB=PS-261003-0417 ' not in line or 'CLASS=RECOVER' not in line:
            continue
        m = re.search(r'ATTEMPT=(\d+) STATE=(\w+)', line)
        assert m is not None
        number, status = int(m.group(1)), m.group(2)
        if number == 2:
            assert status == 'ACK'
            continue  # Explicitly withhold the untrusted selected payload.
        assert number in (1, 3) and status == 'REQUESTED'
        field = re.search(r'PAYLOAD=([0-9A-F]{32})', line)
        assert field is not None
        selected[number] = bytes.fromhex(field.group(1))
    assert set(selected) == {1, 3}
    return selected[1], selected[3]


def controls():
    count = 0
    for initial in (0x2F7BCADD009845FB4D023DA1AA74B6F3,
                    0x92C4A1146FEE2B40000279FA1179C812,
                    0x123456789ABCDEF00123456789ABCDEF):
        for gap in (4, 17, 256, 4096):
            target_state = initial * pow(A, gap, MOD) % MOD
            for endian in ('little', 'big'):
                for swap in (False, True):
                    before = pack(initial >> 64, next_state(initial) >> 64, endian, swap)
                    after = pack(target_state >> 64, next_state(target_state) >> 64, endian, swap)
                    states, found = find(before, after, endian, swap, gap)
                    assert initial in states and (gap, initial) in found
                    count += 1
    assert count == 48
    return count


def main():
    print('SYNTHETIC full 128bit state / later packet reconstruction', controls(), 'PASS')
    before, after = source()
    total = 0
    matches = []
    for endian in ('little', 'big'):
        for swap in (False, True):
            states, found = find(before, after, endian, swap, LIMIT)
            total += len(states)
            matches.extend((endian, swap, gap) for gap, _ in found)
            print('ORIGINAL view', endian, 'swap', swap, 'candidate states', len(states),
                  'later full packet matches', len(found))
    print('ORIGINAL first-flank-compatible 128bit states', total)
    print('ORIGINAL full later-flank matches within 1m output positions', len(matches))
    assert total == 5 and not matches
    print('K04 result: no complete coupon candidate in bounded Lehmer64 producer model')


if __name__ == '__main__':
    main()
