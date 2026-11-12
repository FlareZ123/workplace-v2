# K04 whole-object stage-discriminator test (2026-11-12)

**Owner:** Agent 6  
**Question:** Can a retained, complete non-target spool object—with its selector and 16-byte payload—distinguish the candidate native-MT stage for the selected PS-261003-0417 ACK2 record (950, 951, or 952)?

## Method

Reused the source-derived MT19937 symbolic model and stage-shift groups in `agents/agent49/k04_p951_symbolic_basis.py` and the late-component quotient work. The target is spool row 129 (zero-based): `PS-261003-0417 / ATTEMPT=2 / STATE=ACK / CLASS=RECOVER / DEST=bench`.

The late-Z tail is rows 128–132. Tested the strongest simple cohort hypothesis: these five 16-byte records are consecutive four-word MT blocks, so their starts are `q-4, q, q+4, q+8, q+12`, with `q ∈ {950,951,952}`. For each candidate geometry, rebuilt the affine source basis while withholding the target and then withholding whole non-target records. A withheld word bit counts as fixed only when its linear form reduces to a constant under the remaining source equations. Fixed bits were checked against the actual withheld payload.

This is a holdout test of whole objects, not a claim that cohort contiguity is historically proven.

## Results

- With all five late-Z payloads withheld, six source-consistent schedules survive: one with `q=950`, two with `q=951`, and three with `q=952`. All three candidate stages remain.
- The closest selector peer is row 132, `PS-261003-0420 / WATCH-SPARE / ATTEMPT=2 / STATE=ACK / CLASS=RECOVER / DEST=bench`. With row 132 and target row 129 both withheld, the remaining source fixes **63/128 bits** of row 132 in every surviving schedule. Every fixed bit matches the retained payload; the fixed projection is the same for all three q values. It does not select a stage.
- The adjacent ESC-S object (row 131, `PS-261003-0448 / ATTEMPT=1 / STATE=ACK / CLASS=RECOVER / DEST=desk`) yields **64/128** fixed bits, all matching, with no q discrimination.
- The same-job REQUESTED controls yield **63/128** fixed bits for row 128 (attempt 1) and **31/128** for row 130 (attempt 3), again matching but not distinguishing q.
- Earlier whole-object controls near the two-gap donor locations also fail to discriminate: row 44 and row 96 each give 95/128 fixed bits; row 66 gives 127/128; the physically referenced spare-label row 121 gives 63/128. The fixed projections match across the surviving q schedules.
- The selected row 129 remains **0/128 fixed bits** under the source equations. Excluding the two REQUESTED payloads from the equations does not change that result.

## Conclusion

The retained whole-object controls tested here do **not** distinguish stages 950, 951, and 952. In particular, the only other record with the target's `RECOVER/ACK/2/bench` selector is the explicitly unrelated WATCH-SPARE job; its payload supplies a useful partial control, not an absolute phase anchor.

Do not promote p951 or the conditional two-gap pair (328, 724) to a recovered component. The remaining ambiguity is an absolute one-word phase across the late cohort, while the selected 128-bit block remains unconstrained. A source-backed discriminator would need an independently anchored native word/buffer offset, an authenticated original coupon payload, or an equally direct printer-side record. Further permutations of the same retained payloads cannot supply that missing anchor.

## Reproduction notes

The source equations are the 32-bit untemper equations for each intact 16-byte payload at its candidate four-word start. For each schedule, insert all four lane equations for every included row into the existing GF(2) basis; reduce each held-out lane's 32 bit forms against that basis; count constant forms and compare their constants to the untempered held-out word. The cohort constraint and row identities above fully specify the finite test. Existing basis and stage definitions are linked above; no new PRNG or seed assumption is introduced.
