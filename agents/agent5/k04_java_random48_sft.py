"""Read-only direct Java Random 48-bit LCG output test against H17 routine spool."""
from __future__ import annotations
import re
from pathlib import Path
from random import Random

A = 0x5DEECE66D
C = 0xB
MASK = (1 << 48) - 1
SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"


def next_state(s: int) -> int:
    return (s * A + C) & MASK


def recover(first: int, second: int) -> list[int]:
    """The top 32 bits of two consecutive 48-bit states disclose low 16 bits."""
    return [state for low in range(1 << 16)
            if ((next_state(state := ((first << 16) | low))) >> 16) == second]


def synthetic_controls() -> None:
    rng = Random(20261103)
    for _ in range(100):
        s = rng.getrandbits(48)
        words = []
        for _ in range(4):
            s = next_state(s)
            words.append(s >> 16)
        states = recover(words[0], words[1])
        assert states
        assert any((next_state(next_state(x)) >> 16) == words[2]
                   and (next_state(next_state(next_state(x))) >> 16) == words[3]
                   for x in states)
    print("SYNTHETIC java.util.Random controls: 100/100")


def original() -> None:
    lines = [line for line in SOURCE.read_text(encoding="utf-8").splitlines()
             if "PAYLOAD=" in line]
    assert len(lines) == 133
    payloads = []
    for i, line in enumerate(lines[:128]):
        assert f"JOB=PS-261003-{300 + i:04d} " in line
        assert "ATTEMPT=1 STATE=ACK" in line
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match
        payloads.append(bytes.fromhex(match.group(1)))
    for endian in ("big", "little"):
        for reverse in (False, True):
            possible_first_two = 0
            complete = 0
            for payload in payloads:
                words = [int.from_bytes(payload[j:j + 4], endian)
                         for j in range(0, 16, 4)]
                if reverse:
                    words.reverse()
                states = recover(words[0], words[1])
                possible_first_two += bool(states)
                complete += any((next_state(next_state(x)) >> 16) == words[2]
                                and (next_state(next_state(next_state(x))) >> 16) == words[3]
                                for x in states)
            print(f"ORIGINAL {endian} reverse={reverse}:"
                  f" first-pair state fits={possible_first_two}/128,"
                  f" complete packet fits={complete}/128")


if __name__ == "__main__":
    synthetic_controls()
    original()
