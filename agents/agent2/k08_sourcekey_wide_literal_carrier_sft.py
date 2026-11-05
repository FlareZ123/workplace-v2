"""Read-only original K08 candidate search in wide/archival-source-key literal carriers.

Searches intact source evidence for contiguous word passages after UTF-16/32
decoding or 16-byte repeating XOR against the original desk nonce, K04 mask,
or one of the six authenticated components. It does NOT infer a plaintext.
"""
from hashlib import sha256
import hmac
from itertools import product
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resources"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
WORD = re.compile(r"[a-z0-9]+")
PRINTABLE = frozenset(range(32, 127)) | {9, 10, 13}


def normalize(value: str) -> str:
    return " ".join(WORD.findall(value.lower()))


def reduction(value: str, nonce: bytes) -> str:
    part = hmac.new(nonce, normalize(value).encode("utf-8"), "sha256").digest()[:16]
    return sha256(part).hexdigest()


def xor_pad(source: bytes, key: bytes, phase: int) -> bytes:
    return bytes(value ^ key[(index + phase) % 16] for index, value in enumerate(source))


def ascii_runs(stream: bytes):
    run = []
    for value in stream:
        if value in PRINTABLE:
            run.append(chr(value))
        else:
            if len(run) >= 12:
                yield "".join(run)
            run.clear()
    if len(run) >= 12:
        yield "".join(run)


def wide_runs(stream: bytes, width: int, order: str):
    for phase in range(width):
        run = []
        for index in range(phase, len(stream) - width + 1, width):
            value = int.from_bytes(stream[index:index + width], order)
            if value in PRINTABLE:
                run.append(chr(value))
            else:
                if len(run) >= 12:
                    yield "".join(run)
                run.clear()
        if len(run) >= 12:
            yield "".join(run)


def phrases(run: str):
    words = WORD.findall(run.lower())
    for left in range(len(words)):
        for right in range(left + 2, min(left + 24, len(words)) + 1):
            if sum(len(word) for word in words[left:right]) >= 8:
                yield " ".join(words[left:right])


def main():
    notes = (RES / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(notes).hexdigest() == NOTES_SHA

    route = json.loads((RES / "evidence/recovery-routing.json").read_text())
    target = json.loads((RES / "acceptance.json").read_text())
    candidate = json.loads((ROOT / "candidate.json").read_text())
    assert target["slot_sha256"]["K08"] == TARGET
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    assert hmac.new(nonce, normalize(
        "A good watch leaves the room ready for the next pair of hands."
    ).encode(), "sha256").digest()[:16].hex().upper() == (
        "BF889359B0303F2B2B2FD96AE841210B"
    )

    keys = {"desk_nonce": nonce,
            "K04_mask": bytes.fromhex(route["K04"]["masked_component"])}
    for label in ("K01", "K02", "K03", "K05", "K06", "K07"):
        assert sha256(bytes.fromhex(candidate[label])).hexdigest() == target["slot_sha256"][label]
        keys[label] = bytes.fromhex(candidate[label])
    assert len(keys) == 8 and all(len(key) == 16 for key in keys.values())

    # All four character encodings pass a deliberately inserted full-caption
    # control, with an independently specified nonzero XOR phase.
    planted = "The sea outside and room for one more at the table"
    for width, order in product((2, 4), ("little", "big")):
        encoding = ("utf-16-" if width == 2 else "utf-32-") + (
            "le" if order == "little" else "be"
        )
        encoded = b"@@" + planted.encode(encoding) + b"!!"
        cipher = xor_pad(encoded, nonce, 7)
        recovered = xor_pad(cipher, nonce, 7)
        assert normalize(planted) in {
            phrase for run in wide_runs(recovered, width, order)
            for phrase in phrases(run)
        }
    ascii_cipher = xor_pad(b"@@" + planted.encode() + b"!!", nonce, 9)
    assert normalize(planted) in {
        phrase for run in ascii_runs(xor_pad(ascii_cipher, nonce, 9))
        for phrase in phrases(run)
    }
    assert reduction(planted, nonce) == reduction(normalize(planted), nonce)

    counts = {"source_files": 0, "ascii_runs_12+": 0,
              "wide_runs_12+": 0, "assignments": 0}
    seen = set()
    hits = []
    for path in sorted((RES / "evidence").rglob("*")):
        if not path.is_file():
            continue
        counts["source_files"] += 1
        raw = path.read_bytes()
        for name, key in [("plain", None), *keys.items()]:
            for phase in range(1 if key is None else 16):
                stream = raw if key is None else xor_pad(raw, key, phase)
                for width, order in [(1, "ascii"), *product((2, 4), ("little", "big"))]:
                    # Plain ASCII original-source span census predates this test.
                    if width == 1 and key is None:
                        continue
                    runs = ascii_runs(stream) if width == 1 else wide_runs(stream, width, order)
                    for run in runs:
                        counts["ascii_runs_12+" if width == 1 else "wide_runs_12+"] += 1
                        for phrase in phrases(run):
                            counts["assignments"] += 1
                            if phrase in seen:
                                continue
                            seen.add(phrase)
                            if reduction(phrase, nonce) == TARGET:
                                hits.append({"path": str(path.relative_to(RES)),
                                             "key": name, "phase": phase,
                                             "width": width, "endian": order,
                                             "text": phrase})
    counts["unique_phrases"] = len(seen)
    print(json.dumps({"counts": counts, "hits": hits}, indent=2))
    assert counts == {"source_files": 42, "ascii_runs_12+": 3,
                      "wide_runs_12+": 0, "assignments": 1, "unique_phrases": 1}
    assert not hits


if __name__ == "__main__":
    main()
