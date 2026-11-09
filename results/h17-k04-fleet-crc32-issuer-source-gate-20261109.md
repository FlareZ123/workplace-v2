# K04: source-paired reversible CRC printer issuer from north/south cassette ticket sets

**Agent17 | 9 November 2026 | New complete-coupon source mechanism, no original K04 acceptance hit.** Six accepted components remain valid. Historical K04/K08 unresolved.

## Why this model reaches an actual complete K04

The original 4 October L-29 fleet return register pairs selected **ESC-N / job PS-261003-0417** with five north service tickets **ST-094/081/106/099/112**, and preserved **ESC-S / job PS-261003-0448** with south **ST-130/151/121/135/142**. The latter has an original 18:24 RECOVER ACK full 16-byte packet, **234BE186E97EE05830909790E336109E**, in the original printer buffer. Could a paper/firmware issuer turn cassette tickets into four checksum words, using unknown shared printer initialization? If so the observed south object can reveal a complete north coupon without trusting the disputed 18:02 north payload.

This is a speculative causal issuer, not a source-attested physical writer. Crucially it is different from the previously exhausted ticket-to-MD5/SHA/HMAC masks and same-role CPython seed dictionaries: it models **four genuine 32-bit CRC register outputs** rather than a truncated cryptographic hash, and inverts an **unknown common CRC initialization state** from the complete south sample.

## Two source-calibrated reconstruction variants

1. **Unknown 128-bit shared XOR pad + CRC32 message mask.** If \`coupon_lane = U XOR F(ticket_metadata)\`, where F is four concatenated zlib/IEEE CRC32 outputs with source-chosen lane salting, the unknown U cancels between southern and northern job. In equal-length source representations, each complete proposed north coupon is \`south XOR F(S) XOR F(N)\`, immediately converted to K04 by XORing the unchanged official route mask. This is a new **CRC32 mask family**, distinct in output from prior cryptographic F choices.
2. **Unknown *common 32-bit* CRC initialization seed, exactly recoverable.** In a printer that uses the *same hidden CRC register initialization* to generate four counter/lane-salted checksum words, **one known south output lane uniquely reveals the entire secret 32-bit initial register**. Reverse the conventional reflected CRC bit recurrence, including the byte-fed input, then require the other **three entire south output lanes** to independently yield the *identical seed*. Every source-passing scheme predicts the complete northern physical coupon, even when north/south input lengths differ. Two standard printer-relevant CRC polynomials were tested separately: IEEE reflected 0xEDB88320 and CRC32C Castagnoli reflected 0x82F63B78.

For each north/south pair use six representations of the five original ST ticket numbers (full, 3digit, decimal integer, uint8, uint16BE/LE), five separators, seven complete original route/job/account metadata layouts, eight four-lane counter/position salts, two 32-bit byte endians and four whole-packet byte/word views. The same model is applied to both originals, with no selected K04 copied ACK2 input and no target hash during southern seed fitting.

## Original source results

| Original-source test | Source-model assignments | Complete surviving objects | Original K04 matches |
|---|---:|---:|---:|
| Shared unknown XOR pad, IEEE CRC32 ticket issuer, equal-length paired strings | **11,200** | **1,060 distinct K04 component candidates** | **0** |
| Common recoverable CRC32 IEEE seed, four independent southern lane controls | **13,440** | **0 complete south four-lane fits** | none admitted |
| Common recoverable CRC32C seed, four independent southern lane controls | **13,440** | **0 complete south four-lane fits** | none admitted |

The 1,060 count is deduplicated **final K04 values**, whereas 11,200 counts model assignments. Normal CRC32 bitwise linearity causes many equivalent pads/serializations. The original south packet is tested as an entire 128-bit object in both common-seed families, rather than drawing target hash-driven conclusions from an arbitrary first fourbyte lane.

**Positive complete controls:** independently generated authentic CRC32 and CRC32C four-lane south packets with a hidden nonzero 32-bit initialization correctly recover the exact original seed from *all four* individual words and the withheld complete northern 16-byte output. An independent shared-secret 128-bit XOR pad + CRC32 north/south simulated issuer also recovers the exact withheld original-format north 16 bytes. All assertions PASS. The actual 46-file attached original source was executed unchanged with the exact counts above.

## Consequence

This is a new device-metadata recovery pathway, but the originals do not substantiate it. The unproven possibility that surviving southern copied bytes differ from the original paper also limits falsification. The five October 4 binder ticket numbers may have been recorded *after* October 3 printer generation and never used by firmware. Therefore no complete historical K04 or authenticated selected coupon bit has been recovered. Do not enlarge speculative CRC salts without a real printer-issuer relation.

**Reproducer:** [source-pinned standard-library SFT](../agents/agent17/k04_fleet_crc_source_sft.py), requiring only original repository \`resources/evidence\`, original mask and full K04 commitment. Fleet SHA256 \`10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf\`; spool SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`. The verifier and canonical candidate are not edited.

REC8/1 remains six individually accepted slots, K04 and K08 MISSING, combined INCOMPLETE.
