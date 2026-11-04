"""Read-only source test of periodic XOR/add obfuscation of a CPython bytes seed.

Conditional on the published p951 first-cycle printer geometry. Four seed-key
terms from original intact printer packets (Agent 15) give constraints on a
2357..2428 byte binary seed. Selected 0417 ACK2 is not inspected.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2] / "resources" / "evidence"
SOURCE_DIRS = ("crew", "mail", "maintenance", "procedures", "telemetry", "transfers")
WORDS = {
    23: (0x06EDCDAD,),
    22: (0xFD6A4CF7,),
    601: (0x49342EC0,),
    602: (0x64589C88, 0xE4589C88),
}


def source_words(raw, end, reverse_word):
    values = {}
    for index in WORDS:
        start = end - 4 * (index - 15)
        word = raw[start:start + 4]
        values[index] = int.from_bytes(word[::-1] if reverse_word else word, "big")
    return values


def compatible(values, period, mode):
    for last in WORDS[602]:
        required = {23: WORDS[23][0], 22: WORDS[22][0],
                    601: WORDS[601][0], 602: last}
        pads = {i: (required[i] ^ values[i]) if mode == "xor"
                else (required[i] - values[i]) % (1 << 32) for i in values}
        if all(pads[i] == pads[j] for i in pads for j in pads
               if ((i-j) * 4) % period == 0):
            return last
    return None


def run():
    sources = []
    for group in SOURCE_DIRS:
        for path in (ROOT / group).rglob("*"):
            if path.is_file():
                raw = path.read_bytes()
                if len(raw) >= 2357:
                    sources.append((path.relative_to(ROOT).as_posix(), raw))

    matches, total = [], 0
    for name, raw in sources:
        for end in range(2357, len(raw) + 1):
            for reverse_word in (False, True):
                words = source_words(raw, end, reverse_word)
                for period in (4, 8, 16):
                    for mode in ("xor", "add"):
                        total += 1
                        value = compatible(words, period, mode)
                        if value is not None:
                            matches.append((name, end, reverse_word,
                                            period, mode, hex(value)))
    return {"source_files": [name for name, _ in sources],
            "endpoints": sum(len(raw) - 2356 for _, raw in sources),
            "transform_assignments": total,
            "matches": matches}


if __name__ == "__main__":
    synthetic = bytearray(range(256)) * 10
    end = len(synthetic)
    for index in WORDS:
        start = end - 4 * (index - 15)
        original = WORDS[index][0].to_bytes(4, "big")
        synthetic[start:start+4] = bytes(b ^ 0x5A for b in original)
    for period in (4, 8, 16):
        assert compatible(source_words(synthetic, end, False), period, "xor")
    result = run()
    print(json.dumps(result, indent=2))
    assert not result["matches"]
