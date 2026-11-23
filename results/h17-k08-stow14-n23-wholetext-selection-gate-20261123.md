# K08 STOW14 / N23 whole-text selection gate

**Date:** 2026-11-23  
**Agent:** 14  
**Question:** Does the STOW14 author-mask output plus the conditional N23 → PS-261003-0323 association define a complete whole-text edit or selection operation for K08?

## Result

**No complete phrase constructor was recovered.** The two locators converge on note N09 under one simple arithmetic/bit route, but neither is source-authenticated as a text operation. Bounded word-selection interpretations produce no K08 commitment hit and fail the available label controls.

## Source pins

The reproducer `agents/agent14/k08_stow14_n23_selection_sft.py` reads only the three source files below and the acceptance JSON. It does not access `private/` or the hash-only BX25-08 PDF.

| Source | SHA-256 |
|---|---|
| `noticeboard-and-desk-notes.txt` | `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` |
| `spool-reconstruction.log` | `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` |
| `recovery-routing.json` | `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` |

The unchanged K08 acceptance commitment is SHA-256 `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747` of the 16-byte HMAC result.

## Bounded tests

### 1. STOW14 as a note-set locator

The K05/K06/K07 author-mask code selects these 14 notes authored by Simon, Emily or Gabriel:

`N02, N05, N06, N07, N10, N12, N13, N14, N17, N18, N20, N22, N23, N24`.

The arithmetic `23 − 14 = 9` points from N23 to N09. Separately, applying the existing low-bit-to-selector operation to the *ordinally paired* PS-0323 ACK1 payload gives packed low bits `56F1`, whose hex-character low bits yield selector **9**. Both paths therefore point to N09, Zoey's galley-board caption.

This is a **conditional locator convergence only**:
- The N01–N24 ↔ PS-0301–PS-0324 join is based on suffix and five-minute cadence, not an authenticated queue/job manifest.
- The reconstructed spool payload is explicitly opaque and not independently integrity-checked.
- The K08 route names crew notes and noticeboard drafts, not spool payloads. The missing-evidence gate records that PS-0323 has no preserved route assignment; MAIL-16's ESC-N/ESC-S/WATCH-SPARE restrictions do not authenticate PS-0323 as K08 input.
- N09 is a galley-board caption, not the final keeper-envelope phrase. Directly adopting it does not pass K08.

### 2. STOW14 as a 14-position whole-note shift

A backward cyclic shift of 14 across the 24-note sequence maps N23 → N09, N20 → N06, N13 → N23 and N10 → N20. However, offset 14 is not distinctive in the text:
- same-author pairs: **6/24** at offset 14, versus a maximum **8/24** at offsets 7 and 17;
- mean note-word Jaccard: **0.05575** at offset 14, versus a maximum **0.06890** at offsets 9 and 15.

The apparent N23 → N09 pair therefore does not establish a special editorial shift or a whole-text revision chain.

### 3. Rejected literal word-index sanity checks (not source-defined)

The intended direction is to treat selectors as record locators, not word indexes. I ran the following bounded checks only as negative sanity tests of a tempting literal bitmask interpretation; they are not proposed source-authored operations and should not be extended. Applying the PS-0323 payload-byte LSB mask to N23 yields:

`wording in margin never official only remembers the words`

Applying it to the N20 semantic brief yields:

`wanted the to the the night and the voices`

The complementary masks, reversed mask, and reciprocal N20/PS-0320 cases are also evaluated by the reproducer. None matches the unchanged K08 commitment.

A second rejected sanity check uses the first 14 PS-0323 payload bytes as low- or high-nibble word indexes across the 14 STOW notes. This is likewise not a source-defined operation. The resulting normalized strings are:
- low nibble: `good boat on back to you remembered if watch first to printer an with`;
- high nibble: `good and stays it i best stood disappeared the the the is slogan every`.

Neither matches K08. As a simple generalization control, the same per-job LSB word mask does not reconstruct the explicit N17 standby label (selects only `light the`) or N18 commissioning label (selects only `before the boat`). These are exploratory operations, not source-defined encodings.

## Whole-record selection refinement from MAIL-11

Reproducer: `agents/agent14/k08_whole_record_selection.py` (uses MAIL-11 exclusions and reports the N23/PS-0323 join as conditional; it does not treat selector bits as word indexes).

The 14-note CREW4-author set includes N17, N18 and N23. MAIL-11 explicitly rejects the complete N17 standby label (“Leave the light on for the next watch”) and the complete N18 commissioning label (“Back before the first boat”) as the final desk phrase. N23 independently states that the envelope preserves the words Emily finally put on it. This supports a **source-authored whole-record selection at the note level**: select N23 as the final-envelope instruction record, not N17/N18 and not a word-level assembly.

Under the **conditional** Nxx↔PS03xx suffix/cadence crosswalk, the two RECOVER/store jobs in the 14-note author set are N18/PS0318 and N23/PS0323. MAIL-11 excludes N18, leaving PS-0323 as a **conditional native print-object retrieval target**. This is a useful retrieval heuristic, not an authenticated job assignment: the route table has no preserved queue role for PS-0323, the note/job join remains ordinal, and the reconstructed 16-byte payload is not rendered text.

Thus a whole-record selection is supported at the level of identifying N23 as the instruction record; no whole-text transformation or exact phrase was recovered. The PS-0323 print-object link remains conditional pending a contemporaneous queue/collection manifest.

## Decision and next useful evidence

STOW14 and N23/PS-0323 remain useful **source locators**, not a recovered phrase or authenticated text editor. The convergence on N09 is worth retaining as a conditional base-text lead if an authenticated WN-14/Bundle-06 or native print manifest arrives; it does not justify turning the opaque spool payload into K08 words.

The exact phrase still requires a source that records Emily's final words: the original recovery-envelope face/margin, desk notebook margin, complete authenticated correspondence, original photo-caption revision, or Zoey's small shelf card. The existing custodian request channel is closed; do not reopen it. Use only a new authorized custody path or unsolicited source delivery.

No candidate, acceptance commitment, verifier, or accepted component was modified. K08 remains **MISSING**; REC8/1 remains **INCOMPLETE**.
