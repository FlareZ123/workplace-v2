"""Bounded H-17 printer RS(16,8) source-format falsifier.

Runs locally in workplace-v2 with the unchanged resources/ tree.
No target ACK at 18:02, route mask, acceptance hash or K08 text is read.
The two tested intact controls have different event/physical stage relations.
This code tests a hypothetical encoder, not a historically attested printer law.
"""
from hashlib import sha256
from pathlib import Path
import re

SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
CONTROLS = (
    (
        "2026-10-03T18:24:00Z JOB=PS-261003-0448 ATTEMPT=1 STATE=ACK CLASS=RECOVER",
        "ESC-S late RECOVER ACK (other physical route)",
        ("DCC2D866F95E111A", "C2D866F95E111AE3", "DCB731CCD8DD6020", "B731CCD8DD60201A"),
    ),
    (
        "2026-10-03T16:45:00+00:00 JOB=PS-261003-0417 ATTEMPT=1 STATE=ACK CLASS=LABEL",
        "ESC-N same-job LABEL ACK (other class)",
        ("5AB25E7E420B2A6A", "B25E7E420B2A6AEF", "5A7A041150FE4821", "7A041150FE482185"),
    ),
)


def multiply(a: int, b: int) -> int:
    """GF(256) multiply, reduction polynomial x^8+x^4+x^3+x^2+1."""
    value = 0
    while b:
        if b & 1:
            value ^= a
        a <<= 1
        if a & 256:
            a ^= 0x11D
        b >>= 1
    return value


def alpha(power: int) -> int:
    value = 1
    for _ in range(power):
        value = multiply(value, 2)
    return value


def syndromes(frame: bytes, first_root: int) -> bytes:
    """Evaluate a high-order-first 16-byte polynomial at 8 consecutive roots."""
    values = []
    for offset in range(first_root, first_root + 8):
        root, accum = alpha(offset), 0
        for byte in frame:
            accum = multiply(accum, root) ^ byte
        values.append(accum)
    return bytes(values)


def encode_systematic(data: bytes, first_root: int) -> bytes:
    """Generate an eight-byte parity suffix for a positive-control message."""
    assert len(data) == 8
    generator = [1]
    for offset in range(first_root, first_root + 8):
        root = alpha(offset)
        updated = [0] * (len(generator) + 1)
        for index, coeff in enumerate(generator):
            updated[index] ^= coeff
            updated[index + 1] ^= multiply(coeff, root)
        generator = updated
    remainder = list(data) + [0] * 8
    for index in range(8):
        factor = remainder[index]
        for j in range(1, 9):
            remainder[index + j] ^= multiply(factor, generator[j])
    return data + bytes(remainder[8:])


def main() -> None:
    source = Path(__file__).resolve().parents[2] / "resources" / "evidence" / "print" / "spool-reconstruction.log"
    raw = source.read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA256, "Unexpected original spool"

    data = bytes.fromhex("0011223344556677")
    positive = (
        "0011223344556677AE917605785E1C76",
        "001122334455667776FAE648DC4811F9",
    )
    for first_root in (0, 1):
        codeword = encode_systematic(data, first_root)
        assert codeword.hex().upper() == positive[first_root]
        assert syndromes(codeword, first_root) == bytes(8)
        damaged = bytearray(codeword)
        damaged[5] ^= 0x80
        assert syndromes(damaged, first_root) != bytes(8)
    print("synthetic source-independent RS controls: PASS")

    lines = raw.decode("ascii").splitlines()
    for prefix, description, expected in CONTROLS:
        matching = [line for line in lines if line.startswith(prefix)]
        assert len(matching) == 1, "Non-unique source control"
        payload_hex = re.search(r"\bPAYLOAD=([A-F0-9]{32})\b", matching[0])
        assert payload_hex is not None, "Absent payload"
        payload = bytes.fromhex(payload_hex.group(1))
        observed = tuple(
            syndromes(frame, first_root).hex().upper()
            for frame in (payload, payload[::-1])
            for first_root in (0, 1)
        )
        assert observed == expected, "Original source or algorithm has drifted"
        assert all(any(bytes.fromhex(value)) for value in observed)
        print(description + ": four tested variants all non-codewords")
        for convention, syndrome in zip(("normal root0", "normal root1", "reversed root0", "reversed root1"), observed):
            print("  " + convention + " syndrome=" + syndrome)

    print("STOP: neither physical-route control matches the frozen fleet/ESC-N RS(16,8) family")
    print("No selected 18:02 ACK, mask, K04 commitment or K08 material consulted")


if __name__ == "__main__":
    main()
