# K04: extended speculative future-stage replay coupons, 3 November 2026

**Agent 11. Original K04 target still NO_MATCH.** This is a bounded complete-candidate test under the *hypothetical* p951 shared MT19937 producer and an additional *hypothetical* later-stage copy/replay relation. It does not authenticate physical printer firmware or the selected coupon.

## Distinct question

Agent50's six-geometry relocation study tested MT output stages **-1100..1037** as alternative locations for a fully generated selected coupon, with no commitment hit. Under a precomputed pool / deferred copy architecture, could the selected ESC-N coupon have been copied from a **later four-output stage** outside that scan? This is materially different from donor-word matching: reconstruct the *entire four-word candidate coupon at the proposed copy origin*, XOR the unchanged original K04 mask, and test the original SHA256.

The exact search in this investigation covers four-word native MT window starts **1038..5300 inclusive**, 4,263 windows per source model. The selected original spool row129, original K04 copied ACK payload, and K04 acceptance are excluded from the state fit. This does **not** claim that the original records document a future-stage copy.

## Original observations and independent cross-carrier conditions

- Original intact printer 132 packets, hypothetical published p951 starts, 528 observed four-byte little-endian tempered MT words. GF(2) original spool rank **15,365**.
- AX-7778 16 original checkpoint halfwords, sorted by (seq, attempt), byte-swapped and modeled as the upper16 tempered bits at native **-157..-142** (Agent50's *source-selective but not historically authenticated* cross-carrier stage). Joint rank printer+AX **15,495**.
- Node49 event82 TRP2 archive latch CONTROL words, original source cohort seq200..203, seq900..903, seq990..993, modeled by the 3-output per-latch grid at native **-324..-313**. Of these twelve originals, the seq900 cohort fails source CRC and can only serve as explicitly labelled **auxiliary hypothetical raw observations**.
- Printer+CRC-valid node49: rank **15,432**. Printer+AX+CRC-valid node49: **15,561**. Printer+AX+all twelve raw node49: **15,622**. All tested source constraints are mutually consistent in this assumed alignment. In all five models the omitted *actual* stage951 coupon retains the complete **128-bit source quotient**, despite the additional constraints.

Source SHA-256 pins:
- spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- AX transfers `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`
- TRP2 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`.

## Exact enumeration

For every candidate four-word window, project its 128 native output bits onto the intact original-source GF(2) quotient. If the window has residual rank ≤3, enumerate all `2^rank` complete 16-byte packets through MT tempering. For every generated packet, independently test the direct native layout and all **24 word permutations × 16 per-word byte-reversal masks = 384** alternative layouts. XOR each possible 16-byte coupon with the **unchanged** original K04 mask and compare its SHA-256 against the **unchanged** K04 slot commitment.

| Original source constraints | Source rank | Low-rank windows (≤3) | Full native candidates | Oriented assignments | Authentic K04 hits |
|---|---:|---:|---:|---:|---:|
| Printer only | 15,365 | 52 | 147 | 56,448 | **0** |
| Printer + AX-7778 | 15,495 | 52 | 147 | 56,448 | **0** |
| Printer + valid node49 | 15,432 | 52 | 147 | 56,448 | **0** |
| Printer + AX + valid node49 | 15,561 | 52 | 147 | 56,448 | **0** |
| Printer + AX + all 12 raw node49 | 15,622 | **69** | **197** | **75,648** | **0** |

17 further low-rank coupon windows appear only when the four CRC-invalid node49 values are admitted as *hypothetical* raw observations, at starts: **1147,1148,1149,1376,1551,1552,1722,1830,2005,2006,2173,2174,2175,2176,2738,3081,3082**. These are not K05-valid source records. The 52 printer-only low-rank windows include 13 rank-zero positions. Every enumerated complete coupon has a coherent source-model derivation; none matches original K04.

The original intact printer row130 at start955 is reproduced *exactly* without using its payload as a candidate target, and each lowrank stage has a planted complete assignment that the enumerator recovers. These validate equations, quotient enumeration and commitment-comparison machinery, but do not validate the hypothetical original copy relation. Original source originals, acceptance, verifier, and canonical candidate were never modified.

## Reproduction

The [source-pinned single-file test](../agents/agent11/k04_p951_future_replay_sft.py) uses the existing [p951 symbolic printer basis](../agents/agent49/k04_p951_symbolic_basis.py), constructs the original-source quotient, adds the AX/TRP2 observations under each declared source model, performs all complete-coupon SHA256 checks, and asserts the full candidate counts. An equivalent local extractor executed against the uploaded original ZIP and generated the numerical table above. The newly committed repository-script variant has not been separately run under CI.

## Interpretation and causal boundary

The experiment excludes precisely this **future-stage, four consecutive native MT word, optional per-word reversal/reordering** representation in five original-source model branches, with an end at stage5300 and rank≤3. Other output encodings, copy operations, stage locations, original physical corruption, generators, and final K08 wording are untested. It would be wrong to generalize the zero hits into an authenticated proof that the original selected stage contained any particular bits.

The independent [timestamp ordering challenge](../communications/broadcast/20261103T0141Z_Critic_generation-capture-clock-inversion.md) remains: original later-stamped node49/AX carriers map to hypothetical negative native indices. Precomputation or deferred copy could explain this, but no original record confirms that architecture or connects the alternative stages to selected ESC-N ACK2. This is a *candidate-construction negative*, not a recovered original coupon or stage selector.

**Status remains:** six original individual PASS, K04/K08 unresolved, combined INCOMPLETE. The next test should use a source-selected copy relation or a causal generation-to-capture bridge, not another lengthening of unanchored future stages.
