# K04 CPython metadata-value holdout test — 12 November 2026

## Decision

<badge color="danger">Frozen model falsified</badge>

The single frozen CPython metadata-value model does **not** explain the source-fixed p951 stream and does not predict held-out complete objects. Stop this two-choice branch. The broader claim that metadata fields consume a shared CPython stream remains **unidentifiable from the supplied export**; do not expand into arbitrary field permutations, conditional calls, seeds or offsets.

This is a conditional test of Agent49's p951 stage labels, not authentication of a historical CPython producer or of p951 chronology.

## Frozen model

- Runtime semantics: CPython **3.13.5**, `random.Random.choice` / `_randbelow_with_getrandbits`; for a 3-item population, use `k=3.bit_length()=2`, take the high two bits of the next MT19937 output, reject 3, accept 0–2.
- `CLASS` population/order: `[LABEL, RECOVER, STORES]`.
- `DEST` population/order: `[bench, desk, store]`.
- The inter-payload schedule is exactly `DEST_i → CLASS_(i+1)`: DEST is serialized after the current payload; CLASS is serialized before the next payload. No other draws are permitted.
- Each payload is four consecutive 32-bit MT outputs, serialized little-endian.
- `STATE` and `ATTEMPT` are treated as dispatch-log fields, not random choices: all 128 intact ordinary rows are `ACK` / attempt `1`. The late retry rows remain held out; no one-element or conditional random calls were invented for them.
- Rejection sampling must consume the entire gap; no trailing or hidden draws are allowed.

The runtime version is the available test semantics, not a claim about the historical spooler. Category order is frozen lexically because the export supplies values but no source code documenting an internal choice-list order.

## Fit and holdout

Source: `resources/evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` (133 rows).

- Training: 112 of the 128 intact ordinary rows.
- Holdout: every eighth ordinary row, indices `7,15,23,31,39,47,55,63,71,79,87,95,103,111,119,127` (complete metadata and payload withheld from fit).
- The four late intact controls (rows 128, 130, 131, 132) were also excluded from fit.
- Selected ACK2 row 129's payload was **not loaded**. No K04 mask, acceptance commitment, candidate or verifier was read or used.
- The symbolic p951 basis was built only from the 112 training payloads at the existing p951 candidate positions. The p951 positions for held-out rows are treated as test labels, not fit constraints.

## Results

### Training contradictions

The 112-row payload-only basis has rank **13,442 / 19,968** symbolic state bits, leaving **6,526** free.

Among the 96 transitions whose two endpoint rows are both in training:

- The final output of the gap (which must be the accepted CLASS draw under this schedule) is fully fixed for 16 transitions.
- Only **6/16** equal the next row's CLASS code; **10/16** contradict it (indices 12, 13, 29, 58, 77, 83, 85, 99, 107, 117).
- Adding the training CLASS constraints in ascending transition order produces 12 linear conflicts (indices 4, 12, 13, 29, 58, 77, 83, 85, 99, 105, 107, 117).
- For the DEST rejection placement, deterministic constraint propagation yields 36 unique placements, 28 ambiguous transitions and 32 with no consistent placement. The resulting partial fit has rank 13,659 and still leaves 6,309 symbolic state bits.

The ordinary p951 inter-payload gap lengths are: 53 of length 2, 28 of length 3, 23 of length 4, 8 of length 5, 6 of length 6, 2 of length 7, 5 of length 8, 1 of length 9 and 1 of length 13. Thus **81/127** gaps are shorter than four words; a schedule that samples all four of CLASS, DEST, STATE and ATTEMPT once per ordinary row is structurally impossible without unsupported conditional omission rules.

### Held-out prediction

After fitting only training payloads and training metadata:

- Only three held-out CLASS values become determined: row 63 predicts RECOVER but is actually LABEL; row 87 predicts RECOVER correctly; row 119 predicts LABEL correctly.
- **Zero** held-out DEST values are determined.
- **Zero of 16** held-out ordinary payloads are complete (the number of fixed bits ranges from 0 to 127 of 128).
- Late whole-object controls have only 63, 31, 64 and 63 fixed bits respectively (rows 128, 130, 131, 132); none is complete.
- Sequential prediction from row 0 cannot advance: the first DEST draw at p951 position 4 is underdetermined. Consequently no held-out payload start is predicted by the frozen model.

This is not merely a lack of target overlap: the frozen value model already contradicts intact training CLASS values and fails to predict held-out metadata.

### Implementation control

A planted CPython 3.13.5 stream using the exact same categories, call order and payload format passes:

- 128/128 inter-payload gaps decoded exactly;
- all 16 synthetic held-out metadata records decoded exactly;
- all 128 next-payload starts predicted exactly;
- 83 rejection draws handled correctly.

The independent `getrandbits(2) == getrandbits(32) >> 30` control passes for four seeds × 100 draws. The synthetic positive validates the parser and rejection logic; it does not validate the historical producer.

## Interpretation and limits

The tested model is falsified under the frozen p951 alignment. The source export does not identify CPython, an internal category-list order, or a historical metadata-generation call order. The simple two-choice model is contradicted; a four-field-per-row model is incompatible with the observed short gaps; and no source document defines a conditional call schedule for STATE/ATTEMPT. Any wider family would therefore require arbitrary choices after seeing the data. Stop here and report the broader metadata-consumption hypothesis as unidentifiable from the supplied export.

No selected K04 bits were recovered. K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproduction

From the repository root:

```bash
python agents/agent6/k04_cpython_metadata_value_holdout_sft.py
```

The script uses only the standard library, defaults to the repository spool path, emits the full JSON diagnostics, and includes the synthetic planted control. It deliberately excludes the selected ACK2 payload and acceptance material.
