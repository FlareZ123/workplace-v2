"""Source-only K04: additive 16-bit AX-checkpoint emitter against p951 printer MT.

Hypothesis: each AX checkpoint is one 16-bit view of a native/tempered MT
output plus a fixed per-transfer salt modulo 2**16, with constant stage
stride 1..16. The selected printer ACK is excluded from the source model.
This is a conditional model, not evidence of historical shared firmware.
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "resources"
AGENT1 = HERE.parent / "agent1" / "k04_ax_extended_source_sft.py"
spec = importlib.util.spec_from_file_location("ax_source", AGENT1)
ax = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ax)

MIN_TRAIN_BITS = 32
MIN_HELDOUT_BITS = 24


def compatible_salts(training):
    """Solve the fixed 16-bit modular-addition salt by exact bit-prefix pruning.

    training contains (known_bit_mask, predicted_known_bits, observed16).
    Unknown producer bits are unconstrained; all known bits must agree.
    """
    prefixes = [0]
    for j in range(16):
        bit = 1 << j
        next_prefixes = []
        for low in prefixes:
            for salt in (low, low | bit):
                if all((((observed - salt) ^ value) & mask & bit) == 0
                       for mask, value, observed in training):
                    next_prefixes.append(salt)
        prefixes = next_prefixes
        if not prefixes:
            return []
    return prefixes


def synthetic_positive():
    salt = 0xAB3D
    words = [(0x0F77 + i * 137) & 0xFFFF for i in range(16)]
    observed = [(x + salt) & 0xFFFF for x in words]
    training = [(0xFFFF, x, y) for x, y in zip(words[:8], observed[:8])]
    assert compatible_salts(training) == [salt]
    assert all((((y - salt) ^ x) & 0xFFFF) == 0
               for x, y in zip(words[8:], observed[8:]))
    altered = observed[8:].copy()
    altered[3] ^= 1
    assert any((((y - salt) ^ x) & 0xFFFF) != 0
               for x, y in zip(words[8:], altered))
    partial = [(0x0FFF, (0xF000 + i * 7) & 0x0FFF,
                (0xF000 + i * 7 + salt) & 0xFFFF) for i in range(8)]
    assert (salt & 0x0FFF) in {s & 0x0FFF for s in compatible_salts(partial)}


def scan(predicted, observed):
    """Return number of qualifying windows and every training-consistent fit."""
    n = len(predicted)
    windows = 0
    fits = []
    for stride in range(1, 17):
        for start in range(n - stride * 15):
            train = [(predicted[start + i * stride][0],
                      predicted[start + i * stride][1], observed[i])
                     for i in range(8)]
            bits = sum(mask.bit_count() for mask, _, _ in train)
            if bits < MIN_TRAIN_BITS:
                continue
            windows += 1
            for salt in compatible_salts(train):
                good = bad = 0
                for i in range(8, 16):
                    mask, value = predicted[start + i * stride]
                    diff = ((observed[i] - salt) ^ value) & mask
                    good += (mask & ~diff).bit_count()
                    bad += diff.bit_count()
                fits.append((start + ax.p951.ORIGIN, stride, salt,
                             bits, good, bad))
    return windows, fits


def main():
    synthetic_positive()
    basis, states = ax.symbols(ROOT)
    transfers = ax.transfer_checkpoints(ROOT)
    print("printer_source_rank", basis.rank, "selected_row_excluded", 129,
          flush=True)
    assert basis.rank == 15365
    findings = []
    all_fits = []
    window_count = 0
    for tempered in (False, True):
        for upper in (False, True):
            predicted = ax.predictions(basis, states, tempered, upper)
            for name, raw in transfers.items():
                for swapped in (False, True):
                    observed = [((x & 0xFF) << 8) | (x >> 8) if swapped else x
                                for x in raw]
                    windows, fits = scan(predicted, observed)
                    window_count += windows
                    all_fits.extend((name, tempered, upper, swapped, f)
                                    for f in fits)
                    retained = [f for f in fits if f[5] == 0 and
                                f[4] >= MIN_HELDOUT_BITS]
                    findings.extend((name, tempered, upper, swapped, f)
                                    for f in retained)
                    print(json.dumps({
                        "transfer": name, "tempered": tempered,
                        "upper": upper, "swapped": swapped,
                        "training_windows": windows,
                        "training_fits": fits,
                        "heldout_accepted": retained,
                    }), flush=True)
    expected = ("AX-7778", True, True, True, (-157, 1, 0, 45, 77, 0))
    assert findings == [expected], findings
    assert window_count == 1636072, window_count
    assert len(all_fits) == 6, all_fits
    print(json.dumps({
        "status": "NO_NEW_TARGET_SOURCE",
        "stage_view_training_windows": window_count,
        "training_fit_count": len(all_fits),
        "heldout_accepted_models": findings,
        "synthetic_nonzero_salt": "PASS",
        "original_source_control": "PASS",
        "K04_original_selected_bits_authenticated": 0
    }, sort_keys=True))


if __name__ == "__main__":
    main()
