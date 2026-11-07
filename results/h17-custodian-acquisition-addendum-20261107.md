# Custodian acquisition addendum: K04/K08 source originals (7 November 2026)

This addendum narrows the next retrieval to original source objects that can close the remaining K04/K08 gaps. It incorporates the newly decrypted BX25-08 property annex and the confirmed HathiTrust Part I catalog item. It is an acquisition request, not a claim that any missing source contains the target value.

## Priority 1: FA-18 archival workstation scan set

The BX25-08 A3 property annex confirms **FA-18 = Network service desk and local archival station**, carry-forward maintained. The retired-office bookmark identifies:

- `R:/IT/desk-images/oldscan/scanrelease.txt`
- The complete `R:/IT/desk-images/oldscan/` directory
- The old capture terminal's four-position numeric release setting and Risk desk paper key register

Request the original directory, not only the setting file. Preserve file names, timestamps, original image bytes, sidecars, directory structure and any scan/caption manifests. This is the strongest route to the missing photo/galley-caption stack, book/map verso scans and the K08 keeper wording.

## Priority 2: FA-17 original print and property records

The same BX25-08 annex confirms **FA-17 = North office printer / cassette cabinet**, under H17-POL-17/A3, carry-forward maintained. Request:

- The original `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx`, not the BX25/08 transfer copy
- The September cassette-return index `R:/Stores/returns/SEP26/index.htm` and both signed North/South cabinet binder pages, front/back and attachments, preserving serials, ticket references and custody marks
- The Risk desk paper key register and original A3 folio/copy-stage attachments
- Raw `.SPL/.SHD` files and metadata for selected job `PS-261003-0417`, including all attempts and the actual 18:02 RECOVER ACK object
- The original physical 16-byte coupon and its custody/return-binder record

The reconstructed spool log explicitly marks payload integrity unverified. The last-ACK XOR candidate fails the official K04 commitment; do not treat a reconstructed payload as the physical coupon.

## Priority 3: Cowper Part I scan

HathiTrust record [100485750](https://catalog.hathitrust.org/Record/100485750) lists **Full view pt.1** at Harvard, item `hvd.hn5w2p`:

https://babel.hathitrust.org/cgi/pt?id=hvd.hn5w2p

Request the title page/imprint and the frozen North pages [94, 81, 106, 99, 112], preserving original page labels and image bytes. The five Google Books zoom-1 aliases were identical placeholders; the official HathiTrust viewer could not be opened by our tools. A human browser or authorized library export is required. An Internet Archive copy (`sailingtoursyach0000cowp`) is a 1985 facsimile of the 1895 edition and print-disabled; it is not a substitute for the required Part I copy. See [IA comparator report](h17-k08-cowper-internet-archive-1895-facsimile-20261107.md).

## Priority 4: Electronic correspondence index

The BX25-08 annex labels `https://noyes-energy-group.pages.dev/` as the electronic correspondence index. The public root is a marketing site; `robots.txt` disallows `/admin` and `/api/`, and `/admin` is a username/password portal. Request the actual correspondence-index export from the custodian. Do not submit credentials or attempt the disallowed paths.

## Preservation requirements

For every returned object, preserve the original bytes, source path, owner/custodian, transfer time, file metadata, hashes, page labels, and any chain-of-custody record. Keep transfer copies distinct from originals. Do not change the frozen Cowper edition/page order/counting convention or infer K04 from reconstructed spool payloads.
