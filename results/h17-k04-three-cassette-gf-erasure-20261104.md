# K04: three L-29 printer cassettes as a GF(256)/GF(65536) erasure code

**Agent 4, 4 November 2026 (19:34–19:39 UTC).** A target-facing, source-bound *hypothetical* complete-packet producer test. **No original K04 hit.** The other six verified REC8 components remain intact; K08 exact wording still unknown.

## Mechanism and source selection

The original 4 October print-fleet retirement note maps the selected ESC-N north printer **PS-261003-0417** to cassette **L-29/N**, separately retaining south **L-29/S** (PS-261003-0448) and watch-spare **L-29/W** (PS-261003-0420). The original spool records the late selected north RECOVER ACK2 at 3 October 18:02 UTC, copied `A9A9DC5731A5E2AE879C47215C2559D5`; intact late south RECOVER ACK1 at 18:24 UTC, `234BE186E97EE05830909790E336109E`; and watch-spare RECOVER ACK2 at 18:25 UTC, `432475F72A62DB39F3D5693E2C937FA4`. No original report asserts these cassettes form an erasure code. The fleet return note was recorded **after** the target print; its ticket data are candidate labels, not contemporaneous producer authentication.

Hypothesis: for each byte lane in GF(2^8), or for each independent two-byte lane in GF(2^16), the three packets are evaluations of a common affine polynomial `p(x)=a*x+b` at known route/job/ticket coordinates. Each entire missing north packet is consequently reconstructed as

`P_N=((x_N⊕x_W)/(x_S⊕x_W))*P_S ⊕ ((x_N⊕x_S)/(x_W⊕x_S))*P_W`

where arithmetic is in the selected binary field. Tested seven independent source-visible coordinate triples: N/S/W ordinal, ASCII route character, job suffix modulo 256, minute after 18:00 UTC, first repair-ticket number, sum of repair-ticket numbers modulo 256, and route letter alphabet index. Models used GF(256) polynomials 0x11B and 0x11D, GF(65536) polynomial 0x1100B, both 16-bit word endiannesses. These give **28 source-defined complete north coupon assignments**. Every one was XORed with the unchanged K04 route mask and checked against the full original SHA256 commitment.

## Actual results, controls and interpretation

- Source hashes: spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; fleet note `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`; acceptance `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.
- All six independently planted **complete 128-bit finite-field interpolation positives** passed, exercising both field widths and both byte orders. All 28 tested original component commitments yielded **NO_MATCH**.
- The original ordinary spool contains 11 complete `CLASS=RECOVER, DEST=bench, STATE=ACK` packets. Among **36** full-packet predictions made by interpolating each source-chronological triple (with source job-number field coordinates), **zero** predict their withheld complete first packet. Maximum agreement with any heldout packet is one byte. The late predictions also agree with the disputed north copied ACK in at most one byte.
- This rejects a **simple three-cassette systematic affine-field parity issuer** for exactly the tested coordinates and field/word layouts. It also rejects the matched ordinary global writer for the heldout controls. A late-only writer, other coordinates, additional source state, unequal physical copy quality and different coding schemes remain open.

This is a novel candidate construction over **independent byte/halfword fields** and the *actual three source-named fleet return cassettes*, rather than global GF(2^128) two-anchor affine models or north/south shared XOR/additive pads previously tested. Its weak original source model and complete negative make it an **exploratory finite exclusion**, not an acquired physical coupon or author-final word.

Reproducer: [portable source-pinned SFT](../agents/agent4/k04_three_cassette_gf_erasure_sft.py). Source contents, six accepted slots, original K04 mask, original verifier and acceptance commitments were never modified.
