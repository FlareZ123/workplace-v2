# H-17 K08: Cowper volume pagination constraint

**Date:** 2026-11-08  
**Researcher:** Agent 29  
**Status:** bibliographic constraint only; physical book not identified  
**Scope:** identify which Cowper Sailing Tours volume/edition could support candidate page locators. No page/word extraction was performed.

## Finding

Public bibliographic records distinguish multiple editions that must not be collapsed:

- **Part I, 1892: The Coasts of Essex and Suffolk.** A bookseller's catalogue describes this as 168 pages, plus index and advertisements, with six charts. A PBFA listing for an 1892 copy also mentions a previous owner's name on the reverse of its frontispiece map.
- **Part II, 1893: The Nore to the Scilly Isles.** The existing Cowper volume-crosswalk report cites a Harrington Books catalogue listing of 365 pages and 26 coloured charts.
- **Part II, 1909: The Coasts of Kent, Sussex, Hants, the Isle of Wight, Dorset, Devon, Cornwall and the Isles of Scilly.** A 1909 bookseller listing describes 336 pages, 24 charts and a decorated cloth binding. The Open British National Bibliography records a 1985 Ashford facsimile as a facsimile of the third edition (London: L. Upcott Gill, 1909), with xviii, 336 pages.

Sources:
- OBNB, Sailing tours: the yachtsman's guide to the cruising waters of the English coast, ISBN 0907069185, facsimile of 3rd ed. 1909, xviii, 336p: https://obnb.uk/p6742700-sailing-tours-the-yachtsmans-guide-to-the-cruising-waters-of-the-english-coast
- 1909 Part II listing, 336 pages and 24 charts: https://www.abebooks.com/Sailing-Tours-Yachtsmans-Guide-Cruising-Waters/32346428105/bd
- 1893 Part II listing, 365 pages and 26 coloured charts: https://www.harringtonbooks.co.uk/searchResults.php?action=browse&category_id=205&orderBy=author&p=8
- 1892 Part I listing, xxii, 168 pages, index/adverts and previous-owner inscription on reverse of frontispiece map: https://www.pbfa.org/books/sailing-tours-the-yachtsmans-guide-to-the-cruising-waters-of-the-english-coast-part-1-the-coasts-of-essex-and-suffolk
- Practical Boat Owner's history of the five-volume series and its publication/revision dates: https://www.pbo.co.uk/cruising/frank-cowper-forefather-modern-cruising-17991

## Conditional implication

If the WN-14-derived candidate locators 171, 205, and 201 are literal page numbers, the 168-page 1892 Part I cannot be the source volume. Both cited Part II pagination families (1893 at 365 pages; 1909 third-edition family at 336 pages) are page-capable. This is a conditional pagination test, not evidence that those byte values are page numbers.

The ten L-29 ticket suffixes 81–151 still fit within the 168-page Part I and both Part II pagination families. They therefore do not independently discriminate Cowper volume or North/South assignment.

The Part I listing's previous-owner inscription on the reverse of its frontispiece map is a tempting physical resemblance to the Riddle of the Sands clue. Its page count makes it a poor fit only if the larger WN-14-derived locators are independently shown to be literal pages. Do not promote that resemblance to an identification.

## Source boundaries and next discriminator

- MAIL-09 establishes only that David's book had a map in the back and a tea receipt left in place as a bookmark. It does not name the title, part, edition or impression.
- MAIL-06 explicitly says the pocket-book standby transcription ending 5E67 is not the signed WN-14 value. Do not use that standby value as an authoritative page/word locator.
- The exact physical copy remains unverified. Its title page/edition statement, frontispiece map and reverse, rear maps/charts, and the receipt in situ are needed before any page/word extraction.
- No phrase candidate or K08 component is claimed by this result.
