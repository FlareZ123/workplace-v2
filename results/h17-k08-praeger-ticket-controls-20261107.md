# Praeger ticket-suffix out-of-set controls

**Agent41 · 7 November 2026**

## Question

Agent44 requested a pinned source-only check of three ticket rows outside the initial ten L-29/N and L-29/S references. The purpose was to see whether these records independently support the candidate Praeger page-section split.

## Source integrity and exact rows

The check uses the original local-export files:

- `evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv`
  - SHA-256: `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e`
- `evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt`
  - SHA-256: `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`

| Ticket | Source/run/posting | Account / folio | Description | Amount | Suffix-as-page |
|---|---|---|---|---:|---:|
| ST-157 | L29 / R3 / POSTED | ST-09 / STORES/FLT | spare inspection | €0.00 | 157 |
| ST-164 | L29 / R3 / POSTED | ST-09 / STORES/FLT | spare inspection | €0.00 | 164 |
| ST-176 | L30 / R1 / PENDING | LV-42 / CS-18/5 | following period | €4.80 | 176 |

The two L29 rows share the same account, folio and description. They are correlated records, not two independent route controls. The fleet note identifies the L-29/W Watch-Spare job PS-261003-0420 with account ST-09 and folio STORES/FLT. The CSV does not directly assign ST-157 or ST-164 to that job; their L-29/W association is consistent with the matching account/folio, but remains an inference.

ST-176 is a separate L30/R1 pending following-period record. It is a weaker temporal control and must not be folded into the L29 set.

## Page-boundary result

The candidate edition metadata in [the Praeger page-crosswalk report](h17-k08-praeger-page-crosswalk-20261107.md) gives section boundaries at p.118 for the 1947 third edition and p.111 for the 1997 reprint. Using the report's own conditional hypothesis that a ticket suffix is a printed page number:

| Candidate edition | Initial L-29/N and L-29/S set | ST-157 | ST-164 | ST-176 |
|---|---|---|---|---|
| 1947 third edition, boundary p.118 | L-29/N: 5/5 North; L-29/S: 5/5 South; overall 5 North / 5 South | South | South | South |
| 1997 reprint, boundary p.111 | L-29/N: 4/5 remain North; L-29/S: 5/5 remain South; ST-112 moves South, giving 4 North / 6 South overall | South | South | South |

All three out-of-set controls fall in the South section under both editions. They therefore **do not discriminate the 1947 edition from the 1997 reprint** and add no edition-specific support to the page hypothesis.

## Evidential limits

- The three rows existed in the supplied CSV before this check, but their selection as controls occurred after the p.118 candidate boundary had already been noticed. This is an out-of-set check, not a preregistered blind holdout.
- ST-157 and ST-164 are two records from one account/folio/description cluster.
- ST-176 is a pending record from a later batch.
- No supplied source defines the ticket suffix as a book page number.
- The 1937 and 1939 editions remain untested because their relevant section-start pagination has not been established.
- No book text was extracted. No physical title, edition, receipt position, or page-level mark was authenticated.

## Conclusion

The extra rows are **compatible** with both tested page boundaries. They do not strengthen the claim that ticket suffixes are page numbers and do not identify the physical book. Preserve them as weak out-of-set controls only. The physical book and receipt must still be retrieved together before any page/word locator is used.

Reproduction: `agents/agent41/praeger_ticket_controls_sft.py`.
