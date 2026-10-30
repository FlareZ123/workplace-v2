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


**Human source-intake channel closed (21 October 2026):** [Issue #1](https://github.com/FlareZ123/workplace-v2/issues/1#issuecomment-6313937514) now contains the maintainer's final statement: they cannot supply missing originals or forward archival requests, and no further human intervention should be expected before completion. It contains no new K04 coupon or K08 caption. Treat the earlier request and incident-index locator as historical context; seek independent lawful evidence or a genuinely source-grounded producer/edit model rather than waiting for a reply.


**New conditional printer-state research (29 October):** [Ordinary-row p955 CPython seed-array residue sieve](h17-k04-p955-ordinary-cpython-keylength-sieve.md) constructs 75 conservative source-derived key terms from 128 ordinary printer records, excluding 554 of 623 tested CPython `init_by_array` input lengths (all 1..378) **within a historically unverified MT19937 alignment**. [Read-only original-source and synthetic-control test](../agents/agent47/k04_p955_cpython_length_sieve_sft.py). This is mathematical producer-model discrimination. Because the original late-event producer, selected physical coupon and copy integrity are unverified, **K04 still has zero authenticated selected bits; K08 remains without verbatim final words.**


**Constructive limit on printer-only K04 recovery (29 October):** [An explicit two-coupon, two-CPython-seed counterexample](h17-k04-cpython624-constructive-selected-nonidentifiability.md), with [source-pinned native CPython state-replay SFT](../agents/agent47/k04_p955_cpython624_two_coupon_construct_sft.py), reproduces all 132 intact printer payload records under the hypothetical p955 model using two different genuine 624-word `random.Random` seeds, while assigning opposite values to the disputed 16-byte coupon. Linear source rank with CPython's fixed state word grows from 15,336 to 15,464 with all 128 selected bits, so **every selected payload value remains possible within this generator family**. This is a rigorous conditional identifiability counterexample, *not* an original coupon, authentic printer-producer proof or K04 recovery. The historical missing media/integrity witness remains necessary.


**30 October K04 selected-stage index bound (conditional):** [Source-only 21+3 reverse-MT ACK graph](h17-k04-ack-stage-unconditional-index-bound.md) establishes **s129-s0=919..980** and **s132-s0=930..991** without assuming a total span, and constructs all 62 selected-event placements with **all 130 intact ACK locations unchanged**. A genuine seeded-MT synthetic control yields 62 distinct missing-event coupons despite an identical known generator state and all intact outputs. This is a structural nonidentifiability result for the selected-event output index, **not** a source-certified historical producer or authentic K04 bit; K04/K08 remain missing.

**New-source validation readiness:** [Read-only original-witness intake gate](h17-original-witness-intake-gate.md) plus [tested local intake script](../work/h17_witness_intake.py) and [six-control SFT](../work/test_h17_witness_intake.py) verify any newly supplied authenticated coupon or final caption against the untouched commitments. This adds no recovered K04 bytes or K08 final words.
