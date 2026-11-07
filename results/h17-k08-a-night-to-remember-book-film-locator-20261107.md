# K08 false-positive audit: *A Night to Remember*

**Agent 6 · 7 November 2026**  
**Status: pruned false positive for MAIL-09's map-back book; retained to prevent rediscovery. K08 phrase not recovered.**

## Question

Could MAIL-09's David-owned book with a map at the back and MAIL-15's Saturday film be references to the same work, and does that relationship provide a more discriminating K08 source locator?

## Local source facts

- **MAIL-09** says the library books were in the television room, that the map-back book belonged to David, and that a tea receipt was being used as a bookmark and was left in place.
- **MAIL-15** says a film would be watched after late dinner and that subtitles needed to be enabled manually after each power cycle. It does not name the film.
- **MAIL-11** and **N20** describe Emily's intended line in terms of people making room after a long watch, water outside, the night nearly finished, and voices at a table.
- **N23** still locates the final wording in Emily's margin and says the envelope preserves her final words. No surviving local record quotes them.

## External cross-record candidate

Walter Lord's *A Night to Remember* (1955) and its 1958 film adaptation provide a coherent candidate for the MAIL-09 / MAIL-15 pair.

The official Folio Society product page describes a 2024 edition with **264 pages**, 100 images, and an original Titanic deck plan folded into a separate blocked pocket at the back. It identifies Walter Lord as author and notes the book's adaptation for television and film in the 1950s:

- https://www.foliosociety.com/usa/a-night-to-remember

This is a particularly close physical fit for MAIL-09's “map in the back” description. It is stronger than a generic nautical-book match because the folded plan is specifically a Titanic deck plan. It is still only a candidate: MAIL-09 does not give a title, publisher, edition, page count, or description of the map.

The 1958 film is independently catalogued by TCM:

- https://www.tcm.com/watchtcm/titles/84970

The official Folio page also confirms the book's adaptation into film in the 1950s. Thus a single work could explain both the map-bearing book in MAIL-09 and the Saturday film/subtitle setup in MAIL-15. The export does not establish that this was the film actually shown.

## Edition caution

A 50th-anniversary trade edition's contents list chapter 4, “You Go and I'll Stay a While,” at page 47:

- https://www.cincinnatistate.ecampus.com/night-remember-2nd-lord-walter-philbrick/bk/9780805077643

That page locator belongs to that trade edition. It must **not** be transferred to the 2024 Folio edition, whose 264-page illustrated layout is materially different. If the physical copy is recovered, record its exact title/imprint/edition and the receipt's actual page before using any page number as a locator.

The chapter title and its story of a husband letting his wife take a lifeboat are thematically close to MAIL-11/N20's language about making room for others. This is a scene-level resemblance, not proof that Emily borrowed the wording.

## Bounded commitment checks

The following exact candidates were checked using the supplied K08 normalization, HMAC-SHA256 with the decoded desk nonce, first-16-byte truncation, and the unchanged acceptance SHA-256 commitment:

- “A Night to Remember”
- “You go and I'll stay a while”
- “We started out together and we'll finish together”
- “We started out together and we will finish together”
- “The last night of a small town”
- “The incredible night the Titanic went down”
- “Women and children first”
- “People first, things second”
- “Where you go, I go”
- “We stay together”
- “I understand”
- “You can still go”
- “Don't stay on the ship until the end”

**Result: zero commitment matches.** Agent18 independently reports that its obvious chapter-title/direct-dialogue candidates also failed. These are bounded negatives for the listed strings only; they do not test Emily's paraphrase, the complete book, the full subtitle track, or handwritten marginalia.

A community subtitle source for the 1958 film is indexed at:
- https://subtitlecat.com/subs/191/A%20Night%20to%20Remember%20%281958%29%20-%20Eng.html
- https://subdl.com/subtitle/sd27175/a-night-to-remember/english

The latter lists multiple English release-specific subtitle files. Agent10 is pursuing a bounded complete-subtitle screen; this report does not duplicate that work or treat a community transcription as an authenticated master.

## Adversarial disposition

**False positive for the map-back book.** The deck-plan pocket and 1958 adaptation made this an attractive two-mail join, but a stronger candidate now explains the actual MAIL-09/MAIL-11/N20 clues: Arthur Ransome's *We Didn't Mean to Go to Sea*, 1949 18th impression. Its rear endpaper map and page-94 Chapter VII scene (an all-night passage, Susan setting a place for five at the cabin table, children waiting in fog with the sea outside) match the local semantic brief much more specifically. See [Ransome map/endpaper locator](h17-k08-ransome-map-endpaper-locator-candidate-20261107.md).

The 2024 Folio *A Night to Remember* edition remains a real book/film pair and its rear deck-plan pocket is real, but MAIL-15 does not identify the Saturday film. The local source does not connect that film to MAIL-09's book. The title, chapter title, direct dialogue, and other tested strings produce no K08 HMAC hit. Do not continue subtitle or literary phrase sweeps on this candidate unless a source explicitly identifies it.

**No recovered K08 phrase.** The strongest current physical retrieval target is the Ransome copy and its receipt bookmark, while the literal carrier remains Emily's original envelope/margin and separate desk-note/photo-caption stack. The book's printed text is a locator/inspiration candidate, not a substitute for the handwritten final wording.

## Discriminating physical check

If the already-authorized custody path yields David's book, preserve the book and tea receipt in situ before moving either. Record:

1. Exact title page, publisher, edition, publication date, and pagination.
2. Whether the copy is the 2024 Folio Society edition (264 pages; separate blocked pocket; folded Titanic deck plan) or another edition.
3. Exact position of the tea receipt, including whether it is between pages or in the rear plan pocket.
4. Both faces of the receipt, its date/vendor/amount/reference, and any handwriting.
5. The marked page, adjacent pages, margins, endpapers, and any annotations on the deck plan.
6. Any physical or chronological link from the book/receipt to Emily's final envelope margin.

Keep the book, receipt, envelope, desk notes, and photo-caption stack as separate objects until a physical join is observed. Apply the unchanged K08 HMAC only to a complete, attributable candidate phrase. Do not substitute a printed chapter title or thematic paraphrase for Emily's final wording.


## Audit note

This report is retained as a documented false positive. Its external product/film facts remain true; the inference that the pair identifies David's MAIL-09 book is superseded by the more specific Ransome page-94/endpaper-map candidate. The full subtitle screen belongs to Agent10's independent work and should not be repeated from this branch.
