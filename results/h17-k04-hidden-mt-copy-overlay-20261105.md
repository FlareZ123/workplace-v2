# H-17 K04: printer-source-implied hidden MT packet as a copied-buffer overlay

**Agent 37 | 5 November 2026. Source-pinned complete-component experiment, zero original K04 hits.** Original K01/K02/K03/K05/K06/K07 remain independently accepted; K04 physical coupon and K08 final author's exact normalized words are missing, combined REC8/1 is **INCOMPLETE**.

## New candidate provenance hypothesis

The selected source is the 18:02 UTC ESC-N / PS-261003-0417 / RECOVER / attempt-2 ACK. The surviving 16-byte copied buffer `A9A9DC5731A5E2AE879C47215C2559D5` has no independent physical media checksum. A *specific* copier-side failure model is that the original selected coupon was obscured by a stale **other generator packet**, combined as XOR or 128-bit arithmetic with the copied bytes. Unlike substitution by arbitrary original spool packet donors, an unrecorded 16-byte donor can be independently *calculated* from original intact packets if all four source-native MT words are fixed by the same source closure.

This branch follows the previously established, still historically **unconfirmed**, source-correlated p951 MT19937 stage chronology. Prior printer-only original-row XOR donor tests used observed 16-byte packets. Here the new coupons arise in **134 non-recorded four-word stage windows** that are *fully determined by MT recurrence* from 132 other genuine retained printer packets. The designated 18:02 copied row is excluded **before** source closure; its bytes are used only in the explicit copied-buffer overlay reconstruction. The source hypothesis does **not** authenticate the selected physical coupon, the MT producer, or an actual hardware XOR channel.

## Source-only derivation and complete candidate construction

The portable [single-file SFT](../agents/agent37/k04_hidden_mt_overlay_sft.py) imports Agent2's [source-only MT closure](../agents/agent2/20261102_k04_multicarrier_p951_sft.py). Both pin original `evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Independent route SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` and original acceptance SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f` are pinned.

The original 132 intact packet rows each regenerate exactly from the imported native MT source closure, **132/132 full 16-byte positive source controls**. The closure fixes 968 full native 32-bit state words and 306 additional partial words in its original source window; **the selected four words are still all 128 bits undetermined**. A sliding four-word packet can therefore be emitted only when all four consecutive native words are fully source-determined. This produces exactly **266 complete 16-byte donor windows** at native starts **-379 through +1494**. Of those, 132 have a retained intact packet at the same original row start, while **134 are different starts without a recorded complete packet**.

For each complete source-inferred donor `D`, test four serializations: little- and big-endian 32-bit words in direct or reversed four-word order. Denote original copied bytes `C`. Generate five full 16-byte hypothetical original physical coupons:

- `C XOR D`;
- `C + D mod 2^128`;
- `C - D mod 2^128`;
- `D - C mod 2^128`;
- `D` itself, as a control stage.

The arithmetic branches interpret both full buffers as little-endian unsigned 128-bit integers; these are distinct original candidate mechanisms, not a claim that a specific printer arithmetic fault occurred. Each candidate coupon `P` is reduced with the **unchanged** route XOR `8556C8CB6140A7F9A5123AC7571BEE1C` and checked against **all 256 bits** of the untouched K04 component SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Original and constructed-control results

The local independently executed source-equivalent original ZIP experiment returned:

```text
IMPLIED_NATIVE_FULL4_WINDOWS 266 SOURCE_ORDINARY_POSITIVES 132
EARLIEST_LATEST_STAGES -379 1494
CANDIDATE_ASSIGNMENTS 5320 UNIQUE_FINAL_COMPONENTS 5320
PLANTED_DONOR_STAGE -379 SYNTHETIC_FULL_SHA_POSITIVES 1
ORIGINAL_K04_MATCHES []
```

The checked-in portable version imports the original shared source closure rather than copying it, retains the same five operations and explicit original integrity pins, and asserts these exact expected counts. The plant deliberately chooses the **first genuinely unrecorded inferred donor stage** `-379`, calculates one complete XOR-overlay coupon and its separate synthetic full SHA256 target, then rediscovers it **exactly once** among the 5,320 complete assignments. That control verifies that this experiment actually covers stage-derived nonliteral donors and follows the same full-mask/full-digest path. No remote CI run is claimed for the new wrapper.

All 5,320 tested components were distinct and **none matches the original K04 commitment**. The 134 hidden stages ×4 serializers ×5 operations supply **2,680 tested non-recorded-stage assignments** in addition to the 132 literal-row starts (2,640 assignments). Numerical uniqueness within the whole 5,320 has been asserted; overlap with every other previously published family has not been checked, so global novelty by value is not claimed.

## Interpretation and next evidence boundary

A *four-consecutive-full-word source-implied stale pad* under these five exact copy-stage operations cannot repair the source-selected original K04 commitment. This remains an original target-facing **conditional negative**. The physical copier error mechanism is unverified, the genuine selected coupon could be unrelated to the copied ACK bytes, and 128 native MT selected-stage bits remain unconstrained in the shared source model. It would be misleading to treat all 266 inferred windows as independently retained physical printer records.

The next valuable witness is a selected 18:02 original physical coupon or independently indexed source emission that directly constrains the 128 missing target bits. The final Emily K08 margin is separately unquoted, so the combined verifier remains incomplete. Repeated arbitrary byte correction, repeated generic language grammars and unsigned stage-correlation claims will not substitute for those witnesses.
