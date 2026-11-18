# K08: full N01–N24 / PS-0301–PS-0324 sequence alignment

**Date:** 2026-11-18  
**Status:** New structural observation; no K08 component recovered.

## Question

Is the previously noticed N20→PS-0320 and N23→PS-0323 alignment isolated, or does the full numbered desk-note series map onto the early printer-spool sequence?

## Method

Read the supplied `evidence/crew/noticeboard-and-desk-notes.txt` and parsed the retained attempt-1 ACK records in `evidence/print/spool-reconstruction.log`. For each note number n=01..24, looked up job `PS-261003-(0300+n)` and recorded its timestamp, state, class, and destination.

## Observation

All 24 numbered notes have a matching attempt-1 ACK job. The timestamps form an exact five-minute progression from N01/PS-0301 at 07:05Z through N24/PS-0324 at 09:00Z. The orphan PS-0300 record is a LABEL/store ACK at 07:00Z, exactly five minutes before N01's corresponding job.

| Note | Job | UTC | Class | Destination |
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

The eight Emily-authored entries are N02, N06, N10, N13, N17, N18, N20, and N23. Their corresponding job sequence is therefore PS-0302, PS-0306, PS-0310, PS-0313, PS-0317, PS-0318, PS-0320, and PS-0323. In particular, N20/PS-0320 and N23/PS-0323 are 15 minutes apart in the same ordered series, rather than two isolated numeric coincidences.

## Interpretation

The exact one-to-one numbering and five-minute cadence are strong structural evidence that the N01–N24 note series and PS-0301–PS-0324 spool sequence are related. PS-0300 is a separate prelude candidate, not a member of that 24-item alignment. This makes PS-0320 and PS-0323 useful authoring/version locators and gives PS-0300 a separate orphan-label role.

The evidence does **not** prove that the payload bytes encode note text, that each job rendered the corresponding note, or that any ACK authenticates physical output. Class and destination vary across the sequence; no uniform class/destination rule explains the mapping. Treat the relation as a strong structural crosswalk, not a cryptographic or physical-output proof.

## Follow-on hypotheses (unverified)

A bounded exploratory test treated the documented K08 desk_nonce as an AES-128-ECB key and decrypted the 16-byte payloads of PS-0300, PS-0320, and PS-0323. The plaintext blocks can be interpreted as eight byte-pairs, potentially page/word coordinates into the book mentioned in the mail. This AES use is not documented by the source; the book identity/page map is not authenticated; and no phrase has been validated against the K08 HMAC and slot commitment. Do not promote this as a recovery. Test only if an already available, pinned book/page cache exists; do not access protected services or repeat public acquisition.

Direct SHA-256 of the raw PS-0300, PS-0320, and PS-0323 payloads does not match the K08 slot commitment.

## Reproduction

The mapping is reproducible by matching note suffix n to job suffix 0300+n and reading the attempt-1 ACK row from the supplied spool log. No source files, candidate values, verifier, or acceptance commitments were modified.

**Conclusion:** retain the 24-item note/spool sequence alignment as a strong K08 locator. It is a new source-dependent relationship, but it does not recover K08 or authenticate the physical envelope text.
