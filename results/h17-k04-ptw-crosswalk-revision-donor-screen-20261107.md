# K04 p951: North-ticket crosswalk and PTW-417 revision donor screen

**Agent 24 | 7 November 2026.** A bounded, conditional complete-coupon test. **640 distinct candidates; zero original K04 commitment matches.** The p951 MT chronology and both ST↔PTW offsets remain unverified. No original selected coupon bits were authenticated.

## Question

Could the four North L-29 repair-ticket-linked singleton permit serials, together with one four-bay PTW-417 revision cohort, supply the eight native MT words that make the selected p951 coupon observable?

The proposed eight-word positions are the already-published conditional p951 minimum:
- gap 43: native stages 328–331;
- gap 96: native stages 724–727.

This test is distinct from the earlier cross-archive donor search using only the accepted K03 PTW-417 serial block. It uses the four other singleton permits implied by the competing North ticket offsets, and separately tests all four PTW-417 revision cohorts.

## Source inputs and frozen alternatives

The North binder lists ST-094, ST-081, ST-106, ST-099 and ST-112. ST-081 is omitted because neither corresponding PTW-381 (+300) nor PTW-385 (+304) has a serial receipt in the surviving seal-receipts.jsonl. The four remaining posted FA-17/A3 North tickets are:

| Ticket | +300 permit | +304 permit |
|---|---:|---:|
| ST-094 | PTW-394 | PTW-398 |
| ST-106 | PTW-406 | PTW-410 |
| ST-099 | PTW-399 | PTW-403 |
| ST-112 | PTW-412 | PTW-416 |

Both offsets are retained as hypotheses. The +300 and +304 mappings are not treated as authenticated.

For each offset, the four singleton permit serials are ordered two ways:
1. original L-29/N binder order (ST-094, ST-106, ST-099, ST-112);
2. the PTW-417 witness walk B,D,A,C from MAIL-04.

The second donor group is a PTW-417 revision cohort, ordered B,D,A,C. All original serial records are included:
- revision 1: two distinct Bay-A serial alternatives, producing two cohort choices;
- revision 2: the four signed CLOSED AS_LEFT serials used by the K03 reducer;
- revision 3: the four OPEN AS_LEFT serials;
- revision 4: the four CLOSED REMOVED serials.

Revisions 3 and 4 are included as historical donor hypotheses only. They are not substituted into K03.

## Method

The source-pinned p951 MT19937 basis is built from the original 132 intact printer packets. Selected printer row129 is withheld before reading its PAYLOAD through Agent49's source loader. The original basis rank is 15,365.

For each North-ticket group and each PTW-417 revision group, test:
- North-group order: binder or B,D,A,C witness walk;
- each group's 32-bit word byte order: big or little endian;
- each group's interpretation: raw native word or inverse-tempered MT output;
- assignment of the North group to gap43 or gap96.

Each eight-word assignment adds 256 independent equations, raising rank to 15,621 and determining the selected 128-bit target under this conditional model. The complete four-word target output is tempered, serialized little-endian, XORed with the original K04 route mask, and checked against the unchanged original K04 SHA-256 commitment.

A source-consistent synthetic positive control completes the original affine printer basis with free variables set to zero, extracts the corresponding eight gap words, and verifies that the same recovery routine reproduces the exact withheld synthetic 16-byte target. This validates the algebraic composition and byte handling; it does not authenticate a historical generator.

## Result

| Crosswalk | Complete candidates | Original K04 commitment hits |
|---|---:|---:|
| +300 | 320 | 0 |
| +304 | 320 | 0 |
| **Total** | **640** | **0** |

All 640 component candidates were unique. The source-consistent synthetic positive control passed.

The finite family therefore supplies **no accepted K04 component**. The result does not resolve the ST↔PTW offset, prove or disprove the historical p951 producer, or authenticate any PTW serial as a printer-native observation.

## Reproduction and source controls

Run from the repository root:

    python agents/agent24/k04_ptw_crosswalk_revision_donors_sft.py

SFT: [agents/agent24/k04_ptw_crosswalk_revision_donors_sft.py](../agents/agent24/k04_ptw_crosswalk_revision_donors_sft.py)

Pinned original source SHA-256:
- printer spool: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083;
- seal receipts: c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32;
- print-fleet retirement note: 10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf;
- supplier reconciliation: 73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e.

The test reads the original route mask and K04 commitment only for final candidate adjudication. It does not use the selected row129 payload to fit the model. It does not use K08 data. Original evidence, candidate, acceptance, and verifier files are unchanged.

## Interpretation and next action

This closes one precisely specified crosswalk-conditioned donor family. Do not widen it into arbitrary PTW revision permutations or free stage assignments. The remaining useful K04 paths require an original paired ticket or authoritative September return index to authenticate the offset, and a separate source record that connects physical/copy custody to the selected coupon or supplies independently indexed native observations. Agent36's North cassette and incident-removal custody route remains separate from this conditional algebra.

K04 remains missing; K08 remains missing; the official recovery remains six accepted components and two unresolved.
