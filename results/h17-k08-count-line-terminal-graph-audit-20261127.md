# K08 COUNT LINE terminal-rule graph audit (27 November 2026)

**Agent 47 — no key recovery.** The previously reported STOW14-derived rule maps a note number to the post-label whitespace word count, adding one when that count is even. That rule had been used as a two-hop selector N09→N13→N23, but did not specify how or when to terminate.

## New complete-graph consequence

Applying the same fixed transition without adding a post-selected stop rule returns **N09→N13→N23→N21→N11→N15→N09**. The sequence is a six-node directed cycle. The 24-note graph contains exactly one directed cycle: **22 of 24 starting notes eventually enter it**, while only N10 and N20 exit immediately (to 25 and 31, respectively). Its direct off-graph destinations are 25 and 31. N23 is therefore not an intrinsic terminal of this count/parity operator: extending precisely the same operation from N23 leads to N21. There is no unique final authoring line from the transition alone.

This is not a rejection of the STOW14 note selector, only a distinction between *reachability* and *finite final wording*. To make this method constructive one must specify an independent stop rule (e.g. a source-format marker fixed before testing) and an exact text emitter over the bounded traversal. Simply stopping at N23 because it mentions the target artifact is an interpretive, not mathematical, endpoint.

## Reproduction and source boundaries

[Reproducer](../agents/agent47/k08_count_line_graph_audit.py) uses the unchanged plain-text crew notes, splits at the first colon-space for a post-label body when present, counts whitespace-delimited tokens, and uses the existing even→next-row convention. It checks the exact cycle and all 24 transitions. It loads no PDF, private material, target commitment, K08 nonce or output candidate and prints only note IDs and graph statistics. It does not emit or test guessed wording.

**Disposition:** exact graph property under the stated parser and transition; a negative on *termination by iteration alone*, not a complete phrase exclusion and not an accepted K08 component. Preserve the six-PASS/two-MISSING state. The next experiment must justify a source-fixed stopping/emission rule without another unconstrained wording search.
