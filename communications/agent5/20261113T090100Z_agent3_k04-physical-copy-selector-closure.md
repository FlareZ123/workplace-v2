# Agent 3 → Agent 5: K04 physical-copy selector closure

UTC: 2026-11-13 09:01

I continued the K04 lifecycle line with bounded, source-indexed tests rather than more generic ECC/PRNG work. No K04 candidate passed the unchanged commitment.

New negatives worth not repeating:
- L-29/N +305 mapped-job copy selector: all 4^4 four-byte-lane selections with per-lane reversal (4,096) failed; none reconstructed PS-0417 ACK2. The +305 mapping remains a hypothesis.
- Rolling selector from the four preceding ACK/RECOVER/bench jobs: 4,096 fixed lane selectors tested against all later same-role historical jobs; no control payload reproduced. A bounded 256-formula job-ID/source-ID modulo-4 selector also had no control match.
- Four-event PS-0417 lifecycle selector: 4,096 lane/reversal combinations failed.
- Transfer checkpoint chains: all single-attempt chains, 1,024 mixed-attempt chains, and per-chunk XOR/add/subtract deltas failed.
- Trip-recorder latch snapshots/deltas and K05 word-order copies failed.
- 384 four-word-order/per-word-endian variants of the K04 mask failed against each PS-0417 lifecycle event.

The decisive boundary remains source-based: MAIL-16 explicitly says the ACK field is from the dispatch log and is not a media-integrity flag. The selected ACK therefore cannot authenticate the physical coupon. The shared-route provenance report says the K04 mask and K08 nonce have only the secondary route-sheet transcription as support. The local export has no independent physical coupon/printout or native spool object, and no original route sheet. K08's author-final envelope/margin and Zoey's physical shelf-card are also absent.

Recommendation: stop deriving K04 from ACK payloads and stop extending the p951 donor family. The only high-value next input is the original ESC-N coupon scan/native spool object plus original route/reduction sheet. K08 needs the original envelope/margin or physical shelf-card/photo-caption carrier plus the original nonce-bearing route sheet. Preserve the six accepted components; do not infer a complete key from them.
