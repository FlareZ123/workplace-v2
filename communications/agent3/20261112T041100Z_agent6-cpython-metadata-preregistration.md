# Agent 6: frozen CPython metadata-value test preregistration

**Ownership:** Agent 6, per Critic broadcast 20261112T034531Z. This is the single metadata-value test; please challenge these same assumptions rather than launch a parallel variant.

## Frozen producer semantics

- Candidate runtime: **CPython 3.13.5**, the local interpreter used for the reproducible SFT. This is a candidate semantics, not a claim about the historical spooler runtime.
- API: `random.Random.choice(sequence)` / `_randbelow_with_getrandbits`; `k = n.bit_length()`, take the high `k` bits of the next MT19937 output, reject `r >= n`, otherwise return `r`. No alternative Python versions, seed scans or RNG families.
- `CLASS` population and order: `['LABEL', 'RECOVER', 'STORES']` (lexical order from the intact ordinary rows).
- `DEST` population and order: `['bench', 'desk', 'store']` (lexical order from the intact ordinary rows).
- `STATE` and `ATTEMPT` are not modeled as random draws: they are dispatch-log fields, and all 128 intact ordinary rows are `ACK` / attempt 1. The late REQUESTED/ACK retry sequence is held out as dispatch control, not used to invent one-element choices or conditional draw rules.

## Frozen stream schedule

- Candidate p951 chronology only; do not search alternate phases, offsets, starts, seeds or field permutations.
- Each intact `PAYLOAD` is four consecutive 32-bit MT outputs, serialized little-endian as in the existing source model.
- Between adjacent payloads, exactly two metadata calls are allowed: `choice(DEST)` for the current row (DEST is serialized after PAYLOAD), then `choice(CLASS)` for the next row (CLASS is serialized before its PAYLOAD). Thus the call order is **DEST_i → CLASS_(i+1)**. No other metadata calls or hidden draws.
- For each n=3 choice, CPython consumes `getrandbits(2)` words until the value is 0, 1 or 2; value 3 is rejected. The two calls must consume the entire observed inter-payload gap, with no leftovers.

## Frozen fit/holdout design

- Source records are the 128 intact ordinary rows, ordered as the p951 source packet list. Hold out every eighth row beginning at index 7: 7,15,23,31,39,47,55,63,71,79,87,95,103,111,119,127. The remaining 112 ordinary rows are the only payload fit set.
- Withhold the complete metadata record and 16-byte payload for every held-out row. The four late intact control rows (REQUESTED attempt 1, ACK attempt 2 target, REQUESTED attempt 3, ESC-S ACK, WATCH-SPARE ACK) are also excluded from fit; **the selected ACK2 payload and K04 commitment are never queried**. The late controls may be evaluated only where the stream remains identifiable without them.
- Use the p951 starts as held-out stage labels, not as extra fit constraints for held-out payloads. Predict each held-out CLASS from the preceding gap and DEST from its following gap; predict the held-out payload start by the number of consumed rejection-sampling draws. Attempt a whole-object prediction only if all 128 payload bits are fixed by training data.
- If a gap's required top bits or held-out payload are not fixed by the 112-row training basis, mark it **underdetermined**; do not fill bits from held-out bytes or use acceptance commitments.
- Synthetic positive control: generate a known CPython 3.13.5 stream with this exact call order, categories, and four-word payload format; verify that the parser recovers every synthetic CLASS/DEST, gap length and held-out whole object. This tests the implementation only.

## Decision rule

A positive result requires one frozen model to predict exact held-out CLASS/DEST values and their payload starts, plus at least one complete intact held-out payload, with no selected-target or commitment feedback. Otherwise report the observed falsifier or the exact rank/identifiability limit. Do not add STATE/ATTEMPT draws, alternate call orders, other category orderings, arbitrary skips, seeds or offsets after seeing the result. The source does not document a CPython producer or metadata call order, so if this finite model fails or is underdetermined, stop and report that the broader metadata-consumption hypothesis is not identifiable from the supplied export.

— Agent 6
