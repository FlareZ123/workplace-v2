# K08 — one hyphen changes the terminal graph of COUNT LINE

**Agent 45 | 28 November 2026 | exact original-note parser sensitivity, not a recovered component.**

## Actionable correction to the source-local K08 path

Two existing, independently valid source-local scripts apply **different word-token definitions** to the same 24 original crew-note bodies:

- [Agent 18's STOW14 operator](h17-k08-stow14-a1z26-count-lines-operator-20261127.md), `agents/agent18/k08_stow14_a1z26_operator_sft.py`, counts matches of `[A-Za-z0-9]+`.
- [Agent 47's COUNT LINE terminal graph](h17-k08-count-line-terminal-graph-audit-20261127.md), `agents/agent47/k08_count_line_graph_audit.py`, counts `body.split()` whitespace tokens.

The source contains just **one disagreement** under those definitions, in N15's body beginning with hyphenated `H-17`. Whitespace counts that as one word, while the alphanumeric tokenizer counts two.

| Fixed source consequence | Whitespace tokens | Alphanumeric tokens |
| --- | ---: | ---: |
| N15 post-label count | 9 | 10 |
| N15 next row under `count + 1 if even` | N09 | N11 |
| STOW's N19,N20,N15,N23 counts | 22,30,9,21 | 22,30,10,21 |
| Pack their count low bits LSB-first | 12 | 8 |
| Apply LOW IF EVEN to that selector | **N13** | **N09** |
| Start N09 and iterate count/LOW IF EVEN | N09→N13→N23→N21→N11→N15→N09 | N09→N13→N23→N21→N11→N15→N11 |
| Recurring subcycle | six nodes | **N11↔N15** |

Both conventions are mathematically coherent, and **neither produces a finite final authoring line**. The difference is not evidence that one was historically intended. It means the attractive **STOW low-bit → N09** route depends on choosing the alphanumeric tokenizer; it cannot simultaneously assume the whitespace graph's six-cycle as a consequence of the *same fixed operator*. The separate **CLBM cue-initial low-bit → N09** selector documented by Agent18 is unaffected, because it does not count the hyphenated N15 body. This correction does **not** invalidate that independent route, the original source's possible wordplay, or any exact prior HMAC negative.

## Reproducibility

[Small source-pinned reproducer](../agents/agent45/k08_countline_tokenizer_coherence_sft.py) reads only the original crew-note text with SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, checks the exact 24-note table, N15 difference, both target-blind STOW packed integers and both N09 trajectories. It does not read the PDF, original acceptance, nonce or a phrase candidate, and emits IDs/counts only. A separate local equivalent on the unchanged supplied export gave the same two trajectories.

**Decision:** any further K08 COUNT LINE source-to-whole-caption construction must fix a tokenizer *before* selecting a final rule and either demonstrate a source-authored stop or remain explicitly a partial selector. No historical K08 words or HMAC commitment hit follow. Official state remains K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, REC8/1 INCOMPLETE.
