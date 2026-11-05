"""K04 source-collision AES wrapper reconstruction. Historical evidence is read-only.

Supply H17_RESOURCE_ROOT to point at the extracted original archive root.
"""
import hashlib
import itertools
import json
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
EXPECTED = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def layout(value: bytes, variant: int) -> bytes:
    if variant == 0:
        return value
    if variant == 1:
        return value[::-1]
    if variant == 2:
        return b"".join(value[i:i + 4] for i in (12, 8, 4, 0))
    return b"".join(value[i:i + 4][::-1] for i in (0, 4, 8, 12))


def aes(key: bytes, block: bytes, direction: str) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    ctx = cipher.encryptor() if direction == "E" else cipher.decryptor()
    return ctx.update(block) + ctx.finalize()


def xor(x: bytes, y: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(x, y))


def main() -> None:
    raw = SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    rows = []
    for line in raw.decode("ascii").splitlines():
        if line and not line.startswith("#"):
            rows.append(dict(field.split("=", 1) for field in line.split()[1:]))

    def source(job: str, attempt: str, klass: str, state: str) -> bytes:
        matches = [r for r in rows if r["JOB"] == job and r["ATTEMPT"] == attempt
                   and r["CLASS"] == klass and r["STATE"] == state]
        assert len(matches) == 1
        return bytes.fromhex(matches[0]["PAYLOAD"])

    job = "PS-261003-0417"
    sources = (source(job, "1", "LABEL", "ACK"),
               source(job, "1", "RECOVER", "REQUESTED"),
               source(job, "2", "RECOVER", "ACK"))
    assert len([r for r in rows if r["JOB"] == job and r["ATTEMPT"] == "1"]) == 2
    assert len([r for r in rows if r["JOB"] == "PS-261003-0420" and r["ATTEMPT"] == "2"]) == 1
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    commitment = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"]

    planted = hashlib.sha256(xor(aes(sources[0], aes(sources[1], sources[2], "D"), "E"), mask)).hexdigest()
    tests = 0
    positive = 0
    unique = set()
    authentic = []
    for perm in itertools.permutations(range(3)):
        for orientations in itertools.product(range(4), repeat=3):
            k_old, k_new, block = (layout(sources[perm[i]], orientations[i]) for i in range(3))
            for first in ("E", "D"):
                intermediate = aes(k_old, block, first)
                for second in ("E", "D", "-"):
                    output = intermediate if second == "-" else aes(k_new, intermediate, second)
                    for whitening in range(4):
                        candidate = output
                        if whitening & 1:
                            candidate = xor(candidate, k_old)
                        if whitening & 2:
                            candidate = xor(candidate, k_new)
                        for destination_layout in range(4):
                            component = xor(layout(candidate, destination_layout), mask)
                            digest = hashlib.sha256(component).hexdigest()
                            unique.add(component)
                            tests += 1
                            positive += digest == planted
                            if digest == commitment:
                                authentic.append((perm, orientations, first, second,
                                                  whitening, destination_layout, component.hex().upper()))
    assert tests == 36_864
    assert positive >= 1
    print("source_collision_Aes", "assignments", tests, "unique_components", len(unique),
          "planted_hits", positive, "original_hits", len(authentic))
    for found in authentic:
        print("K04_CANDIDATE", found)


if __name__ == "__main__":
    main()
