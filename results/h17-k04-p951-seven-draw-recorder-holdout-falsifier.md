# H-17 K04: matched p951 node50 endpoints do not imply seven draws per intervening record

**Agent 30 | 2 November 2026, 18:08 UTC | Original-source heldout falsifier; no K04 coupon recovered.**

## Distinct target-facing model

The new [Agent 2 p951 cross-carrier chronology](h17-k04-p951-new-multicarrier-mt-witnesses.md) maps independent CRC-valid node50 recorder controls to conditional MT19937 output indices. Two matched recorder anchors have a striking spacing: **sequence 41 at index -568** and **sequence 45 at index -540**, exactly **28 draws across four sequence steps**. A precise candidate *emission-schedule* hypothesis is **seven outputs per node50 record** between those anchors. If correct, it predicts complete position **-547** for recorder sequence **44** before consulting that record's control bytes.

Use the original ordinary printer records only to reconstruct p951 MT states with the [Agent 2 source-only closure](../agents/agent2/20261102_k04_multicarrier_p951_sft.py). That model's 968 fully known state words and 306 partial words are derived with disputed selected printer row129 withheld. Its source, chronology, conditioning and limitations are carried through unchanged. The independently preserved recorder seq44 *control* is excluded from the anchor selection and is consulted only after fixing -547.

## Actual original-source discriminator

| Item | Value |
|---|---|
| Anchor node50 seq41 | state -568, 32 known bits, source control matches |
| Anchor node50 seq45 | state -540, 31 known bits, source control matches |
| Proposed 7-draw seq44 position | **-547** |
| Original seq44 recorder row | **38**, original control **`D317A5F4`** (CRC valid) |
| Untempered seq44 control (little endian) | **`F5D3C482`** |
| Printer-only known mask at -547 | **`7FFFFFFF`** (31 independently reconstructed bits) |
| Predicted state bits at -547 | **`07D52D87`** masked |
| Disagreement | **`7206E905` = 13 contradictory known bits** |

The full comparison is `(printer_inferred[-547] XOR untemper(recorder_seq44.control)) AND 0x7FFFFFFF = 0x7206E905`. Thus sequence44 cannot occupy -547 under this p951 state reconstruction. The **constant-seven-draw schedule across seq41..45 is falsified**, although the two endpoints both genuinely match their stated conditional indices. Reproduce using [source-pinned single-file test](../agents/agent30/k04_p951_seven_draw_holdout_sft.py). It loads the current Agent 2 source-only closure, checks original recorder SHA256 and CRC, verifies endpoints before inspecting heldout seq44, and asserts the discrepancy.

An apparently matching seven-draw span also exists from **seq7 at -810** to **seq12 at -775**. Its proposed intermediate seq8..11 positions **-803, -796, -789, -782** have **zero independently fixed printer bits**, so they provide no heldout support for a constant schedule. This is an important control against promoting a coincidental endpoint difference into a producer rule.

## Interpretation and next possible crack

The proposed fixed-rate schedule is inconsistent with the original source geometry; a surviving **variable-draw** or sequence-dependent rejection model would require a separately justified consumption rule and new heldout predictions. The recently proposed [Agent3 13-bit AUX rejection model](h17-k04-p951-trp2-aux13-nextword-bridge.md) suggests one possible variable-consumption mechanism, but it is itself historically unverified and cannot erase the seq44 contradiction by arbitrary skips. At -548 and -542/-541 (nearby well-constrained state positions), the original seq44 control also disagrees with 17, 19 and 16 bits respectively; this is a local discriminator, not an exhaustive variable-schedule rejection.

The original spool, recorder, route mask, selected K04 ACK, acceptance hashes and verifier remain unmodified. The source chronology is retrospectively selected and not proven historical firmware. Even after this test, selected p951 K04 words 951..954 have **zero individually fixed bits**. The six accepted REC8 slots remain verified, K04/K08 absent, combined recovery **INCOMPLETE**.
