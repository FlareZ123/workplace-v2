"""H17 REC8 arbitrary whole-block binary XOR-parity recovery, source pinned."""
from __future__ import annotations
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
ACCEPT = ROOT / "acceptance.json"
ROUTING = ROOT / "evidence" / "recovery-routing.json"
APIN = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
RPIN = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
KNOWN = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
}
PREHASH = {
    "K02": "E1A5E474BAD7E853A2E8C71D3317D507",
    "K07": "8947CEDCB9CC73BAB7E87BE63302C5C9",
}

def xor_blocks(values: list[bytes]) -> bytes:
    number = 0
    for value in values:
        number ^= int.from_bytes(value, "big")
    return number.to_bytes(16, "big")

def linear_subset(blocks: list[bytes], mask: int) -> bytes:
    return xor_blocks([blocks[i] for i in range(6) if (mask >> i) & 1])

def main() -> None:
    assert hashlib.sha256(ACCEPT.read_bytes()).hexdigest() == APIN
    assert hashlib.sha256(ROUTING.read_bytes()).hexdigest() == RPIN
    commitments = json.loads(ACCEPT.read_text())["slot_sha256"]
    mask = bytes.fromhex(json.loads(ROUTING.read_text())["K04"]["masked_component"])
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    keys = list(KNOWN)
    for key, hexd in KNOWN.items():
        assert hashlib.sha256(bytes.fromhex(hexd)).hexdigest() == commitments[key]

    values = {"K04": set(), "K08": set()}
    assignments = 0
    matches = []
    for raw2, raw7 in itertools.product((False, True), repeat=2):
        blocks = [bytes.fromhex(PREHASH[k] if (k == "K02" and raw2) or
                 (k == "K07" and raw7) else KNOWN[k]) for k in keys]
        for subset in range(64):
            base = linear_subset(blocks, subset)
            for key, component in (("K04", base),
                                   ("K04", xor_blocks([base, mask])),
                                   ("K08", base)):
                assignments += 1
                values[key].add(component)
                if hashlib.sha256(component).hexdigest() == commitments[key]:
                    matches.append((key, raw2, raw7, subset, component.hex().upper()))

    # Synthetic two-equation binary parity positive: A=X xor Y, B=Y.
    # Missing X and Y are different independently planted subset XORs.
    blocks = [bytes([17*i + j for j in range(16)]) for i in range(6)]
    for m1, m2 in ((0, 63), (13, 37), (27, 14), (61, 1), (4, 29)):
        actual_x = linear_subset(blocks, m1)
        actual_y = linear_subset(blocks, m2)
        check_a = xor_blocks([actual_x, actual_y])
        check_b = actual_y
        recovered_y = check_b
        recovered_x = xor_blocks([check_a, recovered_y])
        assert actual_x == recovered_x and actual_y == recovered_y
        assert recovered_x in [linear_subset(blocks, mask) for mask in range(64)]
        physical = xor_blocks([recovered_x, mask])
        assert xor_blocks([physical, mask]) == actual_x
        assert hashlib.sha256(recovered_x).digest() == hashlib.sha256(actual_x).digest()
    assert not matches

    print(json.dumps({
        "original_accepted_known": 6,
        "views": 4,
        "subset_count_per_view": 64,
        "complete_component_assignments": assignments,
        "distinct_k04": len(values["K04"]),
        "distinct_k08": len(values["K08"]),
        "original_hits": matches,
        "synthetic_pair_and_mask_controls": 5,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
