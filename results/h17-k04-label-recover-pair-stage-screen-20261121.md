# K04 LABEL→RECOVER pair-stage screen

**Agent 43 · 21 November 2026 · bounded negative**

## Question

Can the label-printer/fax observation in note N22, together with the adjacent N23 final-margin note, identify a repeatable copy-stage from a LABEL ACK payload to a RECOVER ACK payload? If a simple stage is learned from the note-aligned ordinary-job pairs, does it reproduce the selected PS-0417 RECOVER payload from PS-0417's earlier LABEL ACK?

This is materially different from applying fax-style bit-plane transforms to the selected RECOVER payload itself: here the earlier LABEL payload is the input and the adjacent LABEL→RECOVER job pairs are the controls.

## Source observations and limits

The source notes say:

- N22 (Simon): “The label printer has spent another morning thinking it is a fax machine.”
- N23 (Emily): “The wording in my margin was never an official slogan. The envelope only remembers the words I finally put on it.”

The documented 24/24 note-to-spool sequence crosswalk places N17/N18 at PS-0317/0318 and N22/N23 at PS-0322/0323. This is a sequence-based locator, **not a source-authenticated foreign key**. The spool records themselves establish these observed pairs:

| Pair | First record | Second record | Destination transition |
|---|---|---|---|
| Control 1 | PS-0317, ACK LABEL, 08:25Z, 5810C1B8C019ECCEFD4C989F711EF326 | PS-0318, ACK RECOVER, 08:30Z, 42D3EB66AF15924DF12166B6CD415819 | store → store |
| Control 2 | PS-0322, ACK LABEL, 08:50Z, 819BA09878C90DCB3B4326A7D50C5E14 | PS-0323, ACK RECOVER, 08:55Z, 1E51EFD2E5CA8F4E1FC8B49297B3D74F | bench → store |
| Target | PS-0417, ACK LABEL, 16:45Z, E1E60D5F6B6DD2225FA6D5A2A63AD932 | PS-0417, attempt-2 ACK RECOVER, 18:02Z, A9A9DC5731A5E2AE879C47215C2559D5 | bench → bench |

The controls therefore do not share the target's destination transition. Any route-independent transform is only a provisional hypothesis; a destination-specific printer stage is not identifiable from these two controls.

## Tested complete-output constructions

Using the original spool, note, routing and acceptance files (all source-pinned by SHA-256 in the reproducer), tested:

1. **Common XOR delta:** whether LABEL XOR RECOVER is identical across the two control pairs.
2. **Common byte permutation plus fixed per-output-byte constant:** all possible input positions for each output byte, requiring one bijection shared by both control pairs, under XOR, addition mod 256, and subtraction mod 256.
3. **Common per-byte bit permutation plus fixed XOR:** all 8! = 40,320 bit-position permutations, requiring the same 16-byte XOR residual across both controls.
4. **Direct commitment checks:** target RECOVER, target LABEL, target LABEL XOR RECOVER, and both control-pair XOR deltas, each XORed with the official K04 mask and checked against the unchanged K04 SHA-256 commitment.

Reproducer: agents/agent43/k04_label_recover_pair_sft.py

Run: python agents/agent43/k04_label_recover_pair_sft.py /path/to/h17-archive-dump.zip

## Results

- Control 1 LABEL XOR RECOVER: 1AC32ADE6F0C7E830C6DFE29BC5FAB3F.
- Control 2 LABEL XOR RECOVER: 9FCA4F4A9D038285248B923542BF895B.
- Target LABEL XOR RECOVER: 484FD1085AC8308CD83A9283FA1F80E7.
- The two control deltas differ.
- No common byte permutation plus fixed XOR/add/sub constants exists across the two control pairs.
- No common per-byte bit permutation plus fixed XOR exists across the 40,320 permutations.
- None of the five direct candidate coupons passes the K04 commitment.

The source-pinned reproducer returns zero original K04 hits. It does not alter the candidate, route, acceptance, verifier or original evidence.

## Conclusion and boundary

The N22/N23 note-aligned pair is a reasonable, source-cued way to test a LABEL→RECOVER copy-stage, but it does **not** support a route-independent bytewise XOR, byte-permutation affine, or per-byte bit-permutation-plus-XOR constructor. The controls' destination transitions differ from one another and from PS-0417, so this result does not exclude a destination-specific operation, a genuine fax codec, an original native spool/rendering object, or a different physical-coupon source.

No K04 bytes were recovered. The selected PS-0417 ACK payload remains an unverified copy, not a verified physical coupon. K04 and K08 remain unresolved; the six accepted slots and the official verifier remain unchanged.
