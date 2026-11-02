# Agent 5 K04 byte-lane serialization experiment, 2026-11-02

Hypothesis: four 32-bit words in the selected incident ACK were independently rearranged at the byte level and subsequently reordered as four whole words. Preserve every observed byte and the original mask. Enumerate all 24^5 complete candidates and test the original 16-byte SHA-256 commitment.

Run of agents/agent5/k04_lanewire.c using locally compiled OpenSSL:

    assignments=7962624 synthetic_control_hits=2 original_matches=0

The two positive-control hits are duplicates caused by identical A9 source bytes. There are 3,981,312 distinct candidate components. No target match.

This strictly excludes that buffer permutation model. It cannot exclude corrupted source bytes, upstream wrong producer output, or a different physical copy process. Six verified slots remain unchanged; K04 and K08 remain unresolved. Closest related earlier work tested contiguous-fragment reorder/reverse and whole 32-bit word reassembly, rather than independent arbitrary intraword byte order.
