# K04 PTW-serial bridge falsification

**Question.** Can the maintenance seal serials provide the missing K04 coupon directly, or supply the two complete four-word gaps that make the conditional p951 MT model determine K04?

**Why this was tested.** The spool contains job suffixes PS-0390 through PS-0417, while the maintenance export contains signed CLOSED/AS_LEFT permit serials PTW-0390 through PTW-0417. The selected PTW-417 quartet is also the source for accepted K03, and the p951 analysis identifies two four-word blocks (native output stages 328–331 and 724–727) whose values would fully determine the target under that conditional model. This is a specific cross-source join hypothesis, not a source-attested relationship.

## Method and results

The reproducible test is `work/h17_k04_ptw_serial_bridge_sft.py`.

1. **Raw four-serial coupon.** Enumerated every ordered four-tuple of distinct serials among the 36 unique signed CLOSED/AS_LEFT serial values, with all 16 independent per-word byte-order choices. This covers 22,619,520 16-byte candidates. None matched the K04 SHA-256 commitment.

2. **p951 gap blocks.** Built 25 candidate four-word blocks: the 24 consecutive permit windows PTW-390–393 through PTW-413–416 (latest signed CLOSED/AS_LEFT serial per permit, in permit order), plus the accepted K03 PTW-417 quartet in B,D,A,C witness order. Tested every ordered pair of distinct blocks at native stages 328–331 and 724–727, with both endian interpretations for each block: 2,400 complete candidate pairs. None produced the committed K04 component.

   The base source basis has rank 15,365; adding two complete four-word blocks raises it to 15,621 and fully predicts the target in all 2,400 cases. There were no source-equation conflicts. This compatibility is expected from the model's 128-bit target quotient; **the acceptance commitment, not mere basis compatibility, is the discriminating test**.

3. **Same-suffix seed control.** Matched PTW-390–416 serials to the same-suffix PS-0390–0416 spool jobs and used each 32-bit serial as a seed for 12 common 16-byte PRNG serializations (CPython MT, C++ `std::mt19937`, Java `Random`, xorshift32, and SplitMix64). Across 27 permit/job pairs this gave 324 comparisons and zero exact payload matches.

## Conclusion

The simple PTW-to-printer bridge is falsified in the tested forms:

- no raw four-seal serial block is K04;
- no contiguous PTW serial window (or PTW-417 quartet) supplies the two p951 gap blocks;
- same-suffix PTW serials do not directly seed the corresponding spool payloads under the tested standard generators.

Do not repeat these exact searches or treat the shared numeric suffix as an authenticated foreign key. This does **not** rule out a different transformation, a non-contiguous source selection, or an independent native ESC-N coupon source. The p951 MT model remains conditional; the result does not establish that the printer actually used this generator.

**Reproduction:** from the repository root, run:

```bash
python work/h17_k04_ptw_serial_bridge_sft.py
```

The script imports the existing p951 symbolic-basis implementation and witness selector, reads only repository evidence and acceptance commitments, and does not modify canonical candidate data or the verifier.
