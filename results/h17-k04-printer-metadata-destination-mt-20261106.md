# K04: source-conditioned printer DEST next-output signal and exact-writer counterexamples (6 Nov 2026)

**Agent25, original archive unchanged.** Hypothesis: printer destination category may be selected using the next MT19937 native draw after each opaque 16-byte spool packet. This is a cross-field producer hypothesis, distinct from the copied ACK2 byte-repair or K05 stage-jitter donor family. The source correlation is stronger than 10,000 class-preserving shuffled-label controls. Its simplest full writer is source-inconsistent, and it does not recover any missing key component. K01/K02/K03/K05/K06/K07 remain PASS; K04/K08 remain MISSING; REC8/1 combined INCOMPLETE.

## New source signal

Source: original printer spool, SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Reuse the exact Agent49 source-only p951 MT19937 basis in agents/agent49/k04_p951_symbolic_basis.py, containing 15,365 independent source equations, fitted to 132 intact payloads **excluding the selected ACK2 row129**. The p951 native STARTS chronology is a conditional source-compatible fixture, not historical proof of the physical producer.

At each row with native start stage q, predict the two highest bits of tempered output q+4. Interpret the two-bit code as 0=store, 1=desk, 2=bench, and 3=rejected draw. Of the nonselected rows, **26** have both source-determined bits and code below 3; **20/26** actual DEST labels agree. The six contradictions occur at zero-based original spool rows **5, 37, 71, 78, 110, 132**. Eleven further source-determined code3 values require a rejected draw rather than a destination.

The winning rule emerged from 4 native/tempered high/low bit views, 25 offsets (-12..12), and six label-code permutations. Exactly **600 candidate rule assignments** met the minimum of 20 source-determined nonreject observations. The unique best had the q+4 tempered-high 20/26 match. A single-rule three-category binomial tail is around 6.73e-6, **before correcting rule selection**.

A reproducible NumPy seed20261105 randomization reoptimizes all 600 rules separately for each shuffled original DEST vector. With 10,000 frequency-preserving **global** permutations, **1** reproduced or exceeded the best accuracy (add-one Monte Carlo p 0.00019998). With 10,000 **within-CLASS** permutations that preserve destination frequencies within LABEL/STORES/RECOVER, **0** reached it (add-one p 0.00009999). Under the fixed winning rule, source rows 0..63 give 5/7 and the later rows give 15/19 hits. This split is descriptive following full-model selection, not a prospective heldout.

Important interpretation: finite randomization accounts for the specified 600 alternatives, but cannot correct for the population's many previously explored printer chronologies and other families. Therefore this is a noteworthy **conditional association**, not a proven generator.

## Source-only exact emitter falsifier

Test whether each of 127 consecutive ordinary packet pairs consumes two metadata categories from successive standard two-bit getrandbits/randrange(3) draws, with code3 rejections allowed anywhere before those two category draws. The source-only test includes both orders (DEST before CLASS and vice versa), all 6-by-6 category-code maps, unknown source bits permitted optimistically to match any compatible rejection/accepted code, and no other hidden draws after both fields.

**Best of all 72 configurations supports 80/127 entire ordinary gaps; 47 original source contradictions remain.** Best ordering is DEST then CLASS, destination code store0/desk1/bench2 and class mapping LABEL0/RECOVER2/STORES1. This rejects the *specified* no-other-hidden-output two-field issuer despite the apparent correlation. Other draw histories, stage changes, selected/copy regimes or a different generator remain outside this falsifier.

At original row128 the recorded destination is bench. If the speculative q+4 rule were valid at this exceptional row, it would set the top two tempered bits of selected stage q951 to code2. Adding just these equations increases exact source rank **15,365 to 15,367**, leaving at least **126 of 128 selected coupon bits unknown** under the conditional model. The proposed issuer has already failed many intact rows. None of these bits is historically authenticated, and no full K04 coupon was constructed.

## Reproduction and next decision

[Source-pinned single-file Python/NumPy reproducer](../agents/agent25/k04_metadata_mt_discriminator_sft.py) executes the complete 600-model grid, both 10k shuffle controls, the 127-row two-field optimistic rejection scan and the rank-two conditional target projection without reading the original K04 hash. Original source, official verifier, acceptance and canonical candidate are untouched.

A distinct, independently anchored original issuer/capture model might exploit the conditional destination alignment. Do not promote the failed model into a physical coupon value, or extend the saturated stage1406/K05 coupon family. No authenticated K04 physical bit and no author-final K08 word were recovered.