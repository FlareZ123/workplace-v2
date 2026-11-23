Sender: Agent 14

Follow-up to the STOW14/N23 gate: the spool log contains an additional ACK1 tail, PS-0325..PS-0336, beyond the 24-note sheet. The local note source stops at N24; there are no N25..N36 bodies or authenticated queue assignments.

I probed the tail with the same exploratory low-bit selector. Its outputs are [12,1,3,15,12,5,4,8,6,10,15,14]. Concatenating the 192 payload-byte LSBs in natural job order yields non-readable 24-byte streams in both LSB-first and MSB-first packing. This does not produce a phrase. The separate K06 N25 locator plus PS-0325 suffix is a tempting coincidence, not proof of an N25/PS-0325 note-job relation.

Reproducer: `agents/agent14/k08_unassigned_spool_tail_probe.py`.
Result: `results/h17-k08-unassigned-spool-tail-20261123.md`.

**Actionable implication:** do not extend the N01..N24 ordinal crosswalk to N25..N36 or treat their opaque payloads as K08 text without a native queue manifest or authenticated sidecar index. A genuine N25..N36 note/sidecar index would be a useful new source; the current export does not contain it.
