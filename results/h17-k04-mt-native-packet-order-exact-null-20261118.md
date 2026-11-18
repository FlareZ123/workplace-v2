# H-17 K04: exact source-preserving MT packet-order null

**Agent 32 | 18 November 2026 | Independent source-only test, no recovery claim**

## Question

Agent 17 reported 25 exact MT19937 native-word recurrence relationships among intact printer payloads, far beyond an independent-random-word null. Do these relationships also align with the **actual packet chronology**, conditional on retaining every one of the original 16-byte payload values and their within-packet word order?

## Reproduction and new method

The original spool source is pinned to SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. This experiment excludes the selected PS-0417 ACK2 record at row129 **before payload decoding**. Parse the other 132 intact packet values as little-endian four-word records, inverse-temper with native MT19937, and enumerate all distinct whole-word identities of the form:

    word(d) = word(c) XOR twist(word(a), word(a+1))

Here a and a+1 are adjacent words inside one intact packet, and c,d belong to two distinct other intact packets. Because XOR is commutative, c and d can be exchanged. The exhaustive search makes **no MT stage chronology assumption**, reads no disputed selected payload, and never loads the K04 route mask or acceptance digest.

**Original result:** 25 full-word identities, corresponding to 18 distinct triples of packet identities and 36 distinct directed precedence edges. Every source packet containing the adjacent-word parent precedes both other packets in the recorded source order. The first 128 ordinary packets alone yield 23 identities, 16 triples and 32 precedence edges.

The conditional null uniformly permutes the original **whole** intact packets. It retains every value-level XOR coincidence and every within-packet pair. For all the identified identities to have a forward MT interpretation under such a permutation, the parent packet must precede the other two packets. The related identities share packet rows, so one must deduplicate edges and count valid linear extensions of the resulting dependency graph exactly.

| Original packet set | Full-word identities | Distinct packet triples | Connected dependency components | Exact probability of all-forward ordering |
| --- | ---: | ---: | --- | ---: |
| All 132 intact packets | 25 | 18 | Four 5-node, ten 3-node | **16 / 2,989,355,625 = 5.3523240481 × 10^-9** |
| First 128 ordinary packets | 23 | 16 | Three 5-node, ten 3-node | **8 / 199,290,375 = 4.0142430361 × 10^-8** |

For each five-node component, 16 of 120 orders satisfy its prerequisites (2/15); for each three-node component, 2 of 6 orders satisfy them (1/3). Components have disjoint packet nodes, giving the displayed exact product of rational probabilities. This treatment accounts for the overlap among 25 identities rather than incorrectly multiplying 25 independent probabilities. An auxiliary 512-trial whole-packet permutation pilot (fixed seed 20261118) gave mean 8.373 forward identities and maximum 18, compared with the source 25.

## Reproduction and controls

The independent, standard-library [single-file test](../agents/agent32/k04_mt_packet_order_null_sft.py) verifies the original source hash, obtains both exact values above, tests an actual seeded CPython MT recurrence at native indices 0,1,397,624 and checks 10,000 random temper/inverse-temper round trips. It reproduces both source results and positives on the unmodified local 46-file ZIP export.

## Evidence boundary and research decision

This is **an exact conditional probability under the stated uniform whole-packet order null**. It is neither a posterior probability that the historical printer was MT19937 nor a proof of a particular absolute output stage or input seed. The real packet order was written by a process; a uniform random order is an intentionally adversarial comparison, not a model of actual human job dispatch. The value matches were identified independently of source order; temporal orientation supplies the tested additional signal.

The selected 18:02 physical PS-0417 coupon is still unconstrained by these identities and remains unavailable. The current K04 original commitment has **no new match**. The finding strengthens the source-guided MT stream hypothesis and supports prioritizing a genuinely authenticated producer/output-stage bridge rather than more unsupported algorithm or byte-layout sweeps. K08 final wording remains missing. Combined REC8/1 acceptance remains incomplete.
