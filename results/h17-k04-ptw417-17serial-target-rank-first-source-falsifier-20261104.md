# H-17: original PTW417 17-serial MT stages cannot recover K04 under target-informative layouts

**Agent 8 | 4 November 2026 | Source-only original falsifier plus complete synthetic-coupon positive.**

## Precise target-bearing question

The original `resources/evidence/maintenance/seal-receipts.jsonl` contains **17 distinct PTW-417 revision records**, including selected signed as-left B,D,A,C seal serials used for accepted K03. Each serial is 32 bits. The printer's selected physical K04 16-byte coupon is missing. Could the entire original 17-serial sequence give **state-determining source equations** for the previously studied *conditional p951 MT19937 printer producer*, thereby reconstructing the unknown K04 coupon without using the unreliable copied ACK?

The printer basis uses the exact 132 genuine intact full-packet records **with selected row129 withheld**, as defined in [Agent49's source model](../agents/agent49/k04_p951_symbolic_basis.py). Its rank is 15,365. The selected coupon in this mathematical geometry consists of native word stages 951..954. No historical record authenticates this shared-producer assumption or the PTW-to-PRNG stage numbering.

## Frozen source-stage mechanisms

Sort **all 17** original PTW417 entries by either `(revision,bay)` or `(bay,revision)`, forward or reverse. Test each opaque 32-bit serial in big-endian and little-endian views, interpreted as either **native** or **standard MT-tempered** output. Hypothesize 17 equally spaced stages beginning at any integer **650..950**, stride **1..8**, constrained to the existing symbolic model's latest stage1040.

First perform exact GF(2) rank algebra without consulting PTW417 serial bytes. **499 stage/stride geometries** would constrain at least one previously undetermined K04 native bit (coupon quotient fewer than 128). Their detailed anatomy matters:

- **382 / 499** geometries place at least one purported PTW serial at one of the *four selected coupon stages themselves*, giving direct symbol overlap; some place all four and trivially reduce quotient to zero. This mathematical overlap supplies no original authenticity.
- **117 / 499** geometries do **not** overlap coupon stages. All 117 constrain only **one** of 128 K04 native degrees of freedom (quotient 127). No nonoverlap layout in this frozen family predicts the complete coupon from these records.

Only these 499 *mathematically target-informative* stage geometries proceed to original serial compatibility. Applying 2 genuine record sort orders × 2 directions × 2 endian views × 2 native/tempered interpretations gives **7,984 complete original-source assignment models**. Exact incremental GF(2) elimination enforces every retained original printer bit plus each actual PTW serial bit.

**All 7,984 models contradict the genuine retained source. Zero are compatible.** Contradictory models are stopped on the first inconsistency. Neither a partial coupon bit nor a complete key was authenticated.

## Full 128-bit synthetic positive

To rule out an algebra/inversion implementation failure, solve the real original printer rank15,365 equations for a particular full 19,968-bit initial MT register, with all free variables set to zero and each pivot satisfied exactly. Generate **17 planted genuine MT-tempered serials** from native stages938..954 of that same source-compatible full register. Apply the exact source insertion using those serials, reconstruct four native selected coupon words951..954 by the augmented GF(2) basis, and compare all **128 bits** to their independent generated values. **PASS**. The positive deliberately includes direct stage overlap to prove the fully reconstructible branch, not to claim the original PTW417 ever used that stage.

Original evidence pins: printer log SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; seal receipt log SHA256 `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`.

[Reproducible single-file Python SFT](../agents/agent8/k04_ptw417_17serial_mt_coupon_target_sft.py), imports only the existing Agent49 symbolic model and standard library. Executed locally against original uploaded 46-member ZIP. Committed Git blob was verified byte-identical to the tested script (SHA1 `eec73456a4e6c0a7dfbce5b59046d42957c08211`).

## Interpretation

This is a **new target-rank-first test of all 17 same-permit revisions**, different from Agent46's earlier three original serial anchors, restricted Bay rejection rule and PTW416 source falsifier. It conditionally explores a complete-coupon-reachable stage overlap before applying any original K04 SHA256. Its strong synthetic positive and original-source contradiction distinguish actual historical evidence from a mathematically possible invented state.

The broad negative is conditional on p951's **unproven** producer, the two specified source orderings and equal stage stride1..8, start650..950. Unobserved generators, irregular stage consumption, different historical seed streams or genuine physical spool media lie outside the claim. The original selected coupon remains entirely unknown, and K08 author's exact keeper-final margin remains missing. Original six slots PASS, K04/K08 MISSING, combined REC8/1 INCOMPLETE. Original verifier, evidence, mask, acceptance and candidate have not been changed.