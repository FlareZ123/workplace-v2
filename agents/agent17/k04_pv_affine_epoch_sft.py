"""Source-only unknown-scale PV donor test built on Agent20's p955 projector.

This run excludes selected spool row129, K04 mask, and all acceptance data.
Usage in repo: python agents/agent17/k04_pv_affine_epoch_sft.py
Optional first argument is the resources directory.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import runpy
import statistics
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'resources'
PRODUCER = Path(__file__).resolve().parents[1] / 'agent20' / 'k04_p955_pv_future_source_only_sft.py'

# Agent20 checks exact original spool digest, source-only GF2 rank15305 and
# zero contradictions, and returns 154 source-predictable MT random floats.
with redirect_stdout(StringIO()) as captured:
    saved_argv = sys.argv
    sys.argv = [str(PRODUCER), str(ROOT)]
    try:
        source = runpy.run_path(str(PRODUCER))
    finally:
        sys.argv = saved_argv
assert 'SOURCE_RANK 15305 SOURCE_CONTRADICTIONS 0' in captured.getvalue()
pv = source['pv']
float53 = source['source_predictable']
word32 = {i: v / 2**32 for i, (v, mask) in source['fixed'].items() if mask == 0xFFFFFFFF}
assert len(float53) == 154 and len(word32) == 318


def affine_fit(observations):
    """Return least-squares offset, slope, RMS and rounded-match count."""
    n = len(observations)
    mx = statistics.fmean(x for x, y in observations)
    my = statistics.fmean(y for x, y in observations)
    variance = sum((x - mx) ** 2 for x, y in observations)
    assert variance > 0
    slope = sum((x-mx)*(y-my) for x,y in observations) / variance
    offset = my-slope*mx
    errors = [abs(offset + slope*x - y) for x,y in observations]
    return offset, slope, (sum(e*e for e in errors)/n)**0.5, sum(e <= 0.00050001 for e in errors)


def source_epoch_fit(source_values, stride):
    """One PV seq -> stride MT 32-bit draws, with unknown initial epoch."""
    feasible = []
    samples = list(range(100,212))
    for epoch in range(min(source_values) - stride*111, max(source_values) + 1):
        observations = [(source_values[idx],pv[seq])
                        for seq in samples
                        if (idx := epoch+stride*(seq-100)) in source_values]
        if len(observations) < 5:
            continue
        offset, slope, rms, exact = affine_fit(observations)
        feasible.append((rms,-exact,epoch,len(observations),offset,slope))
    feasible.sort()
    assert feasible
    assert not any(f[0] <= 0.001 for f in feasible)

    # A known affine scale must be recovered on 5+ synthetic samples.
    epoch = max(feasible, key=lambda f:f[3])[2]
    synthetic = [(source_values[idx], round(12+76*source_values[idx],3))
                 for seq in samples
                 if (idx := epoch+stride*(seq-100)) in source_values]
    assert len(synthetic) >= 5
    a,b,rms,exact = affine_fit(synthetic)
    assert abs(a-12)<0.001 and abs(b-76)<0.002 and rms < 0.0005
    print('PRODUCER_STRIDE',stride,'EPOCHS_WITH_FIVE_PLUS',len(feasible),
          'BEST_SOURCE_RMS',round(feasible[0][0],9),
          'BEST_EPOCH',feasible[0][2], 'BEST_SAMPLE_COUNT',feasible[0][3],
          'BEST_ROUNDED_MATCHES',-min(f[1] for f in feasible),
          'SYNTHETIC_AFFINE_CONTROL_PASS')
    return feasible


fits_float = source_epoch_fit(float53, 2)
fits_word = source_epoch_fit(word32, 1)
assert len(fits_float) == 1223 and len(fits_word) == 1357
assert abs(fits_float[0][0] - 2.886829310171501) < 0.000001
assert abs(fits_word[0][0] - 3.9658538212173293) < 0.000001
print('NO_MATCH: same-MT raw-float PV with affine unknown scale/epoch, both tested strides')
print('K04 target coupon never read; no authenticated selected bit or K08 phrase')
