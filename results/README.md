# H-17 incident archive recovery

**Six of eight REC8/1 components** have passed the unmodified official slot verifier; K04 and K08 remain unresolved, so combined acceptance is **INCOMPLETE**.

| Slot | Verified component | Primary evidence |
|---|---|---|
| K01 | `049AAB2E1CDE7A82CD7C60234303C91A` | signed WN-14, mail 03, 06, 14 |
| K02 | `0D7E3AB56FB75DA3EB0E2E06786D239E` | LT-204 GOOD/HOLD UTC filter, greatest revision per seq |
| K03 | `1384AF96E25D6ADA666209CB55E062FA` | signed PTW-417 CLOSED AS_LEFT, bay B,D,A,C |
| K04 | **missing** | ESC-N printer job PS-261003-0417 has unverified ACK payload |
| K05 | `FF8B78200A56E8586DCDA00EF01E4572` | TRP2 valid CRC, greatest seq per latch |
| K06 | `5DBF40EE52FAAED9A536D3326CF0D95A` | RC-17 revision C, DRAIN/ISOLATE/PURGE/VERIFY |
| K07 | `93495F5E425AB8E592123DABAEB68545` | AX-7782 transfer, greatest retry attempts |
| K08 | **missing** | final keeper caption absent from supplied drafts |

**Cross-repo research gate:** [Extensive 180+ prior H-17 reports in workplace-v1 and exact source-byte comparison](h17-v1-prior-art-gate.md). **K04 exact three-byte mutation search was already exhausted twice in v1**; every contiguous four-byte replacement window (13 × 2^32 assignments) and the repeated four-byte XOR lane model (2^32 deltas) have also been exhausted there with no match. Duplicate v2 CI was cancelled. Future K04/K08 work should be informed by the v1 target-information frontier.

Detailed evidence from current repository:
- [Six-slot recovery status with corrected prior-art bounds](h17-recovery-status.md).
- [New K04/K08 evidence including decrypted supplementary PDF provenance](h17-six-pass-and-open-slots.md).
- [Partial accepted candidate](../resources/candidate.json) and [reproducible offline reducer](../resources/work/recover_six.py).

For a source-specific records request, see [missing evidence and historical incident index locator](h17-missing-evidence-request.md).

Priority: obtain authentic K04 spool payload bytes and the exact K08 keeper caption, avoiding repeated verification of six solved slots.

**Cracking allocation gate (20 Oct 13:22 UTC):** [Critic target-information budget](../communications/broadcast/20261020T132243Z_Critic_target-information-budget.md) requires a new source observation, withheld intact-source prediction and actual target-space reduction *before* further unsupported radius/phrase/seed sweeps. This is a work-priority rule; the six-pass/two-missing status is unchanged. A SHA-256 commitment verifies guesses but does not reconstruct arbitrary missing material.

Original-source provenance: [Uploaded ZIP versus live repository exact tree/blob integrity](h17-attached-zip-integrity.md) (46 files identical, including the entire 42-file evidence tree); reproducible [read-only comparison tool](../work/h17_source_integrity.py). No new K04/K08 target-bearing bytes were supplied by this copy. A bounded [literal-carrier audit of the four later-added office members and decrypted BX25/08 text/stream](h17-supplement-original-carrier-audit.md) tested **14,927 raw byte windows, 648 ASCII-hex windows and 103,800 normalized 1–40-word spans**, including synthetic controls; zero authentic missing-slot commitment hits. This extends the predecessor's original pre-supplement scan in the stated extraction classes and **does not recover coupon bits or caption words**. An [independent audit of the ZIP container bytes](h17-zip-container-channel-audit.md), with [eight tamper-detection positive controls](../work/test_h17_zip_container_audit.py), found no hidden free-standing ZIP payload, mismatched local/central metadata or unexplained byte regions. The packaging-level negative does not establish that omitted original coupons or keeper words never existed.

**Custodian source intake:** [Issue #1](https://github.com/FlareZ123/workplace-v2/issues/1) requests the exact original K04 coupon/integrity witness and final K08 desk-margin wording, with the historical missing incident-index path.

**New-source validation readiness:** [Read-only original-witness intake gate](h17-original-witness-intake-gate.md) plus [tested local intake script](../work/h17_witness_intake.py) and [six-control SFT](../work/test_h17_witness_intake.py) verify any newly supplied authenticated coupon or final caption against the untouched commitments. This adds no recovered K04 bytes or K08 final words.
