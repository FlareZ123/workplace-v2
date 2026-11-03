# Original cross-carrier 227-step joint MT parity donor search

**Agent4, 3 November 2026 | New source-only, cross-field test. No K04/K08 recovery.**

The newly identified consecutive revision B footer controls showed that whole-word prediction can connect records generated in different evidence streams. A separate, harder possibility is **two outputs whose individual values remain unpredictable but whose joint parity is fixed** by the surviving printer source. Single-word exact-match scans would miss such pairs.

To test it, build the original p951 MT19937 symbolic source with all 132 retained intact printer packets. Exclude selected printer row129 throughout. The exact original printer-only equation rank is 15365. From independent nonprinter source files extract **152 original four-byte fields**: 12 RC17 revision B/C/D footer strips, 84 CRC-valid TRP2 CONTROL words, 44 PTW seal serial suffixes, four signed WN-14 ink groups, and eight 4-byte chunks of the route-sheet K04 mask / K08 nonce. Those route constants are independently preserved; no selected K04 coupon or commitment is loaded.

For each pair of symbolic native stages `t`, `t+227` within -1100..1040, reduce their 64 native or tempered output-bit expressions modulo the original 132-packet source equations. Retain positions where *both* outputs individually have no more than twelve already fixed bits and where the two together impose at least **24 independent cross-word parity equations**. This explicitly targets hidden two-word relationships, excluding the trivial case where a single word was already predictable.

| Symbolic output view | Eligible 227-apart stage pairs |
|---|---:|
| Native | 143 |
| Tempered | 145 |
| **Combined** | **288** |

At each eligible position, test **both byte orders** and every ordered pair of **distinct** original four-byte fields. A parity-syndrome join avoids constructing the 13.2 million pairs individually. All source-fixed affine equations are checked, including within-word constraints as well as cross-word parity.

<text strong color="default">Original-data result: 0 exact matches among 13,220,352 pair assignments.</text>

The [reproducible source-pinned SFT](../agents/agent4/k04_rc17_crosscarrier_227_syndrome_sft.py) includes a synthetic positive pair generated from the source-compatible affine parity values, plus a forced one-bit negative. It asserts the original field census and zero matches. This is **a new cross-carrier joint-syndrome test**, rather than another isolated full-word donor scan.

**Interpretation:** Under the specified p951 producer and MT lag227 pairing, the surviving original fullword carriers do not provide a second independently joint-constrained donor pair at these source-informative stages. This cannot exclude three-way constraints, other lag distances, a different producer, or pairs involving non-fourbyte extraction rules. Previously found B VERIFY/PURGE remains the sole strong original full-word link, and its conditional source rank increase does not fix the selected K04 bits. Six components remain accepted; K04 and K08 missing; combined INCOMPLETE. Original evidence and acceptance commitments are unchanged.
