# K04: HST PV / CPython random-float screen

**Run:** 12 November 2026, Agent 43  
**Status:** bounded negative result; no K04 bytes recovered.

## Question

Can the 112 historian PV values provide additional constraints on the p951 MT19937 source state, rather than being treated as raw diagnostic words? The tested hypothesis was that each value is a CPython `random()`-derived engineering reading, rounded to three decimals, with a source-indexed relationship to the printer stream.

## Source basis

The test reused the p951 native-stage model in `agents/agent49/k04_p951_symbolic_basis.py`:

- 133 printer packet starts, `ORIGIN=-1100`;
- all 132 intact packet rows inserted, with selected row 129 (stages 951–954) withheld;
- resulting GF(2) rank: **15,365 / 19,968**;
- all 128 selected-row state bits remain undetermined by the printer-only basis.

The HST export contains 112 PV rows with unique `seq` values 100–211. The tested row orders were sequence order, file/retrieval order, and timestamp order.

## Model and test

For a CPython `random()` call, the 53-bit integer is

`x = ((word_1 >> 5) << 26) | (word_2 >> 6)`.

For a reading stored as `round(lo + (hi-lo)*x/2^53, 3)`, the observed decimal gives an exact integer interval for `x`. Its top 16 bits are the top 16 bits of `word_1`. I converted each value to the one- or two-element set of allowed top-16 prefixes, then checked the necessary prefix condition against every top-16 bit already fixed by the p951 basis. This is a conservative screen: it does not impose the lower 37 bits of the float.

Two simple engineering ranges were tested: **[10, 90]** and **[0, 100]**.

1. **Contiguous continuation:** one PV `random()` call per row, two MT outputs per call, at an unknown start offset 967–2078 after the last p951 printer stage. All three row orders were tested. **No offset** satisfied all 112 necessary prefix constraints for either range.
2. **Per-job interleave:** use the candidate numeric crosswalk `job_id = seq + 200`, associating each PV row with printer jobs 0300–0411. The two MT outputs for its `random()` call were allowed at any position in the gap after the corresponding four-word printer packet where a two-word call could fit. For both ranges, **29 of 112 rows had no compatible stage anywhere in their corresponding gap**. The immediate post-packet placement first conflicts at `seq=102`; the immediate pre-packet placement first conflicts at `seq=100`.

## Interpretation

These results reject only the tested simple CPython-float models: a contiguous post-printer run within the scanned offset window, and a one-float-per-job call placed in the corresponding p951 packet gap. They do **not** rule out a richer HST producer, another scale, another source ordering, a separate RNG, or an independent historian process. The export does not provide tag engineering ranges or a documented PV-to-printer call schedule, so further arbitrary scale/order searches would be overfitting.

The `seq` field was used as a join key, not asserted to be an MT output. Consistent with Agent 4's source-field boundary, treat it as an externally assigned historian identifier unless an original schema establishes otherwise. PV values and engineering units remain context, not raw `DIAG_WORD` material.

## Next action

Do not continue broad PV/MT generator scans without a source-defined scale and call schedule. Keep the HST `DIAG_WORD` branch with its current owner. The higher-value K04 path is an independently retained **complete selected/copy object** for `PS-261003-0417` attempt 2 (native job object and rendered/physical output), or a source-indexed A3 custody object that can establish where that output went. Existing acquisition locators and boundaries are consolidated in `results/h17-missing-evidence-request.md`; the 21 October custodian channel is closed and must not be reopened.
