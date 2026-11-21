# Rolling PTW state as xoroshiro128++ input: bounded negative

Date: 2026-11-21  
Owner: Agent 2  
Status: Reproduced locally; no candidate

## Question

Can the rolling four-bay PTW register, formed from signed CLOSED/AS_LEFT serials, serve directly as the 128-bit initial state of xoroshiro128++ and emit the corresponding same-suffix PS ACK packet?

This is a target-blind constructor test. It does not assume that the PTW/PS numeric-suffix join is authentic; that join remains unverified.

## Inputs and selection

- Source receipts: `resources/evidence/maintenance/seal-receipts.jsonl`.
- Printer observations: `resources/evidence/print/spool-reconstruction.log`.
- For PTW-390 through PTW-416, select the signed CLOSED/AS_LEFT serial record for each permit. Each of these permits has one qualifying record and updates one bay in the rolling register.
- After each update, retain the current latest serial for each of the four bays. The first complete four-bay state occurs at suffix 395.
- Compare the resulting 22 states (PTW-395..416) with the single same-suffix ACK packet from PS-0395..0416. PS-0417 is excluded from both construction and evaluation.

## Constructor and frozen configurations

Each state consists of four 4-byte serial suffixes. The 16-byte state was constructed under:

- 2 bay orders: A/B/C/D and B/D/A/C;
- 2 byte orders within each 32-bit serial: big-endian and little-endian;
- 2 interpretations of the two 64-bit xoroshiro state words: big-endian and little-endian;
- 2 orders of the two 64-bit state words.

This gives 16 state interpretations. For each state, xoroshiro128++ was initialized directly and the first two 64-bit outputs were packed as the 16-byte predicted packet under four fixed output serializers: big/little endian, with normal/reversed 64-bit word order. No warm-up offsets were searched.

The standard xoroshiro128++ transition/output function is implemented in [the reproducer](../resources/work/test_rolling_ptw_xoroshiro128pp.py). The script validates the expected 22 source pairs and emits machine-readable JSON for all 64 fixed configurations.

## Result

**Result: 0 exact packet matches.**

- 22 complete same-suffix PTW/PS pairs evaluated.
- 16 state interpretations × 4 fixed output serializers = 64 configurations.
- Best result: 0 exact 16-byte packet matches out of 22 for every configuration.
- Reproduced locally against the supplied evidence export with the script's direct evidence-path option.

## Interpretation and limitations

This excludes only the exact direct-state, first-packet xoroshiro128++ constructor under the 64 declared serial/state/output serializations. It does not refute other deterministic producers or establish that the PTW/PS suffix join is real. The spool reconstruction log labels payload integrity unverified; the experiment therefore tests the retained ACK observations, not authenticated physical media.

No warm-up offsets, alternative PRNGs, key derivations, or target PS-0417 values were tested. Do not broaden this into a PRNG sweep. A future extension requires a new source-authored discriminator. The native PS-0417 spool/rendered output and authenticated job-to-physical-copy link remain the decisive K04 evidence.
