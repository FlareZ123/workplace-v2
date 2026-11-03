"""Single-file original-source PTW/MT sampler-chain discriminator.

Run inside repository with Python 3. No third-party packages. Reads only original
resources and the neighboring, previously published Agent49 symbolic source model.
No selected K04 source coupon is used or accepted-file change performed.
"""
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import source, get, temper, Basis

RESOURCE = ROOT / "resources"
RECEIPTS = RESOURCE / "evidence" / "maintenance" / "seal-receipts.jsonl"
assert hashlib.sha256(RECEIPTS.read_bytes()).hexdigest() == (
    "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
)
PTW = {
    int(r["permit"][-3:]): r
    for line in RECEIPTS.read_text(encoding="utf-8").splitlines()
    if (r := json.loads(line))["permit"].startswith("PTW-")
}
BAY = {"A": 0, "B": 1, "C": 2, "D": 3}
FIXED = {405: -964, 412: -944, 414: -937}
source_basis, mt = source(RESOURCE)
assert source_basis.rank == 15365
cache = {}

def quotient(stage):
    if stage not in cache:
        entries = []
        for symbolic in temper(get(mt, stage)):
            rhs = 0
            remainder = 0
            while symbolic:
                pivot = symbolic.bit_length() - 1
                if pivot in source_basis.rows:
                    vector, value = source_basis.rows[pivot]
                    symbolic ^= vector
                    rhs ^= value
                else:
                    bit = 1 << pivot
                    symbolic ^= bit
                    remainder ^= bit
            entries.append((remainder, rhs))
        cache[stage] = entries
    return cache[stage]

def fixed_mask(stage):
    mask, val = 0, 0
    for bit, vec in enumerate(temper(get(mt, stage))):
        answer = source_basis.predict(vec)
        if answer is not None:
            mask |= 1 << bit
            val |= answer << bit
    return mask, val

PIN = {stage: fixed_mask(stage) for stage in range(-1000, -880)}

def valid_bay(stage, permit):
    mask, value = PIN[stage]
    mask &= 7 << 29
    return ((value ^ (BAY[PTW[permit]["bay"]] << 29)) & mask) == 0

def valid_reject(stage):
    mask, value = PIN[stage]
    return (mask & (1 << 31) == 0) or (value & (1 << 31) != 0)

def valid_serial(stage, permit):
    mask, val = PIN[stage]
    serial = int.from_bytes(bytes.fromhex(PTW[permit]["serial"][3:]), "little")
    return (mask & (val ^ serial)) == 0

def next_stages(permit, last_stage):
    next_permit = permit + 1
    for stage in range(last_stage + 2, last_stage + 11):
        if stage not in PIN or stage - 1 not in PIN:
            continue
        if next_permit in FIXED and stage != FIXED[next_permit]:
            continue
        if (
            valid_serial(stage, next_permit)
            and valid_bay(stage - 1, next_permit)
            and all(valid_reject(k) for k in range(last_stage + 1, stage - 1))
        ):
            yield stage

def paths(start, stop):
    states = {FIXED[start]: [()]}
    for permit in range(start, stop):
        new = defaultdict(list)
        for stage, candidate_paths in states.items():
            for nxt in next_stages(permit, stage):
                for p in candidate_paths:
                    new[nxt].append(p + ((permit + 1, nxt),))
        states = new
    return states.get(FIXED[stop], [])

def joint_rank(path, hidden_before_416=0):
    """Return rank or None if this complete source history contradicts itself."""
    basis = Basis()
    events = ((405, FIXED[405]),) + path
    try:
        for permit, stage in events:
            serial = int.from_bytes(bytes.fromhex(PTW[permit]["serial"][3:]), "little")
            for bit, (remaining, rhs) in enumerate(quotient(stage)):
                basis.insert(remaining, ((serial >> bit) & 1) ^ rhs)
        for (_, prev), (permit, stage) in zip(events, events[1:]):
            first_reject = prev + 1 + (hidden_before_416 if permit == 416 else 0)
            for rejected_stage in range(first_reject, stage - 1):
                remaining, rhs = quotient(rejected_stage)[31]
                basis.insert(remaining, 1 ^ rhs)
            bay = BAY[PTW[permit]["bay"]]
            for bit in range(3):
                remaining, rhs = quotient(stage - 1)[29 + bit]
                basis.insert(remaining, ((bay >> bit) & 1) ^ rhs)
    except AssertionError:
        return None
    return basis.rank

