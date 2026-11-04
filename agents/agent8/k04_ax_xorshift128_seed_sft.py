"""H-17 AX checkpoint -> xorshift128 state -> speculative K04 coupon bridge.
Original resources are read only. Python standard library, single-file test.
"""
from hashlib import sha256
from itertools import combinations, product
from json import loads
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
AUDIT = ROOT / "evidence/transfers/transfer-audit.jsonl"
ROUTE = ROOT / "evidence/recovery-routing.json"
ACCEPT = ROOT / "acceptance.json"
assert sha256(AUDIT.read_bytes()).hexdigest() == "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
assert sha256(ROUTE.read_bytes()).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
assert sha256(ACCEPT.read_bytes()).hexdigest() == "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
checks = {(r["transfer"], r["seq"], r["attempt"]): int(r["checkpoint"], 16)
          for line in AUDIT.read_text().splitlines() if (r := loads(line))["kind"] == "CHUNK"}
transfers = sorted(set(t for t, _, _ in checks))
assert len(transfers) == 4 and all((t, s, a) in checks for t in transfers for s in range(8) for a in (1, 2))
mask = bytes.fromhex(loads(ROUTE.read_text())["K04"]["masked_component"])
target = loads(ACCEPT.read_text())["slot_sha256"]["K04"]
MOD = 0xFFFFFFFF


def step(state):
    x, y, z, w = state
    t = (x ^ ((x << 11) & MOD)) & MOD
    return (y, z, w, (w ^ (w >> 19) ^ t ^ (t >> 8)) & MOD)


def previous(state):
    x1, y1, z1, w1 = state
    q = w1 ^ z1 ^ (z1 >> 19)
    t = (q ^ (q >> 8) ^ (q >> 16) ^ (q >> 24)) & MOD
    x = (t ^ ((t << 11) & MOD) ^ ((t << 22) & MOD)) & MOD
    out = (x, x1, y1, z1)
    assert step(out) == state
    return out


def split(number):
    return tuple((number >> (32 * i)) & MOD for i in range(4))


def join(words):
    return sum(w << (32 * i) for i, w in enumerate(words))


def outputs(state, count, selector):
    words = split(state)
    result = []
    for _ in range(count):
        words = step(words)
        value = 0
        for i, w in enumerate(words):
            if selector & (1 << (2 * i)):
                value ^= w & 0xFFFF
            if selector & (1 << (2 * i + 1)):
                value ^= w >> 16
        result.append(value)
    return result


def equations(selector, count):
    rows = [0] * (count * 16)
    for bit in range(128):
        for i, word in enumerate(outputs(1 << bit, count, selector)):
            for j in range(16):
                if (word >> j) & 1:
                    rows[i * 16 + j] |= 1 << bit
    return rows


