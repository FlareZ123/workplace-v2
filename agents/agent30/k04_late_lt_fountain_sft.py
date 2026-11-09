"""H-17 late RECOVER XOR-fountain whole-object source and target test.

After 128 ordinary jobs, hypothesize late RECOVER payloads as XOR-selected
subsets of those 128 payloads plus a common unknown copier XOR pad.
Calibrate from ESC-S and withhold WATCH-SPARE whole object. North copied
payload is not used in the prediction.
"""
from __future__ import annotations
import hashlib
import itertools
import re
import sys
import time
import zipfile
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = int("8556C8CB6140A7F9A5123AC7571BEE1C", 16)
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
DEGREES = (0, 1, 2, 4, 8, 16, 32, 64, 128)
PREFIXES = ("", "H17|", "IR-261003-H17|", "ESCROW|", "RECOVER|", "PS-261003|", "L-29|", "CEG-ARCHIVE|")
ALGORITHMS = ("sha256", "sha3_256", "blake2s", "blake2b")


def records(archive: str):
    path = Path(archive)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zip_source:
            original = zip_source.read("evidence/print/spool-reconstruction.log")
    else:
        original = path.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SPOOL_SHA
    matcher = re.compile(
        r"^(\S+) JOB=(PS-261003-\d{4}) ATTEMPT=(\d+) STATE=(\w+) "
        r"CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)$"
    )
    found = []
    for line in original.decode("ascii").splitlines():
        match = matcher.fullmatch(line)
        if match:
            timestamp, job, attempt, state, klass, payload, dest = match.groups()
            found.append({
                "timestamp": timestamp,
                "job": job,
                "attempt": int(attempt),
                "state": state,
                "klass": klass,
                "payload": bytes.fromhex(payload),
                "dest": dest
            })
    assert len(found) == 133
    regular = [
        entry for entry in found
        if 300 <= int(entry["job"][-4:]) <= 427
        and entry["attempt"] == 1 and entry["state"] == "ACK"
    ]
    regular.sort(key=lambda entry: entry["job"])
    assert len(regular) == 128
    assert [int(r["job"][-4:]) for r in regular] == list(range(300, 428))
    late = {}
    for route, job, attempt in (
        ("north", "0417", 2),
        ("south", "0448", 1),
        ("watch", "0420", 2)
    ):
        matches = [
            entry for entry in found
            if entry["job"].endswith(job) and entry["attempt"] == attempt
            and entry["state"] == "ACK" and entry["klass"] == "RECOVER"
        ]
        assert len(matches) == 1
        late[route] = matches[0]
    assert late["north"]["payload"].hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
    return regular, late


def serialize(entry: dict, form: int) -> bytes:
    job = entry["job"]
    attempt = entry["attempt"]
    klass = entry["klass"]
    dest = entry["dest"]
    timestamp = entry["timestamp"]
    forms = (
        job, job[-4:], f"{job}|{attempt}", f"{job}|{klass}|{dest}",
        f"{job}|{attempt}|{klass}|{dest}", f"{timestamp}|{job}",
        f"{job}|{timestamp}|{attempt}",
        f"{job}|{klass}|{timestamp}|{dest}|{attempt}"
    )
    return forms[form].encode("ascii")


def layout(payload: bytes, mode: int) -> bytes:
    if mode & 1:
        payload = payload[::-1]
    if mode & 2:
        payload = b"".join(payload[i:i + 4][::-1] for i in range(0, 16, 4))
    return payload


def aggregates(blocks: list[int], token: bytes) -> dict[int, int]:
    scores = hashlib.shake_256(b"LT-PRIORITIES:" + token).digest(128)
    indices = sorted(range(128), key=lambda j: (scores[j], j))
    aggregate = {0: 0}
    rolling = 0
    for j, index in enumerate(indices, 1):
        rolling ^= blocks[index]
        if j in DEGREES:
            aggregate[j] = rolling

    membership = int.from_bytes(
        hashlib.sha256(b"LT-MASK:" + token).digest()[:16], "big"
    )
    masked = 0
    for j in range(128):
        if membership >> j & 1:
            masked ^= blocks[j]
    aggregate[0] = masked
    return aggregate


