# H-17: source-paired record-ID hash issuer and revision-operator tests

**Agent 6 | 4 November 2026.** Three new, finite source-to-complete-candidate pilots deliberately avoid further arbitrary corrections of the disputed ACK2 bytes. Original source, route, candidate, acceptance and verifier were not edited. All original K04 SHA queries use the unmodified recorded commitment. These are **conditional exclusions of explicitly enumerated mechanisms**, with **no recovered K04 physical-coupon bit or K08 exact terminal word**.

[Reproducible original-source single-file SFT](../agents/agent6/k04_crossarchive_recordid_retry_bridge_sft.py).

## 1. Test a document-authoring digest bridge on 27 matched permit/job IDs

An original maintenance receipt exists for every PTW-390 through PTW-416. Each has one 32-bit SG serial and one same-number printer packet PS-261003-0390 through -0416. Numerical matching is an **observation**, not proof of a common writer. The nearest previous test, [Agent 8's per-bay reversible-word encoder](h17-k04-ptw-printer-matched-id-bay-affine-source-holdouts-20261104.md), addressed direct 32-bit encodings. This experiment instead asks whether an emitted 128-bit printer packet was a truncated **hash of its 32-bit permit serial and public event identity, plus a shared full-block pad**.

Finite model grid:

- 4 serial representations: 4 raw bytes big or little endian, eight ASCII hex characters, full `SG-XXXXXXXX` label.
- 8 event contexts: none, permit ID, print job ID, decimal ID, bay, CLASS/DEST, permit/bay, job/CLASS/DEST.
- Both source/context concatenation orders; three delimiters (none, pipe, LF).
- Eight 128-bit digests: SHA256 first/last, SHA512 first/last, BLAKE2s-128, BLAKE2b-128, MD5, SHAKE256-128.
- Transform `P=H(m) XOR pad` or `P=H(m)+pad (mod 2^128)`; `pad` either globally common or one pad per bay.

**6,144 complete-model assignments.** Each fits its first original observation exactly by construction; then predicts **all remaining 26** original full 16-byte packets for global-pad models, or **23** for bay-pad models. **Zero exact held-out full-packet predictions**. A planted SHA256+global-XOR original family recovers its mask from one source observation and predicts all 26 source controls.

This falsifies the enumerated shared-pad digest writers on matched historical controls. It cannot falsify a completely different label serializer, record-specific secret pad, selected-only issuer, or actual printer physics. None of these unsupported issuer models was applied to manufacture a 0417 coupon.

Original SHA256 pins: `print/spool-reconstruction.log` = `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; `maintenance/seal-receipts.jsonl` = `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`.

## 2. Selected-source 16-bit retry and revision operators

Original sources preserve **eight genuine old/new 16-bit word pairs** for K02 LT-204 GOOD/HOLD DIAG_WORD within the route's eight-second UTC window, and **eight genuine attempt1/attempt2 checkpoint pairs** for the actually selected K07 transfer AX-7782. Unlike the earlier cross-domain [16-byte K05/K06/K07/printer affine pilot](h17-k04-crossdomain-version-postselection-20261104.md), these are same-role within-carrier field revisions.

For each carrier independently, train `new = f(old) XOR pad` or `new = f(old)+pad (mod 2^16)` on only sequence 0. The 33 specified `f` transforms are identity, byte-swap, bitwise complement, and all 1..15 rotations in both directions. Orient old/new words independently. **528 fitted models, each tested against seven held-out original revision/attempt words: zero individual 16-bit exact predictions.** A planted single-operation history passes all seven.

An additional cross-carrier index-specific hypothesis `delta_K07[i] = rol16(delta_K02[i],k) XOR pad`, where `delta=old XOR new`, was trained on sequence 0 for all 16 rotations. **Zero of 112 held-out word comparisons matched**. Fitting an integer-ring affine `new = a*old+b (mod 2^16)` to the first two pairs has **one admissible exact-fitting model per carrier**, and **zero predictions of the six held-out original words** in either. A planted affine history passes.

These results reject the specified uniform retry/version operators as a reliable bridge to the missing same-job ACK2. They do not rule out a job-specific change or an unobserved error mechanism in the copied physical coupon.

Original pins: `telemetry/freeze-export.jsonl` = `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`; `transfers/transfer-audit.jsonl` = `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`.

## 3. Direct complete-coupon construction from same-number PTW-417 serials

As a separate, **low-confidence cross-record transfer hypothesis**, take every **ordered four-distinct** tuple among the 17 original PTW-417 serial revisions, under common original/reversed byte order. Interpret those sixteen source bytes as the escrow coupon and apply the official K04 XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C`. The immutable K04 SHA256 rejects **all `17P4 × 2 = 114,240` complete original component assignments**. An independent synthetic chosen tuple is recovered exactly once by the identical source-and-mask pipeline. This test differs from [Agent 8's source-conditioned MT stage placement of the 17 serials](h17-k04-ptw417-17serial-mt-coupon-target-rank-first-source-falsifier-20261104.md), and makes no claim that same numeric ID proves physical coupon copying.

### Decision

Across the frozen issuer, revision and simple four-source-block mechanisms, there is **no new accepted component** and no basis to promote arbitrary selected physical bits. The exact printer 0417 last ACK selector remains as specified, while the copied byte-level value still fails official K04. Next genuinely target-facing work should explain an independently observed full-block writer or transport step before promoting its predicted selected coupon. For K08 the unquoted Emily author-final margin remains a separate unresolved literal source.

**Official outcome unchanged:** K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE, `accepted=false`.