def solve(rows, observed, enumerate_states=False):
    augmented = [row | (((observed[i // 16] >> (i % 16)) & 1) << 128)
                 for i, row in enumerate(rows)]
    pivots = []
    rank = 0
    for bit in range(128):
        k = next((i for i in range(rank, len(rows)) if (augmented[i] >> bit) & 1), None)
        if k is None:
            continue
        augmented[rank], augmented[k] = augmented[k], augmented[rank]
        for i in range(len(augmented)):
            if i != rank and ((augmented[i] >> bit) & 1):
                augmented[i] ^= augmented[rank]
        pivots.append(bit)
        rank += 1
        if rank == len(rows):
            break
    if any((a >> 128) & 1 for a in augmented[rank:]):
        return rank, False, []
    if not enumerate_states:
        return rank, True, []
    free = [i for i in range(128) if i not in pivots]
    assert len(free) <= 12
    base = sum(((augmented[i] >> 128) & 1) << bit for i, bit in enumerate(pivots))
    basis = [(1 << f) ^ sum(1 << bit for i, bit in enumerate(pivots)
                             if (augmented[i] >> f) & 1) for f in free]
    states = [base ^ sum(x for b, x in zip(flags, basis) if b)
              for flags in product((0, 1), repeat=len(free))]
    return rank, True, states


def components(state):
    words = split(state)
    for order in ((0, 1, 2, 3), (3, 2, 1, 0), (1, 0, 3, 2), (2, 3, 0, 1)):
        for endian in ("big", "little"):
            raw = b"".join(words[i].to_bytes(4, endian) for i in order)
            yield raw
            yield bytes(a ^ b for a, b in zip(raw, mask))


selectors = {}
for word in range(4):
    selectors[f"w{word}_low"] = 1 << (word * 2)
    selectors[f"w{word}_high"] = 1 << (word * 2 + 1)
    selectors[f"w{word}_xor_halves"] = 3 << (word * 2)
for a, b in combinations(range(4), 2):
    for half in range(2):
        selectors[f"w{a}_xor_w{b}_{half}"] = (1 << (2 * a + half)) | (1 << (2 * b + half))
for half in range(2):
    selectors[f"all_w_{half}"] = sum(1 << (2 * word + half) for word in range(4))
assert len(selectors) == 26

# Planted source-compatible coupon three inverse draws upstream of AX-7782 attempt 1.
seed_selector = selectors["w0_xor_halves"]
seed_observed = [checks["AX-7782", i, 1] for i in range(8)]
rank, ok, available = solve(equations(seed_selector, 8), seed_observed, True)
assert rank == 127 and ok and len(available) == 2
planted_state = available[0]
for _ in range(3):
    planted_state = join(previous(split(planted_state)))
planted_coupon = list(components(planted_state))[6]
planted_hash = sha256(planted_coupon).hexdigest()

models = source_pass = selected_states = candidates = original_hits = planted_hits = 0
for name, selector in selectors.items():
    eq8 = equations(selector, 8)
    eq16 = equations(selector, 16)
    for transfer in transfers:
        for attempt_major in (False, True):
            for reverse in (False, True):
                indices = ([(s, a) for a in (1, 2) for s in range(8)] if attempt_major
                           else [(s, a) for s in range(8) for a in (1, 2)])
                if reverse:
                    indices.reverse()
                observed = [checks[transfer, s, a] for s, a in indices]
                models += 1
                _, compatible, _ = solve(eq16, observed)
                source_pass += compatible
                if compatible:
                    print("GENUINE_16_CHECKPOINT_SOURCE_MATCH", name, transfer, attempt_major, reverse)
    for attempt in (1, 2):
        for reverse in (False, True):
            seqs = range(7, -1, -1) if reverse else range(8)
            observed = [checks["AX-7782", s, attempt] for s in seqs]
            rank, compatible, states = solve(eq8, observed, True)
            if not compatible:
                continue
            selected_states += len(states)
            print("SELECTED_8_CHECKPOINT_FIT", name, attempt, reverse, "rank", rank, "states", len(states))
            for state in states:
                for backward in (False, True):
                    trial_state = state
                    for offset in range(33):
                        for candidate in components(trial_state):
                            candidates += 1
                            digest = sha256(candidate).hexdigest()
                            original_hits += digest == target
                            planted_hits += digest == planted_hash
                            if digest == target:
                                print("ORIGINAL_K04_HIT", name, attempt, reverse, backward, offset, candidate.hex().upper())
                        trial_state = join(previous(split(trial_state))) if backward else join(step(split(trial_state)))
    test_state = 0x7ABCDAF012345678ABCDEFA987654321
    assert solve(eq16, outputs(test_state, 16, selector))[1], name

print("FINAL", {"readout_families": len(selectors), "complete_source_models": models,
                "original_source_16word_pass": source_pass,
                "source_selected_8word_seed_states": selected_states,
                "complete_original_K04_candidates": candidates,
                "original_K04_matches": original_hits,
                "planted_source_compatible_target_matches": planted_hits,
                "planted_generator_positive_models": len(selectors)})
assert models == 416 and source_pass == 0 and selected_states == 24
assert candidates == 25344 and original_hits == 0 and planted_hits >= 1
