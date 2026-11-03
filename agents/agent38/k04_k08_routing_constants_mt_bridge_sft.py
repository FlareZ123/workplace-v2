"""Search whether original routing mask/desk nonce are consecutive MT packets.

Uses Agent2's original, source-pinned, selected-ACK-withheld p951 closure.
This is a deliberately CONDITIONAL shared-producer model. It tests 2501
possible four-native-word positions (-1000..1500 inclusive), both byte
orders and both global word orders; no K04/K08 acceptance check.
Reproduction: python agents/agent38/k04_k08_routing_constants_mt_bridge_sft.py
"""
import json
from pathlib import Path
import runpy


def main():
    repo = Path(__file__).resolve().parents[2]
    core = runpy.run_path(str(repo / "agents/agent2/20261102_k04_multicarrier_p951_sft.py"))
    state, known, state_offset = core["source_closure"](repo / "resources")
    untemper = core["untemper"]
    full_mask = 0xFFFFFFFF

    # An original source packet is reconstructible at p951 start index zero.
    spool = (repo / "resources/evidence/print/spool-reconstruction.log").read_text()
    first = next(line for line in spool.splitlines() if "PAYLOAD=" in line)
    original = bytes.fromhex(first.split("PAYLOAD=")[1].split()[0])
    for lane in range(4):
        at = state_offset + lane
        assert known[at] == full_mask
        assert core["temper"](state[at]) == int.from_bytes(
            original[4 * lane:4 * lane + 4], "little")
    assert all(known[state_offset + 951 + lane] == 0 for lane in range(4))
    print("original source positive and target-exclusion controls PASS")

    route = json.loads((repo / "resources/evidence/recovery-routing.json").read_text())
    subjects = {
        "K04 route masked_component": bytes.fromhex(route["K04"]["masked_component"]),
        "K08 desk_nonce": bytes.fromhex(route["K08"]["desk_nonce"]),
    }
    for label, packet in subjects.items():
        matches, candidates = [], []
        for endian in ("little", "big"):
            for reverse in (False, True):
                native = [untemper(int.from_bytes(packet[4*i:4*i+4], endian))
                          for i in range(4)]
                if reverse:
                    native.reverse()
                for start in range(-1000, 1501):
                    positions = range(state_offset + start, state_offset + start + 4)
                    fixed = sum(known[i].bit_count() for i in positions)
                    if fixed < 64:
                        continue
                    conflicts = sum(
                        ((state[i] ^ value) & known[i]).bit_count()
                        for i, value in zip(positions, native))
                    candidates.append((conflicts, fixed, endian, reverse, start))
                    if conflicts == 0:
                        matches.append((endian, reverse, start, fixed))
        print(label, "packet placements with >=64 fixed bits and no conflict:",
              matches)
        print("best 5 observed conflicting placements:", sorted(candidates)[:5])
        assert not matches
    print("No direct routing-constant shared-MT packet bridge at this threshold.")


if __name__ == "__main__":
    main()