def known_target_bits(path):
    """Individually fixed selected bits. Other target bits remain undetermined."""
    basis = Basis()
    events = ((405, FIXED[405]),) + path
    for permit, stage in events:
        serial = int.from_bytes(bytes.fromhex(PTW[permit]["serial"][3:]), "little")
        for bit, (remaining, rhs) in enumerate(quotient(stage)):
            basis.insert(remaining, ((serial >> bit) & 1) ^ rhs)
    for (_, prev), (permit, stage) in zip(events, events[1:]):
        for rejected_stage in range(prev + 1, stage - 1):
            rem, rhs = quotient(rejected_stage)[31]
            basis.insert(rem, 1 ^ rhs)
        bay = BAY[PTW[permit]["bay"]]
        for bit in range(3):
            rem, rhs = quotient(stage - 1)[29 + bit]
            basis.insert(rem, ((bay >> bit) & 1) ^ rhs)
    return sum(
        basis.predict(remaining) is not None
        for stage in range(951, 955)
        for remaining, _ in quotient(stage)
    )

def cp_sampler_control():
    a = random.Random(26513)
    b = random.Random(26513)
    rejects = 0
    for _ in range(1000):
        expected = a.randrange(4)
        while True:
            draw = b.getrandbits(3)
            if draw < 4:
                break
            rejects += 1
        assert expected == draw
        assert a.getrandbits(32) == b.getrandbits(32)
    assert rejects > 1000
    return rejects

def main():
    rejects = cp_sampler_control()
    assert all(valid_serial(stage, permit) for permit, stage in FIXED.items())
    p1, p2 = paths(405, 412), paths(412, 414)
    assert len(p1) == 125 and len(p2) == 1
    assert p2[0] == ((413, -940), (414, -937))
    viable = [
        (rank, p)
        for a in p1
        for b in p2
        if (rank := joint_rank(p := a + b)) is not None
    ]
    assert len(viable) == 8
    assert all(rank == 220 and known_target_bits(path) == 0 for rank, path in viable)
    strict = [
        (rank, path)
        for _, base in viable
        for t15 in next_stages(414, -937)
        for t16 in next_stages(415, t15)
        if (rank := joint_rank(path := base + ((415, t15), (416, t16)))) is not None
    ]
    assert strict == []
    rescues = []
    for _, base in viable:
        for t15 in next_stages(414, -937):
            for hidden in range(1, 9):
                for additional_rejections in range(9):
                    t16 = t15 + 2 + hidden + additional_rejections
                    if t16 not in PIN or t16 - 1 not in PIN:
                        continue
                    if not (valid_serial(t16, 416) and valid_bay(t16 - 1, 416)):
                        continue
                    if not all(valid_reject(k) for k in range(
                        t15 + 1 + hidden, t16 - 1
                    )):
                        continue
                    path = base + ((415, t15), (416, t16))
                    rank = joint_rank(path, hidden_before_416=hidden)
                    if rank is not None:
                        rescues.append((hidden, additional_rejections, rank, path))
    assert len(rescues) == 96
    assert {k: sum(x[0] == k for x in rescues) for k in range(1, 9)} == {
        1: 0, 2: 0, 3: 24, 4: 40, 5: 24, 6: 8, 7: 0, 8: 0
    }
    print("CPython sampler positive PASS; rejected draws", rejects)
    print("original rank", source_basis.rank, "individual paths", len(p1))
    print("joint 405..414", len(viable), "additional rank", viable[0][0])
    print("selected bits fixed", known_target_bits(viable[0][1]), "/ 128")
    print("original 415..416 strict heldout survivors", len(strict))
    print("single-gap latent-draw rescue", len(rescues))
    print("one illustrative source-consistent rescued path", rescues[0][-1])
    print("K04/K08 NOT RECOVERED")

if __name__ == "__main__":
    main()
