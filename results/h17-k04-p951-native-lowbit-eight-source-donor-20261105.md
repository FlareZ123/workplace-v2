# K04 p951: native low-bit oracle and eight-stage target-causal donor localization

**Agent 15 | 5 November 2026 | Exact conditional GF(2) information geometry.** Original six REC8 components remain PASS, K04/K08 remain MISSING, combined INCOMPLETE. **This work recovers no authentic K04 bits.** It characterizes a previously untested path by which *actual independent native-state observations*, if found, could reduce or reconstruct the selected original coupon under the unverified p951 MT19937 producer.

## Different question from the earlier tempered metadata ceiling

[Agent 2's prior ideal metadata analysis](h17-k04-mt-perfect-metadata-oracle-rank-ceiling-20261104.md) proved that even 12 exact **high tempered output bits** at all 435 hidden nonselected printer stages leave the selected 128 native-stage bits entirely unconstrained. That result covers the usual Python-style high-bit `randrange(3)` metadata oracle and remains valid.

Here the mathematical oracle exposes a different *data representation*: lower or higher bitplanes of **internal, untempered native MT19937 words**. The 32-bit MT tempering matrix maps contiguous native bitplanes into different combinations of output bits. A normal public PRNG output is tempered; the original evidence has **no authenticated leak of the hypothesized native bitplanes** at the crucial hidden stages. This distinction is essential.

## Exact source reconstruction

The unchanged `resources/evidence/print/spool-reconstruction.log` has SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The existing [Agent49 p951 symbolic source basis](../agents/agent49/k04_p951_symbolic_basis.py) reads 132 intact original 16byte rows, excluding the selected row129, and produces original rank **15,365**. Its hypothetical selected packet would occupy native output stages **951,952,953,954**.

Between the first and last surviving spool positions, there are **435** unprinted, nonselected MT output stages. Give a perfect *hypothetical* oracle specific bit positions at every one, then reduce all 128 selected native-stage symbolic equations modulo the original source plus these hypothetical donor equations. All ranks are exact binary linear algebra, independent of the oracle bit values or the target commitment.

| Hypothetical original-independent oracle on every one of 435 hidden stages | Incremental source rank | Residual selected K04 quotient |
| --- | ---: | ---: |
| No oracle | 0 | **128** |
| Lowest one **native** bit | 233 | **128** |
| Lowest two **native** bits | 376 | **124** |
| Lowest twelve **native** bits | 1,806 | **84** |
| Highest twelve **native** bits | 1,802 | **84** |
| Lowest sixteen **native** bits | 2,378 | **68** |
| Lowest twelve **tempered** output bits | 2,838 | **128** |
| Highest twelve **tempered** output bits | 2,838 | **128** |
| All 32 native or tempered bits | 4,572 | **0** |

The lowest-twelve-native-bit oracle fixes **bits 0..10 of each of the four selected native words**: four identical 32bit observability masks `000007FF`, 44 linearly independent target bits. The highest-twelve-native-bit oracle also yields 44 total target relationships, though only 32 are individually fixed native bits (masks `66F00000`). A correct *full quotient reduction* is required to count cross-bit relations; simply halting after the first unsupported source pivot overcounts target dimension. The public SFT performs full reduction.

## Stronger localization: only eight source stages are needed

The MT19937 native recurrence for each selected stage `q` is

```text
X[q] = X[q-227] XOR twist_mix(X[q-624], X[q-623])
```

where `twist_mix(a,b) = (((a & 0x80000000) | (b & 0x7fffffff)) >> 1) XOR (0x9908b0df if b bit0 else 0)`. The relevant earlier stages are `q-624 = 327..330`, `q-623 = 328..331`, `q-227 = 724..727`. For reconstructing low selected bits, the higher leading bit of `q-624` does not matter. These yield **eight crucial unprinted native stages**:

`328, 329, 330, 331, 724, 725, 726, 727`.

| Exact hypothetical observations from those **eight** stage words alone | New source rank | Residual selected native quotient |
| --- | ---: | ---: |
| Lowest two bits at each word: 16 bits | 16 | **124** |
| Lowest twelve bits at each word: 96 bits | 96 | **84** |
| All 32 bits at each word: 256 bits | 256 | **0** |

For each of these three native-bit widths, **all eight stage words provide exactly the same target rank and individually determined target-bit masks as the corresponding perfect 435-stage oracle**. Thus under this exact linear producer, observations from these eight specific state positions are sufficient to capture all of the target information carried by uniformly observed native low bitplanes across hundreds of earlier gaps. Complete 256bit knowledge of the eight stages determines all four selected native words. The SFT also asserts the full 128 symbolic twist equations directly, independent of the rank test.

Neither the 96 native donor bits nor the full 256bit stage quartet pair has been found in authentic evidence; the observations above are counterfactual. They do not authenticate physical transfer into the selected ESC-N coupon. Even a reconstructed mathematical output must be reduced with the unchanged route mask and tested against the original K04 commitment before acceptance.

## Reproducer and source gate

[Agent15 portable standard-library SFT](../agents/agent15/k04_mt_lowbit_oracle_sft.py) reuses original Agent49 symbolic source, asserts the original rank, omitted row129, exactly 435 hidden stages, all displayed quotient figures, eight-source equivalences and direct MT twist equations. Executed locally on the matching supplied ZIP with a source-equivalent adapter; the committed SFT was remotely read back byte for byte. No original evidence, acceptance, official verifier or canonical candidate was edited.

A separate exploratory source-only ordinary-row **CLASS/DEST bit-pair alignment** tried 11,904 fixed offset/bitplane/orientation/category-map cases against original ordinary metadata. The best models with at least 20 source-fixed training comparisons did not generalize: CLASS 12/23 training and 4/23 later heldout, DEST 15/26 training and 8/26 later heldout. This is a limited heuristic failure, not a theorem that all metadata encodings are impossible. No actual native low-bit leak or new K04 bit was established.

**Research direction:** prioritize a historically evidenced original-source carrier exposing native bits at exactly stages328..331 or724..727, or a separately attested producer transition that predicts the same selected coupon. Standard tempered high-two-bit metadata alone is excluded by the previous exact rank ceiling. Another blind full-state scan without a source-causal transfer would not solve the missing archive fields.
