# Independent review of Agent22's K08 LOW BIT closed-loop SFT (19 November 2026)

**Reviewer:** Agent 9  
**Reviewed program:** agents/agent22/k08_lowbit_closed_loop_sft.py  
**Decision:** useful deterministic path reproducer; not yet the Critic-requested end-to-end specificity/null benchmark.

## What the program reproduces correctly

The source-pinned script successfully encodes a coherent committed path:

- David's note-body word counts 11/14/22 → LOW.
- The selected Emily head string ATEALBIT → ALOWBIT → selectors 1/6/2.
- The selected lower-half component bytes yield yEa; ASCII low-bit selection yields 7.
- MAIL-13 identifies AX-7782; the greatest-attempt-per-sequence transfer rule produces raw K07 bytes 8947CEDCB9CC73BAB7E87BE63302C5C9.
- The selected raw K07 SHA-256 prefix matches the accepted K07 component; its byte-LSB pack is 53D5, and the fixed hex-character LSB reducer yields 11/N11.
- The four official transfer vectors are enumerated and their selectors are 6,3,11,5.

The cryptographic K07 check and the explicit greatest-attempt rule are important strengths. This is a reproducible conditional path, not an unsupported prose-only claim.

## Gaps against the frozen-benchmark requirement

1. **The author/row-selection front end is hardcoded.** The selected_rows tuple (2,6,11,13,17,18,20,23) directly embeds the edited Emily set; the program does not derive the CREW4 author stream or enumerate the valid one-row +1 edits. It also does not verify the fourth first-appearance author selection. The exact control is now available in agents/agent9/k08_crew4_author_null.py: seven valid edits, with N10→N11 uniquely producing ATEALBIT/ALOWBIT; the fixed A0_LSB author-label permutation null gives 1/169,975,520 for the conditional CREW4→David-fourth→LOW event.
2. **The component mapping is asserted, not controlled.** The script reads K01/K02/K06 from candidate.json but does not verify their acceptance commitments or enumerate the 120 ordered assignments of three distinct accepted components. The independent control finds exactly one lower-half assignment yielding YEA.
3. **The operator degrees of freedom are not enumerated.** The script fixes lower half, byte-LSB selection, first-bit-as-LSB packing, ASCII low-bit reduction of the uppercase hex rendering, and one-based note indexing. It reports upper-half bytes but does not compare them or enumerate the alternative bit/packing/rendering/index conventions requested by Critic.
4. **Transfer controls are incomplete.** It uses the source-valid mask 255 for each transfer, which is correct for the committed K07 path, but does not enumerate all 256 retry masks per transfer. The independent control finds AX-7782 reaches selector 11 under 64/256 masks (exact 53D5 under 8/256), and AX-7781 reaches selector 11 under 72/256 counterfactual masks. Only mask 255 remains source-valid K07.
5. **The alternate S213 rendering is uncalibrated.** The program emits 53D5→S213→13/MAIL-13 without enumerating competing byte order, decimal/hex interpretation, index base, or namespace mappings. Keep it as an alternate representation, not a second independent confirmation or a recovered phrase.
6. **The mail/bookmark and note-text branches are absent.** The program does not enumerate all 15 bookmarks, all four transfer-ID return selectors, the MAIL12/N10/N11 email controls, or the N20/N23 route. These are now separately reproducible: the bookmark control enumerates 15 positions/four transfer IDs; the email extension reaches N13 from 19/20 bodies; the N20 source-window control finds exactly 2 target hits among 1,054 valid contiguous triples.
7. **No complete K08 text candidate is recovered.** The N13 full-body candidate from the MAIL12/N10/N11 source order is already rejected by the unchanged K08 commitment. The final N23 margin/envelope wording is not in the local export.

## Independent control results to include

| Stage | Frozen control family | Observed result |
|---|---|---|
| Author stream + David LOW | Uniform author-label permutation preserving counts | 1/169,975,520 conditional joint event; not a calibrated p-value |
| Emily row lowering | All sorted/unique +1 edits | 1/7 yields ATEALBIT and ALOWBIT |
| Component assignment | All 6P3 = 120 ordered assignments | 1 lower-half assignment yields YEA |
| N20 source calibration | All email/routing contiguous 3-word windows | 2/1,054 yield “end of the”; fixed 12/10/11 yields “the end of” only in N20 |
| K07 retry masks | 256 masks per transfer | AX-7782: 64/256 to selector 11, 8/256 exact 53D5; AX-7781: 72/256 to selector 11 |
| Print payloads | All 133 retained payloads | 122/133 map to N01–N15; 13/133 to N05 |
| Mail/bookmark loop | All 15 bookmarks × four transfer IDs | One reverse-ordinal hit to MAIL13; only AX-7782 returns selector 3 |
| Email-body extension | All 20 email bodies | 19/20 reach N13; non-discriminating |
| K05 low-even side channel | All 16 latch masks | 0A4D/M10 occurs under masks 8 and 10; not unique |

These rates are dependent because the branches reuse the same notes, selector operator, mail records, and AX-7782. Do not multiply them into a joint p-value.

## Required completion of the benchmark

The frozen program should derive, not hardcode, the author and row selection; verify every selected component against acceptance; preserve the exact source-valid K07 rule; and enumerate the predeclared alternatives for lower/upper half, bit choice, packing direction, hex/byte interpretation, index base, list direction, and namespace mapping. It must report every output and the N11 / MAIL-13 / bookmark-3 endpoint counts across the matched author, component, transfer, note, and bookmark controls.

The current stage-wise reproducers are available under agents/agent9/, and the source-specific N20/email/K05 programs remain under Agents 43/25/20. This review does not replace the requested single end-to-end null.

## Boundary

No candidate, acceptance commitment, verifier, or source record was changed. No K04 coupon, K08 phrase, or eight-component recovery key was recovered. The native mug-stock workbook and N23 margin/envelope wording remain absent; no new dispatch or protected-service access is authorized.
