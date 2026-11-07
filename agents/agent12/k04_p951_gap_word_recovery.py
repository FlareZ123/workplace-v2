"""Recover the selected K04 coupon once the eight minimal p951 gap words arrive.

Call from the workplace-v2 repository root. Words are 32-bit tempered MT19937
outputs, supplied as integers or 8-digit hexadecimal strings:
    recover_k04(gap43_words, gap96_words)

gap43_words are stages 328..331; gap96_words are stages 724..727.
The module reuses Agent49's source-only p951 basis and verifies the official
K04 slot commitment after applying the route mask.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.agent49.k04_p951_symbolic_basis import ORIGIN, STARTS, source, temper, untemper


GAP43_STAGES = (328, 329, 330, 331)
GAP96_STAGES = (724, 725, 726, 727)


def _word(value: int | str) -> int:
    parsed = int(value, 16) if isinstance(value, str) else int(value)
    if not 0 <= parsed <= 0xFFFFFFFF:
        raise ValueError("Each gap observation must be a 32-bit word")
    return parsed


def recover_k04(
    gap43_words: Sequence[int | str],
    gap96_words: Sequence[int | str],
) -> dict[str, str | bool]:
    """Recover the 16-byte selected payload and masked K04 component.

    Each sequence must contain four words in the stage order documented above.
    A contradictory observation raises ValueError through the shared GF(2) basis.
    """
    if len(gap43_words) != 4 or len(gap96_words) != 4:
        raise ValueError("Supply four gap43 words and four gap96 words")

    repo_root = REPO_ROOT
    basis, state = source(repo_root)
    if STARTS[129] != 951:
        raise AssertionError("The shared p951 stage alignment changed")

    observations = [
        (stage, _word(value))
        for stage, value in zip(GAP43_STAGES, gap43_words)
    ] + [
        (stage, _word(value))
        for stage, value in zip(GAP96_STAGES, gap96_words)
    ]

    for stage, output_word in observations:
        native_word = untemper(output_word)
        for bit, form in enumerate(state[stage - ORIGIN]):
            basis.insert(form, (native_word >> bit) & 1)

    payload = bytearray()
    for stage in range(STARTS[129], STARTS[129] + 4):
        output_forms = temper(state[stage - ORIGIN])
        word = 0
        for bit, form in enumerate(output_forms):
            value = basis.predict(form)
            if value is None:
                raise AssertionError("Eight gap words did not determine the selected 128-bit payload")
            word |= value << bit
        payload.extend(word.to_bytes(4, "little"))

    evidence = repo_root / "resources" / "evidence"
    route = json.loads((evidence / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((repo_root / "resources" / "acceptance.json").read_text(encoding="utf-8"))
    mask = bytes.fromhex(route["K04"]["masked_component"])
    component = bytes(a ^ b for a, b in zip(payload, mask))
    digest = hashlib.sha256(component).hexdigest()
    expected = acceptance["slot_sha256"]["K04"].lower()

    return {
        "coupon_payload": payload.hex().upper(),
        "component": component.hex().upper(),
        "sha256": digest,
        "expected_sha256": expected,
        "matches": digest == expected,
    }
