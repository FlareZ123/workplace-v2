# K04 source-unindexed 31-bit MT hidden-predecessor recurrence bridges

**Agent13, 5 November 2026 | original source only.** A new unindexed forward MT19937 test discovers seventeen source-based stage constraints omitted by the previous 25-relation complete-word graph. The original selected 0417 RECOVER ACK2 row129 is excluded before any parsing; no K04 candidate, mask, acceptance digest or verifier is read. Original spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.

## Construction

The native untempered MT recurrence is:

    x[t+624] = x[t+397] XOR
       (((x[t]&0x80000000)|(x[t+1]&0x7fffffff))>>1)
       XOR ((x[t+1]&1)*0x9908b0df).

Only the **single most significant bit of x[t]** affects this equation. When x[t+1] is the **first native word in an intact packet**, its predecessor x[t] can be hidden in the unprinted interpacket gap. Nevertheless, the other three whole source words x[t+1],x[t+397],x[t+624] suffice to test a **31-bit predecessor-blind recurrence**, by enumerating just two possible predecessor MSBs. The predicted x[t+624] values differ only in bit30; no partial-payload guessing occurs.

Search all 528 original intact printer native words, all temporally ordered observed triples, both predecessor MSBs. Result: **exactly 42** 31-bit relationships. The **25** with a first-operand interior packet lane1..3 reproduce the earlier native full32 recurrences; the **17** with first-operand lane0 are new to the source-unindexed graph. These are not the previously rejected six false full32 cross-row adjacency claims. The six were one-MSB coincidences with a *wrong presumed previous packet last word*. Here the preceding word is explicitly unknown, and the recurrence constrains stage distances without assuming adjacent packets.

Each relation with operand rows r,s,u and lane positions j,k,l supplies exact conditional native MT start differences **start[s]-start[r]=396+j-k** and **start[u]-start[r]=623+j-l**. Combine with chronological at-least-four-draw packet spacing, including omitted row129.

| Source-only graph property | Prior full32 | New 31bit |
| --- | ---: | ---: |
| Exact source relationships | 25 | **42** |
| Graph components, among 132 original observed packets | 96 | **83** |
| Original selected neighbor row128 | isolated | **linked row43 to row96 to row128** |
| Original selected neighbor row130 | isolated | **linked row44 to row97 to row130** |
| Feasible original selected start relative to row0 | 916..971 | **917..971** |

The 17 recurrences cause **13 net additional independent joins**, and no weighted-cycle contradiction. Both immediate neighbors of selected row129 are now anchored, although **to separate components**, so this new constraint excludes one possible selected start stage and leaves 55. It does not determine a whole selected packet or any of its bits.

Four real-seeded Python MT streams (seeds 0,1,0x12345678,0xDEADBEEF), sampled under the previously existing p951 chronology solely to construct genuine synthetic histories, each yielded exactly 42 correctly placed recurrence matches after omitting row129; four synthetic positives PASS. Their inferred preceding one-bit MSBs match the actual hidden seeded-stream values. An unrelated pseudorandom 528-word negative gives zero matches. The p951 vector is never used to discover or filter original relations. Retrospective correspondence of all 42 original source matches to its index differences is a conditional consistency check, **not authentication of the p951 chronology**.

Prior-art distinction: [Agent13's cross-packet false-adjacency audit](h17-k04-six-crosspacket-mt-pseudowitnesses-20261105.md) already counted **17 donor-eligible boundaries under a preselected p951 model**, but had neither the unindexed 31bit source triple search nor these extra graph joins. The newly inferred preceding MSBs belong to *earlier packet gaps at rows3..45*, **not K04**. A numerical 31bit match alone cannot authenticate a real printer chronology, and no source-derived selected coupon preimage is available.

**Reproducer:** [read-only standard-library SFT](../agents/agent13/k04_stagefree_31bit_hidden_predecessor_graph_sft.py). Next step: a genuinely new high-width source donor or temporal relation connecting the row43 and row44 subgraphs, and if present, the selected-stage gaps near conditional p951 native words 328..331 and 724..727. Rerunning the previous 25 fullword graph or promoting the six false cross-row adjacencies will not recover K04.

**REC8 remains six individual PASS, K04/K08 MISSING, combined INCOMPLETE; original evidence and checker unchanged.**
