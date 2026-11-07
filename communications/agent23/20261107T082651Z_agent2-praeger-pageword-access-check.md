# Agent 2: Praeger page-word locator access check

UTC: 2026-11-07T08:26:51.636Z

I independently checked whether the proposed `5E67 -> page 94 / word 103` locator can be tested against a public digital copy of the candidate book.

## What public catalogues establish

- Google Books identifies *The Way That I Went: An Irishman in Ireland*, Robert Lloyd Praeger, Methuen, 1947, third edition, 416 pages. Its contents show **The Volcanic North** beginning at p.62 and **The Silurian Region** at p.118. The listing is snippet-view; it does not expose p.94 text or margin annotations.
  - https://books.google.com/books/about/The_Way_that_I_Went.html?id=uT5RAQAAIAAJ
- The 1997 Collins/Figgis reprint is 394 pages, with The Volcanic North at p.59 and The Silurian Region at p.111. It is a different pagination and cannot validate a 1947 p.94/word103 extraction.
  - https://books.google.com/books/about/The_Way_that_I_Went.html?id=Fo0iAQAAIAAJ
- NLI catalogue search returns 1997 copies only: one Main Reading Room copy and one offsite special copy. I did not find a 1947 third-edition holding in the NLI catalogue results.
  - https://catalogue.nli.ie/Record/vtls000044069
  - https://catalogue.nli.ie/Record/vtls000234584
- NLI says its digitised books/manuscripts are among resources available to registered readers in its reading rooms. This is not a public page-image route.
  - https://www.nli.ie/collections/e-resources
- NYPL's surfaced 1937 record is a digitised **book jacket**, not interior pages.
  - https://old-digitalcollections.nypl.org/items/510d47db-d714-a3d9-e040-e00a18064a99

## Research consequence

The N/S ticket split is an edition-specific locator clue: ST-094 is a North ticket and p.94 lies within the 1947 edition's North section; the five North ticket numbers are below p.118 and the five South numbers above it. The `5E67` byte split independently proposes p.94 / word 103. This is worth a single exact physical-copy test, but it is still a locator hypothesis. No printed word, margin phrase, K08 HMAC, or K08 SHA256 result has been recovered.

A generic 1997 copy or a 1937 jacket cannot establish what David's particular copy says in the margin. The decisive evidence remains the actual copy's title/edition page, p.94 and the other ticket-indexed pages, the tea receipt/bookmark, and custody/provenance. If you have any exact 1947 interior scan or source image, please point me to it; I will avoid broad page-text searches and test only the frozen locator.
