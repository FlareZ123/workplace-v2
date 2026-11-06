# K04 p951 MT model: full-packet leave-one-out benchmark

**Agent 32 | 6 November 2026 | source-only conditional benchmark**

## Question

Can the conditional p951 MT19937 printer model reconstruct an entire original 16-byte printer packet when that packet is withheld, while the disputed selected 0417 row129 remains withheld from every fit?

This directly tests whole-object predictive ability. It is stricter than validating individual CONTROL bits or fitting the selected packet itself.

## Method

- Pin the original `resources/evidence/print/spool-reconstruction.log` SHA256 to `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Freeze the 133-entry native-stage map from [Agent49's p951 symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py); its selected row129 stage is 951.
- Exclude selected row129 from every fit. The SFT does not capture, decode, or retain row129's `PAYLOAD` field.
- For each of the other 132 original packets, withhold that complete 16-byte packet and fit the linear MT19937 basis from the remaining 131 packets.
- Predict each of the withheld packet's 128 tempered output bits. Count only bits that are fully fixed by the remaining source equations, and compare those predictions with the withheld original packet.
- Run deterministic synthetic MT19937 positive controls at rows 12, 131 and 132 to validate the linear prediction implementation.
- Do not read the K04 mask, K04 slot commitment, or acceptance verifier.

The reproducible single-file SFT is [`k04_p951_leave_one_packet_out_sft.py`](../agents/agent32/k04_p951_leave_one_packet_out_sft.py).

## Results

<badge color="warning">No complete packet reconstructed</badge>

Across all 132 leave-one-packet-out trials, **zero** withheld packets had all 128 bits fixed. Every bit that the model did fix matched the original heldout value: **0 incorrect fixed bits**.

| Fixed bits in withheld packet | Number of packets |
|---:|---:|
| 0 | 62 |
| 26 | 15 |
| 32 | 4 |
| 58 | 22 |
| 64 | 12 |
| 90 | 11 |
| 96 | 1 |
| 122 | 5 |
| **128** | **0** |

The strongest partial predictions were 122/128 bits for rows 12, 41, 66, 95 and 125. No complete 16-byte prediction was obtained.

### Same-role RECOVER ACK controls

| Withheld packet | Native stage | Fixed bits | Lane fixed-bit counts | Incorrect fixed bits |
|---|---:|---:|---|---:|
| PS-261003-0448, attempt 1, row 131 | 959 | 64/128 | 32, 32, 0, 0 | 0 |
| PS-261003-0420, attempt 2, row 132 | 963 | 58/128 | 0, 0, 26, 32 | 0 |

Both are original RECOVER ACK packets, the same broad packet role as the selected 0417 ACK2. Neither is reconstructed as a complete object.

### Selected target shape

With all 132 nonselected original packets in the basis, selected row129 at stage951 has **0/128 fixed bits**. The source model therefore supplies no complete or partial selected-coupon bytes from the printer packets alone.

The synthetic controls reproduce the same fixed-bit counts at the three tested rows and have zero incorrect fixed bits. This validates the SFT's linear algebra and bit accounting; it does not validate the historical firmware hypothesis.

## Interpretation and limit

This is a **conditional test of the frozen p951 stage map**, not proof that the printer historically used this MT19937 stream. It establishes that, under the existing p951 hypothesis, the original packet corpus cannot independently predict even one complete 16-byte packet under one-packet missingness. The two same-role controls retain 64 and 58 unknown bits respectively. A ranked full-packet candidate stream would therefore require an additional source-derived selection rule; assigning arbitrary values to those free bits would manufacture evidence.

This does not contradict Agent16's 113/113 recorder CONTROL-bit holdout. That experiment validates four 32-bit CONTROL words under metadata-first stage selection. This experiment asks whether the same printer basis can recover an entire 128-bit printer packet.

**Research consequence:** stop treating p951 partial-bit or recorder CONTROL agreement as a whole-coupon reconstruction path. Further work on K04 needs an independently anchored physical/copy boundary or a new source constraint that predicts a complete selected object. Do not spend more compute on larger p951 target-hash lists without such a constraint.

**Status:** K04 remains unresolved. K08 remains unresolved. No acceptance component or original evidence was modified.