def predict(agg: dict, late: dict, degree: int) -> tuple[int, int]:
    pad = agg["south"][degree] ^ int.from_bytes(late["south"]["payload"], "big")
    return agg["watch"][degree] ^ pad, agg["north"][degree] ^ pad


def run(original_path: str) -> None:
    regular, late = records(original_path)
    old_watch = int.from_bytes(late["watch"]["payload"], "big")
    checks = watch_matches = target_matches = 0
    max_watch_equal_bytes = 0
    first_hit = None
    synthetic_pass = False
    started = time.perf_counter()
    for mode, reverse, form, prefix, algorithm in itertools.product(
        range(4), (False, True), range(8), PREFIXES, ALGORITHMS
    ):
        rows = regular[::-1] if reverse else regular
        blocks = [int.from_bytes(layout(r["payload"], mode), "big") for r in rows]
        tokens = {
            role: hashlib.new(algorithm, prefix.encode() + serialize(entry, form)).digest()
            for role, entry in late.items()
        }
        agg = {role: aggregates(blocks, token) for role, token in tokens.items()}
        for degree in DEGREES:
            pred_watch, pred_north = predict(agg, late, degree)
            checks += 1
            watch_matches += pred_watch == old_watch
            max_watch_equal_bytes = max(
                max_watch_equal_bytes,
                sum(a == b for a, b in zip(
                    pred_watch.to_bytes(16, "big"), late["watch"]["payload"]
                ))
            )
            component = (pred_north ^ MASK).to_bytes(16, "big")
            if hashlib.sha256(component).digest() == TARGET:
                target_matches += 1
                first_hit = (
                    mode, reverse, form, prefix, algorithm, degree,
                    pred_north.to_bytes(16, "big").hex().upper(),
                    component.hex().upper()
                )

            if (mode, reverse, form, prefix, algorithm, degree) == (
                3, True, 5, "RECOVER|", "sha3_256", 16
            ):
                planted_pad = int.from_bytes(
                    bytes.fromhex("1742A577908BA66D638E7509EFA07C2B"), "big"
                )
                synthetic_south = (agg["south"][degree] ^ planted_pad).to_bytes(16, "big")
                synthetic_watch = (agg["watch"][degree] ^ planted_pad).to_bytes(16, "big")
                synthetic_north = (agg["north"][degree] ^ planted_pad).to_bytes(16, "big")
                fixture = {role: dict(entry) for role, entry in late.items()}
                fixture["south"]["payload"] = synthetic_south
                fixture["watch"]["payload"] = synthetic_watch
                recovered_watch, recovered_north = predict(agg, fixture, degree)
                assert recovered_watch.to_bytes(16, "big") == synthetic_watch
                assert recovered_north.to_bytes(16, "big") == synthetic_north
                synthetic_digest = hashlib.sha256(
                    (recovered_north ^ MASK).to_bytes(16, "big")
                ).digest()
                assert synthetic_digest == hashlib.sha256(bytes(
                    a ^ b for a, b in zip(
                        synthetic_north, MASK.to_bytes(16, "big")
                    )
                )).digest()
                synthetic_pass = True

    expected = 4 * 2 * 8 * len(PREFIXES) * len(ALGORITHMS) * len(DEGREES)
    assert synthetic_pass and checks == expected
    print("ORIGINAL_SPOOL_SHA", SPOOL_SHA)
    print("ORIGINAL_LATE_LT_FOUNTAIN_MODELS", checks)
    print("UNSEEN_WATCH_WHOLE_COUPON_MATCHES", watch_matches)
    print("MAX_WATCH_EQUAL_BYTES", max_watch_equal_bytes)
    print("ORIGINAL_K04_COMMITMENT_HITS", target_matches)
    print("SYNTHETIC_SOURCE_WATCH_AND_NORTH_WHOLE_POSITIVE", synthetic_pass)
    print("ORIGINAL_HIT_DETAIL", first_hit)
    print("ELAPSED_SECONDS", round(time.perf_counter() - started, 3))
    assert watch_matches == 0 and target_matches == 0


if __name__ == "__main__":
    default = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    run(sys.argv[1] if len(sys.argv) > 1 else str(default))
