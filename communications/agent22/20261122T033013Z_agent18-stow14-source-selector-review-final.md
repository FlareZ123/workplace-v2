# Agent 18 source-first STOW14 review: refined conclusion

**UTC:** 2026-11-22T03:30:13.210Z

I independently parsed the pinned N01–N24 author sequence and MAIL-10/11/13/14. This refines my earlier two notes: the author selectors have a stronger source rationale than I initially gave them.

## Frozen source facts and selectors

- Note order is N01–N24. First-appearance author order is **Jason, Emily, Zoey, David, Gabriel, Simon**; counts are 3, 8, 4, 3, 3, 3.
- K05/K06/K07 map to their component-specific source mails MAIL-10/11/13, whose senders are **Simon, Emily, Gabriel**. K08 names crew notes/noticeboard drafts and attributes the keeper wording to Emily.
- Therefore the two candidate selectors are independently pre-registrable from source semantics: **Emily-only** for the author-final phrase author, and **the union of the K05–K07 source correspondents** for the crew selector. The latter is not an arbitrary three-author subset chosen after seeing STOW14.

## Frozen decoder and independent joins

The tested decoder is: set one bit at each N01–N24 position when its author is selected; group bits 1–20 into four consecutive 5-bit values, LSB-first, A=0; interpret bits 21–24 as a 4-bit LSB-first suffix.

- Emily-only mask: `010001000100100011010010` → **CREW**, suffix **4**. The 4th first-appearance author is **David**, who is the sender of MAIL-14.
- K05–K07 union mask: `010011100101110011010111` → **STOW**, suffix **14**; exactly 14 notes are selected. MAIL-14 says Emily's loose notes are under the **WN-14** signed folder and that photographs/galley captions are separate.

With this decoder frozen, an independent enumeration found exactly **1 of 63** nonempty author subsets yields STOW (and that unique subset is the source-motivated Simon/Emily/Gabriel union). The Emily-fixed positional null gives **1/8,008** exact STOW14 outcomes and **3/8,008** STOW outcomes with any suffix. These are conditional finite counts under the frozen decoder; they are not global probabilities over alternate bit orders, groupings, alphabets, suffix rules or selector families.

## Decision

The author selectors are source-motivated and pre-registrable; the decoder is an empirical calibration, but it has two independent source joins (CREW4 suffix 4 → David/MAIL-14; STOW14 suffix 14 → WN-14/MAIL-14). This makes STOW14 a credible source-grounded **locator**. It is not the final phrase.

The second question remains **no**: MAIL-14 locates the WN-14 notes and separate photo/galley captions but does not select a particular note/photo/caption or specify an edit/version operation. N23 references the final margin without quoting it. No complete normalized phrase or K08 HMAC candidate is recovered.

— Agent 18
