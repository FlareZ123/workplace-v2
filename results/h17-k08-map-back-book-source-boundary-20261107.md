# K08 map-back book and tea-receipt source boundary

**Agent 35 · 7 November 2026**

## Question

Does the physical book mentioned in MAIL-09 provide a plausible literal source for the missing K08 keeper caption, and can the supplied records identify the book or the page carrying Emily's margin?

## Source-derived facts

- MAIL-09 (Jason to Zoey, 1 October 2026, 08:03 UTC) says the library books were in the television room; one book with a map in the back belonged to David, and a tea receipt was being used as a bookmark and was deliberately left in place.
- N20 is attributed to Emily and describes the desired line's content as the sea, the end of the night, and voices at the table.
- N23 is attributed to Emily and says the wording in her margin was not an official slogan, while the envelope preserves the words she finally put on it.
- MAIL-11 says Emily worked from desk notes and photograph captions. MAIL-20 says several captions and drafts were on her desk and that her final selection matters.

The supplied records do **not** identify the book title, edition, page, receipt contents, date/merchant, or the medium in which Emily wrote the margin. MAIL-09 predates MAIL-11 by about ten hours, but chronology does not establish that Emily borrowed David's book or wrote in it. N23 has no date or page locator.

## External candidate tested (hypothesis only)

The public-domain GITenberg edition of *The Riddle of the Sands* (Project Gutenberg eBook 2360) is a plausible candidate for a book with maps at the back: its pinned HTML package contains `map-a.png`, `map-b.png`, `chart-a.png`, and `chart-b.png`. The source is not named in MAIL-09, so this is not an identification.

Pinned source:
- Repository: [GITenberg/The-Riddle-of-the-Sands_2360](https://github.com/GITenberg/The-Riddle-of-the-Sands_2360)
- Commit: `319919d550a9d5f959907ed8c75ca9509f3a56c1`
- Text: `2360.txt`
- Git blob SHA-1: `db9b00a3564514404073964b2da0e7637f8f53ec`
- Image assets: `2360-h/images/map-a.png`, `map-b.png`, `chart-a.png`, `chart-b.png`

## Exact printed-text test

The full pinned text was normalized using the K08 route's rule: lowercase; replace every character outside ASCII letters, digits and whitespace with a space; collapse whitespace; trim.

The test enumerated all contiguous windows of 3–64 normalized words that contained at least one term from each of these three frozen groups:

- Water/sea: `sea, seas, water, waters, tide, tides, wave, waves, ocean, shore, surf, harbour, harbor, bay, coast, coastline, channel, sand, sands, salt, brine, foam, estuary, estuarys`.
- Night/time: `night, tonight, evening, midnight, dawn, daybreak, dusk, darkness, dark, late, last, watch, morning, after, finish, finished, end, over, closing, close, ending`.
- Social/table/voice: `voice, voices, table, supper, dinner, meal, tea, coffee, talk, talked, talking, conversation, crew, hands, room, friends, friend, together, welcome, warmth, company, circle, gathered, chat, chatted, speaking, speak, spoke, heard, murmur, murmured, song, sing, laughter, laugh, laughing`.

For each candidate, the test computed HMAC-SHA256 using the original K08 desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`, retained the first 16 bytes, then SHA-256 hashed that component and compared it with the unchanged K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

**Executed.**

- Text length: 637,455 characters.
- Normalized words: 115,122.
- Candidate windows tested: **55,941**.
- Original K08 commitment matches: **0**.
- SHA-256("abc") and RFC 4231 HMAC-SHA256 positive-control vectors both passed.
- Reproducer: [`agents/agent35/k08_riddle_sands_literal_window_sft.js`](../agents/agent35/k08_riddle_sands_literal_window_sft.js).

## Interpretation and limits

This excludes a direct contiguous printed-text phrase in this specific edition under the frozen three-motif gate. It does not exclude a paraphrase, a different book or edition, map lettering, a handwritten marginal annotation, or text on either side of the bookmark. The public text is contextual evidence only; it is not the recovered K08 phrase.

The possible physical-marginalia link is an inference from MAIL-09 and N23, not an established fact. The records cannot tie Emily to David's book or identify the marked page. The exact book and bookmark should therefore be retrieved together, preserving their original position, title/edition, marked page and adjacent pages, all marginalia, and both sides of the receipt. Keep the word “receipt” open to the physical item's actual form; do not infer its contents from the phrase.

The `RN-047` entry in `supplier-reconciliation-L29.csv` is not a supported join to this tea receipt: it is mapped to ST-09 / BX25/03 / stores-float exception, with no reference to the television room, book, tea, or Emily.

**Outcome:** zero K08 words recovered. This is a bounded printed-text exclusion and a concrete physical-source locator, not a solution or a title identification.


## Chapter XX semantic fingerprint and expanded exact test

The specific candidate is now more interesting than a generic maritime book. Chapter XX of *The Riddle of the Sands* is titled “The Little Drab Book”. It opens with Davies at a cabin table amid books, then describes an old, cheap-cloth guide for yachtsmen to a British estuary. The in-story guide has a partly scratched white “3d.” label, a title-page attribution “By Lieut. X--, R.N.”, a yacht-owner frontispiece, and the name “Dollmann” on the back. The chapter closes with the protagonists too excited to sup or sleep, talking with absolute mutual confidence amid discordant voices. The sea, night, table and voices therefore appear in close narrative proximity, matching N20's three-part semantic description unusually well.

This is a **semantic/source hypothesis**, not an identification. The novel does not name the guide's title or say that the guide itself has a map in the back. MAIL-09's map-back book could be the novel, the in-story guide, or another book. The GITenberg edition's map/chart assets establish only that the novel itself is a plausible map-bearing candidate. The title/page/receipt and Emily-to-book link remain absent.

A second, broader exact test covered every contiguous 3–64-word window in Chapter XX, without any motif filter:
- Chapter XX normalized words: **3,938**.
- Candidate windows tested: **242,141**.
- K08 commitment matches: **0**.

The first whole-book test remains 55,941 motif-gated windows with zero matches. The chapter-wide test makes a direct printed quote from this chapter unlikely under the exact K08 normalization. If this source connection is real, the phrase is more likely Emily's paraphrase or a handwritten margin/receipt than a literal sentence in the printed text.

MAIL-06 supplies a possible physical identity check: David says his pocket book contains an old WN-14 standby transcription whose group D ends `5E67`. MAIL-09's map-back book also belongs to David, one day later. The two items may be the same, but the records do not say so. Interpreting `5E67` as hex word offset 24,167 in the novel produced generic surrounding text; no indexing rule is established. If the book is recovered, check whether it contains that standby transcription as an identity discriminator, not as a K08 component.

For physical retrieval, check the exact David-owned book against the Chapter-XX fingerprint (old drab/cheap cloth, 3d. label, yachtsman's guide to a British estuary, Lieut. X-- R.N. title page, yacht frontispiece, “Dollmann” on back), and separately check for the WN-14 standby transcription ending `5E67`. Preserve the receipt bookmark in situ, the marked page and adjacent pages, all marginalia, and both sides of the receipt. Do not infer the book's title from this candidate.
