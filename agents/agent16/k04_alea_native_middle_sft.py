"""H-17 K04: exact Alea/MWC3 whole-packet missing-middle inversion SFT.

Source-pinned original spool. Selected ACK2 copy is excluded from inference.
Johannes Baagoe Alea multiplier, 2091639, with three 32-bit lag states.
"""
import hashlib
import itertools
import os
import re
from pathlib import Path

A = 2091639
Q = 1 << 32
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K04_TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")


def serialize(words, order, flip):
    chunks = [b""] * 4
    for j, index in enumerate(order):
        chunks[index] = words[j].to_bytes(
            4, "little" if flip & (1 << index) else "big"
        )
    return b"".join(chunks)


def recover(packet, future=12):
    """Generate complete future packets from every source-consistent view."""
    assert len(packet) == 16
    for order in itertools.permutations(range(4)):
        for flip in range(16):
            words = tuple(
                int.from_bytes(
                    packet[4*i:4*(i+1)],
                    "little" if flip & (1 << i) else "big",
                )
                for i in order
            )
            carry3 = (words[3] - A * words[0]) % Q
            if carry3 >= A:
                continue
            out = list(words)
            carry = (A * out[0] + carry3) // Q
            for i in range(4, future):
                n = A * out[i-3] + carry
                out.append(n % Q)
                carry = n // Q
            yield order, flip, carry3, out


def read_rows():
    root = Path(os.environ.get(
        "H17_SOURCE_ROOT",
        str(Path(__file__).resolve().parents[2] / "resources"),
    ))
    source = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    pat = re.compile(
        r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) "
        r"PAYLOAD=([A-F0-9]{32})"
    )
    rows = [m.groups() for line in source.decode().splitlines()
            if (m := pat.search(line))]
    assert len(rows) == 133
    return rows


def main():
    # Positive: hide all four output words of the middle of a twelve-word
    # synthetic Alea/MWC3 sequence; invert the first, check the third.
    words = [0x10203040, 0x50607080, 0x90A0B0C0]
    carry = 123456
    for i in range(3, 12):
        n = A * words[i-3] + carry
        words.append(n % Q)
        carry = n // Q
    order, flip = (2, 0, 3, 1), 0b1010
    first = serialize(words[:4], order, flip)
    hidden = serialize(words[4:8], order, flip)
    third = serialize(words[8:12], order, flip)
    predicted = [
        (o, f, out)
        for o, f, _, out in recover(first)
        if serialize(out[8:12], o, f) == third
    ]
    assert any(
        o == order and f == flip
        and serialize(out[4:8], o, f) == hidden
        for o, f, out in predicted
    )
    synthetic_target = hashlib.sha256(bytes(
        x ^ y for x, y in zip(hidden, MASK)
    )).hexdigest()
    assert any(
        hashlib.sha256(bytes(
            x ^ y for x, y in zip(serialize(out[4:8], o, f), MASK)
        )).hexdigest() == synthetic_target
        for o, f, out in predicted
    )
    print("PLANTED complete_erased_middle=PASS heldout_third=PASS K04_gate=PASS")

    rows = read_rows()
    selected = next(r for r in rows
                    if r[0].endswith("0417") and r[1:4] == ("2", "ACK", "RECOVER"))
    assert selected[:4] == ("PS-261003-0417", "2", "ACK", "RECOVER")
    cases = (
        ("0417-REQUESTED-1", "0417", "1"),
        ("0417-REQUESTED-3", "0417", "3"),
        ("0448-ACK-1", "0448", "1"),
        ("0420-ACK-2", "0420", "2"),
    )
    first_fits = []
    for label, suffix, attempt in cases:
        row = next(r for r in rows if r[0].endswith(suffix)
                   and r[1] == attempt and r[3] == "RECOVER")
        fits = list(recover(bytes.fromhex(row[4])))
        print("ORIGINAL_SOURCE", label, "views=384",
              "Alea_native_state_fits=", len(fits))
        if suffix == "0417" and attempt == "1":
            first_fits = fits

    third = bytes.fromhex(next(r[4] for r in rows
                               if r[0].endswith("0417") and r[1] == "3"))
    accepted = 0
    for order, flip, _, out in first_fits:
        predicted_third = serialize(out[8:12], order, flip)
        coupon = serialize(out[4:8], order, flip)
        component = bytes(x ^ y for x, y in zip(coupon, MASK))
        if predicted_third == third:
            print("SOURCE_THIRD_WHOLE_MATCH", order, flip)
        if hashlib.sha256(component).hexdigest() == K04_TARGET:
            accepted += 1
            print("ORIGINAL_K04_PASS", component.hex().upper())
    print("ORIGINAL_K04_ACCEPTED", accepted,
          "selected_ACK2_copy_used_for_inference=False")


if __name__ == "__main__":
    main()
