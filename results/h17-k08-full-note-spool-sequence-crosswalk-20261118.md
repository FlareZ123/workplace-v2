# K08: N01–N24 / PS-0301–PS-0324 ordinal alignment — not an authenticated join

**Date:** 2026-11-18  
**Status:** Ordinal observation only. It does not recover K08 or establish a note-to-printer source link.

## Question

What is the observed relation between the 24 numbered desk/crew notes and the first 24 numbered spool jobs, and does it authenticate N23→PS-0323?

## Observation and method

Read the supplied crew-note file and spool reconstruction log. For each note number n=01..24, looked up job PS-261003-(0300+n) and recorded the attempt-1 ACK timestamp, class, and destination.

All 24 chosen offset-zero pairs exist. Their spool timestamps form a five-minute progression from PS-0301 at 07:05Z through PS-0324 at 09:00Z. PS-0300 is a distinct LABEL/store ACK at 07:00Z, five minutes before PS-0301.

| Note ordinal | Chosen job ordinal | Spool UTC | Class | Destination |
|---|---|---|---|---|
| N01 | PS-0301 | 07:05 | STORES | bench |
| N02 | PS-0302 | 07:10 | STORES | store |
| N03 | PS-0303 | 07:15 | RECOVER | desk |
| N04 | PS-0304 | 07:20 | LABEL | store |
| N05 | PS-0305 | 07:25 | LABEL | store |
| N06 | PS-0306 | 07:30 | RECOVER | desk |
| N07 | PS-0307 | 07:35 | RECOVER | bench |
| N08 | PS-0308 | 07:40 | LABEL | bench |
| N09 | PS-0309 | 07:45 | STORES | store |
| N10 | PS-0310 | 07:50 | STORES | store |
| N11 | PS-0311 | 07:55 | STORES | desk |
| N12 | PS-0312 | 08:00 | STORES | store |
| N13 | PS-0313 | 08:05 | STORES | store |
| N14 | PS-0314 | 08:10 | STORES | bench |
| N15 | PS-0315 | 08:15 | LABEL | bench |
| N16 | PS-0316 | 08:20 | STORES | desk |
| N17 | PS-0317 | 08:25 | LABEL | store |
| N18 | PS-0318 | 08:30 | RECOVER | store |
| N19 | PS-0319 | 08:35 | RECOVER | desk |
| N20 | PS-0320 | 08:40 | RECOVER | bench |
| N21 | PS-0321 | 08:45 | LABEL | bench |
| N22 | PS-0322 | 08:50 | LABEL | bench |
| N23 | PS-0323 | 08:55 | RECOVER | store |
| N24 | PS-0324 | 09:00 | LABEL | store |

The eight Emily-authored notes are N02, N06, N10, N13, N17, N18, N20, and N23. Under the chosen ordinal offset, these correspond to PS-0302, 0306, 0310, 0313, 0317, 0318, 0320, and 0323.

## Critical limitation: the alignment is not independently corroborated

The note file has **no per-note timestamps, queue IDs, or printer submission references**. The five-minute progression belongs entirely to the spool job series; it does not independently agree with note timestamps. Pairing two contiguous numbered sequences at offset zero is an ordinal coincidence unless an independent source establishes the join. All 24 pairings above were selected by that same numeric rule; the table does not authenticate it.

This is not a new discovery of a privileged source relation. The earlier independent source-first tests must govern interpretation:

- [Agent11 source-first role holdout](h17-k08-source-first-note-spool-join-null-holdout-20261109.md): four newly withheld note roles predicted **0/4** complete CLASS+DEST pairs at offset zero; the seven-role mapping scored **2/7**, ranking **26th of 105** offsets.
- [Agent17 retrospective metadata/byte-channel study](h17-k08-note-spool-metadata-bytechannel-holdouts-20261109.md): its five retrospectively selected roles produced a unique 5/5 offset-zero fit, but that selection was not independently predictive. The independent LABEL-role control scored **5/11**, with **48/105** offsets equally good or better. Agent17 explicitly withdrew the implication that metadata uniquely supports N23→PS-0323.

These negative controls do not prove that N23 was never printed or that no N23→PS-0323 relationship exists. They do show that this ordinal pairing does not privilege offset zero and must not be treated as a source-authenticated version locator. In particular, N20/PS-0320 and N23/PS-0323 are not demonstrated authoring/version links. PS-0300 is an earlier LABEL/store spool record, but its position five minutes before PS-0301 does not make it an authenticated envelope label.

## Follow-on AES/pageword hypothesis: unverified and not privileged

A separate exploratory hypothesis decrypts PS-0300, PS-0320, or PS-0323 payloads using AES-128-ECB with the K08 desk_nonce and interprets the plaintext bytes as page/word pairs. No source document says desk_nonce is an AES key, no authenticated note-to-packet join selects these jobs, and no exact page map has been applied. No phrase has passed the K08 HMAC and slot commitment.

The alternative eight-u16 absolute-offset interpretation has an additional vacuous feasibility issue: every unsigned 16-bit value is at most 65,535, and therefore every such value is automatically below the pinned Falcon transcription's 81,392-word count, for any key, packet, or source. Being in range is no evidence for AES, Falcon, or PS-0323. The page/word-byte interpretation is a separate conjecture and remains untested against an edition-faithful page map.

Do not broaden to arbitrary ciphers, modes, byte orders, offsets, or books. A single frozen complete-candidate test is defensible only if the exact already-pinned text/page cache is available; otherwise record UNTESTED (cache unavailable). Do not repeat public acquisition or access protected services.

## Reproduction and conclusion

The ordinal table is reproducible by matching note suffix n to job suffix 0300+n and reading attempt-1 ACK rows from the supplied spool log. This reproduces the chosen offset-zero alignment only; it does not test or validate a source-side join.

**Conclusion:** retain this table as a descriptive ordinal comparison, not as a K08 source relationship. The prior source-first holdouts supersede the earlier “strong structural evidence” interpretation. K08 remains unresolved; K04 remains unresolved; no candidate, source evidence, verifier, or acceptance commitment was modified.
