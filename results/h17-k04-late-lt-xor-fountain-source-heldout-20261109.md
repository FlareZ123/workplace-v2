# K04: late RECOVER XOR-fountain whole-object producer and withheld route control

**Agent 30 | 9 November 2026 | Original full-coupon test, K04 still missing.**

## Distinct physical/producer mechanism

The original spool contains exactly 128 ordinary ACK attempt-1 packets at job IDs PS-261003-0300..0427, followed by three different late acknowledged RECOVER-route objects. This motivates a speculative *fountain* copier rather than an unknown stream-state or arbitrary correction of the suspect north ACK: each late 16-byte coupon is an XOR subset of the prior 128 complete 16-byte ordinary payloads. Metadata for that late job selects the subset. A single unknown 16-byte fixed XOR relay/copy pad is eliminated using a complete physical-route source anchor.

MAIL-16 expressly calls WATCH-SPARE an unrelated spare. The tested shared-pad/issuer bridge between its buffer, ESC-S, and ESC-N is therefore a falsifiable **exploratory coupling assumption**, with no claimed physical common-issuer authentication. A whole-packet WATCH mismatch rejects the shared-issuer model under faithful copied buffers, while remaining compatible with genuinely independent route producers or additional copy damage.

The proposed issuer is not historically specified. It is a source-to-complete-object alternative to the already failed systematic RS(128+5) and keyed three-route HMAC producer families. It does not depend on the disputed north copied ACK bytes.

## Freeze, calibration and test

- Original printer spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- The 128 ordinary packet payloads are selected strictly by signed job ID, first acknowledged attempt, and original order. All source bytes remain unchanged.
- **Calibration:** ESC-S, PS-261003-0448, RECOVER ACK1, 18:24 UTC, retained complete payload `234BE186E97EE05830909790E336109E`. Infer `pad = observed_south XOR issuer_south`.
- **Independent blind whole-packet control:** WATCH-SPARE, PS-261003-0420, RECOVER ACK2, 18:25 UTC, original copied payload `432475F72A62DB39F3D5693E2C937FA4`. Predict all 16 bytes before using the target commitment.
- **Target:** ESC-N, PS-261003-0417, RECOVER ACK2, 18:02 UTC. Predict the full hypothetical original 16-byte north coupon, XOR with original `8556C8CB6140A7F9A5123AC7571BEE1C` mask, and check original K04 SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The copied selected ACK2 payload is used solely as a parsing selector/sanity check; its bytes do not enter any predicted coupon.

For each route, source metadata seeds one of four named hashes and SHAKE256-defined packet priorities. Nine subset rules are eight fixed degrees (1,2,4,8,16,32,64,128) plus a 128-bit inclusion-mask rule. The frozen complete family contains **4 byte/word layouts × 2 row orders × 8 metadata serializations × 8 domain prefixes × 4 digest choices × 9 subset rules = 18,432 models**.

## Actual original result

| Independent criterion | Original result |
| --- | ---: |
| Fully specified complete-coupon model candidates | **18,432** |
| Exact 16-byte independent WATCH-SPARE predictions | **0** |
| Maximum identical positions in WATCH-SPARE across tested models | **2 bytes** |
| Exact original K04 256-bit commitment hits | **0** |
| Planted full synthetic WATCH-SPARE and north-coupon reconstruction | **PASS** |

The planted control uses one nontrivial combination of subset selector, input layout and ordering, a separate known synthetic 128-bit pad, and a synthetic K04 acceptance digest; it checks the exact same inference, full coupon and mask path as the original case. Original source bytes, original commitments, candidate file and original verifier were not modified.

**Scope:** This excludes the stated 18,432 deterministic source-metadata-seeded LT/XOR subset plus one shared fixed pad models only. A historical shared fountain issuer has not been authenticated; the source heldout explicitly contradicts every specified combination. Unknown different coding distributions, source stages, route-dependent pads, or separate physical-copy failures remain outside this test. No K04 bits and no K08 words have been recovered. All six previously accepted slots remain PASS, K04/K08 MISSING, combined REC8 INCOMPLETE.

**Executable portable SFT:** [Agent 30 late fountain code](../agents/agent30/k04_late_lt_fountain_sft.py). Runs against repository resources by default or the original ZIP path explicitly.
