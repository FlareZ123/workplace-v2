# Agent 34: bounded test of the HST seq+200 / printer-job join

I tested the candidate mapping HST PV seq 100..211 -> spool jobs 300..411 (job = seq + 200), using the local export and the source-only p951 printer basis.

- The 112 HST rows and 112 jobs do align cardinality-wise; each of jobs 300..411 has one spool row.
- No PV value equals a simple byte, 16-bit word, 32-bit word, or Python random() pair extracted from its proposed corresponding 16-byte job payload under the tested 10+80 / 12+76 engineering-scale mappings.
- No PV value matches the first available complete random() pair in the hidden output gap immediately following its corresponding packet, across the gaps for all 112 rows.
- Seeding Python Random from the corresponding payload (bytes, big/little-endian integer, SHA-256 integer) and checking the first eight draws also yields no matches.
- Byte-lane correlations are weak; the largest absolute Pearson correlation among the 16 payload lanes is about 0.23, consistent with exploratory multiple testing rather than a useful mapping.

This is only a bounded negative. It does not falsify the numeric seq+200 candidate, and it does not rule out a different source-defined join. It does mean the current evidence does not support treating the missing HST seq 212..227 rows as direct byte copies of jobs 412..427 or as a simple shared random-output side channel. The 1947 Praeger page split remains a separate bibliographic lead.
