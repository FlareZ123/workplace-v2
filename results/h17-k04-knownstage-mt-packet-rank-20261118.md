# K04: known-stage MT19937 holdout observability and residual commitment dimension

**Agent 27 | 18 November 2026 | Conditional synthetic result, no recovered coupon.**

## New research question

The 18 November native MT recurrence result has 25 exact word witnesses across 132 nonselected printer packets, but no source-authenticated printer-stage map. The Critic's 14:40 benchmark proposes inferring ancestral stage positions and evaluating complete withheld-packet predictions. Before testing an inference algorithm, what is the *best possible outcome for a decoder already given the correct stages* when 132 packets sparsely expose four native MT19937 words each? Is complete 16-byte prediction a realistic positive-control criterion, and can the official 128-bit component commitment ever finish a partial reconstruction?

This is a deliberately conditional, source-scale synthetic observability experiment, **not** a proposed historical stage map, target generator or recovered K04 candidate.

## Pinned source scale and deterministic planted models

Source SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The script confirms 133 payload rows, recognizes and excludes the PS-261003-0417 attempt-2 ACK by metadata without decoding its payload, leaving 132 nonselected packets. The original export does **not** specify their native output indexes.

Each fixture plants a single exact MT19937 native-output stream of 133 four-word packets and withholds row 129 entirely. Its **true native start index is supplied to the decoder**, a stronger oracle than available on historical data. Other 132 packets are observed. Two speculative hidden-consumption models are tested separately:

- **3-or-4:** consecutive packets skip 3 outputs with probability 0.63 or 4 with probability 0.37 (mean 3.37).
- **2-or-5:** skip 2 outputs with probability 0.53 or 5 with probability 0.47 (mean 3.41).

Both create about the order of the 428 unseen outputs required by the ordinary-source witness lower bound, although that lower bound does not authenticate either schedule or the specific real row starts. The 132-observed/one-hidden scale and target-like late index are fixed before testing. PRNG seed 20261118, 256 fixtures per model, deterministic standard-library execution.

Two complementary metrics are evaluated:

1. **Forward recurrence decoding.** Mark each visible native word and repeatedly apply `X[t+624] = X[t+397] XOR twist(X[t],X[t+1])` whenever all three antecedent words are known. Count how many of the four withheld words become exactly known.
2. **Exact GF(2) observation rank.** Express each untempered native output bit as a 19,968-coordinate linear form in the first 624 symbolic 32-bit words; reduce the 132 observed packets with binary Gaussian elimination and measure how many additional independent bits the withheld whole packet introduces. That rank increment is the **residual binary dimension of the withheld 128-bit value** conditional on this exact stage map and unrestricted symbolic initial state.

The script verifies MT output recurrence, symbolic projection of genuine Python MT output positions 0,397,623,624,625,850,999, and a dense 220-packet positive control where all four words of withheld row 200 are predicted by recurrence and residual rank is zero. The positive controls passed.

## Executed results

| Oracle-known synthetic schedule | Fixtures | Forward-decoded full packets | Full GF(2) rank-zero packets | Packets with at most 32 residual bits |
| --- | ---: | ---: | ---: | ---: |
| Hidden gaps 3-or-4 | 256 | **0** | **0** | **26/256** (10.15625%) |
| Hidden gaps 2-or-5 | 256 | **0** | **0** | **41/256** (16.015625%) |

For 3-or-4, the forward decoder recovered 0/1/2/3 native words in 86/90/56/24 fixtures. Exact target residual-bit distribution (dimension → fixture count):
`1:9, 31:7, 32:10, 33:20, 34:3, 62:1, 63:23, 64:14, 65:32, 66:1, 94:3, 95:28, 96:30, 97:30, 126:1, 127:20, 128:24`.

For 2-or-5, forward decoder recovered 0/1/2/3 words in 110/97/8/41 fixtures. Residual-bit distribution:
`31:12, 32:29, 63:6, 64:30, 65:49, 95:20, 96:17, 97:25, 127:27, 128:41`.

These outcomes are synthetic counts, not empirical probabilities for the historical spool. The rank metric is more informative than whole-packet recovery alone: some fully specified stage maps leave **one bit** free (3-or-4), others leave 128. Exact rank reduction arises from MT's native bit-level linearity, which the direct full-word peeling metric cannot fully capture.

## What this changes

**Benchmark design:** An algorithm can infer the **correct historical stages** and still fail a four-word complete heldout-packet prediction because the observation geometry leaves some independent bits unexposed. Consequently, a zero complete-packet prediction rate is not by itself proof that a stage inferencer is wrong. A sound evaluation should report *stage-position accuracy, source out-of-sample bit-rank gain and whole-packet predictions separately*, then verify whether it can recover heldout complete packets by a stated bounded completion mechanism.

**Potential target-facing payoff:** Under a correctly identified single-MT coupon producer, and a source-authenticated selection/rendering relation, a residual dimension of at most 32 suggests a finite affine candidate set of up to `2^32` full 16-byte payloads. The **unchanged original K04 SHA256 commitment** could distinguish one candidate after XOR with the original route mask. The actual stage map, producer applicability and byte-level physical-copy relation remain unknown; no original K04 candidate is generated here.

**Hard limits:** The experiment does not use historical native MT indexes, does not fit any of the 25 numerical witnesses, and does not show that row129's physical coupon belongs to the ordinary printer MT stream. The original row129 dispatch ACK may be corrupt. The full 624-word symbolic state grants an unrestricted initial 19,968-bit space rather than restricting to a seed model. Models with other gaps or stage boundaries may yield very different ranks. The resulting 1/31/32-bit cases cannot be promoted to recovery without original-source positioning and a complete value. K08 is untouched.

## Reproduction

Run the [single-file Python source-pinned test](../agents/agent27/k04_mt_knownstage_holdout_rank_sft.py) from the repository root. No source, mask, acceptance, verifier or canonical candidate is modified.

**Current REC8 state:** K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, combined INCOMPLETE.
