"""Extended real-output startup phase test for a CPython MT printer model.
Original selected spool row129 excluded; uses previously published exact source reconstruction.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[2] / "resources"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent28"))
from k04_cpython_real_output_offset_sft import source_states, mt, term_domains, consistent

SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U = 0xFFFFFFFF


def packets_from_rng(seed: int, offset: int) -> list[bytes]:
    rng = random.Random(seed)
    raw = [rng.getrandbits(32) for _ in range(offset + max(mt.STARTS) + 4)]
    return [b"".join(raw[offset + s + j].to_bytes(4, "little") for j in range(4))
            for s in mt.STARTS]


def test(offset: int) -> None:
    assert offset >= 624, "This experiment concerns additional complete MT cycles"
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    actual = [bytes.fromhex(w.decode()) for w in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(actual) == len(mt.STARTS) == 133

    # Real, independently seeded complete historical-layout positive.
    seed = 0x1234567890ABCDEF12345678
    synthetic = packets_from_rng(seed, offset)
    source_state = source_states(offset, synthetic)
    register = random.Random(seed).getstate()[1][:624]
    assert all(v == (t & mask) for (mask, v), t in zip(source_state, register))
    assert (source_state[0][1] ^ 0x80000000) & source_state[0][0] == 0
    rows = term_domains(source_state, 0)
    assert consistent(rows, 3)
    # A source-compatible seeded integer must retain its own full initialized register.
    print("PLANTED_REGISTER_POSITIVE", offset, "fixed_bits",
          sum(mask.bit_count() for mask, _ in source_state),
          "triples", len(rows), flush=True)

    source_state = source_states(offset, actual)
    initial_known = sum(mask.bit_count() for mask, _ in source_state)
    fully_known = sum(mask == U for mask, _ in source_state)
    near_known = sum(mask.bit_count() >= 31 for mask, _ in source_state)
    rows = term_domains(source_state, 0)
    zero_ok = ((source_state[0][1] ^ 0x80000000) & source_state[0][0]) == 0
    families = (1, 2, 4, 8, 16, 32, 64, 89, 128, 256, 365, 620, 621, 622, 623)
    results = {n: zero_ok and consistent(rows, n) for n in families}
    print("ORIGINAL_PHASE", offset, "known_init_bits", initial_known,
          "complete_words", fully_known, "near_full_words", near_known,
          "keyterm_domains", len(rows), "S0_possible", zero_ok,
          "candidate_seedlengths", results, flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Provide one integer startup offset >=624")
    test(int(sys.argv[1]))
