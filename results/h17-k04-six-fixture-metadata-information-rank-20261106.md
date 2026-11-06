# K04 six-fixture MT metadata observability and single-word donor quotient

**Agent 1 | 6 November 2026 | exact source-fitted GF(2) result; no original K04 coupon or K08 final text recovered.**

## Closest prior art and precise new scope

This is a **six-chronology extension and isolated-donor census**, not the discovery that p951 high-bit printer metadata is insufficient. Agent 2's [4 November exact p951 metadata-oracle ceiling](h17-k04-mt-perfect-metadata-oracle-rank-ceiling-20261104.md) had **already** demonstrated the stronger bound that the highest **twelve** tempered bits of all 435 p951 hidden words leave 128/128 selected bits free. Agent 15's [5 November p951 native-donor localization](h17-k04-p951-native-lowbit-eight-source-donor-20261105.md) had already identified the full eight-word donor locations 328..331 and 724..727, and the [six-stage source parity map](h17-k04-six-model-ordinary-gap-causal-cut.md) previously described a conditional single-bit role for stage p-227. The present contribution is one executable source-fit-rank analysis comparing **all six** frozen chronologies using an identical strong top-octet oracle, and the exact enumeration of the **only individually informative whole-word stage** under each. Do not present the p951 high-octet result as a first discovery or infer a newly authenticated coupon bit.

## Question

Can the nominally hidden two-bit `CLASS`/`DEST` printer-metadata draws, if obtained from another surviving source, make the selected 18:02 RECOVER ACK2 physical coupon reconstructible under the six original-source-compatible native MT19937 printer chronologies p950..955? The original archive does not authenticate MT19937 as the historical printer producer, so these conclusions are explicitly conditional on each frozen stage layout.

Instead of using only the two highest bits of an actual documented metadata draw, grant an unusually powerful *hypothetical oracle*: reveal the highest eight **tempered** bits of **every** unobserved, nonselected native MT word between the first and last observed printer packet. This includes all possible metadata positions and any other hidden draws at those stages. Ask whether even this disclosure removes any independent target K04 coupon bit.

## Method and source

The immutable source is `resources/evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Extract 133 original sixteen-byte packets; exclude row129 (selected RECOVER ACK attempt2) *before fitting*, preserving all 132 intact nonselected packets. Decode four little-endian native MT19937 32-bit outputs per packet, invert standard tempering, and impose their 16,896 observed native bits on an exact 624×32-bit symbolic GF(2) generator. The six frozen historical *hypotheses* for packet starts are from `agents/agent5/k04_crosssource_six_vectors.json` in workplace-v1, mirrored verbatim for reproducibility to `agents/agent1/k04_prior_six_stage_fixtures.json`.

For each vector, measure the independent rank of the original 132-packet observations and the incremental rank of the 128 target native bits, then add top-eight tempered bits for every hidden nonselected stream position. The reported residual is the rank increment of the selected 128-bit packet after granting those hypothetical additional observations. Importantly this is *rank*, not a hash-candidate count or a claim of actual recovered metadata.

A separate quotient-space test takes every one of the hidden native 32-bit word positions individually, appends its *entire* 32-bit observation to the observed source basis, and calculates how many independent target equations intersect with the revealed word. Algebraically, for original observation space \(O\), target space \(T\), and a hypothetical donor-word observation span \(D\), the new independent target information is \(\dim(T+O)+\dim(D+O)-\dim(T+D+O)-\dim(O)\). The implementation computes this through exact quotient ranks, without relying on sample-word coincidence or the target SHA-256.

## Executed results

| Frozen fixture | Original state rank | Hidden nonselected native words | Selected residual after original source | State rank after every hidden top octet | Selected residual after every hidden top octet | Sole individually informative fullword (stage, independent target bits) |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| p950 | 15,366 | 434 | 128 | 17,239 | **128** | (723, 1) |
| p951 | 15,365 | 435 | 128 | 17,271 | **128** | (724, 1) |
| p952 | 15,367 | 436 | 128 | 17,326 | **128** | (725, 1) |
| p953 | 15,368 | 437 | 128 | 17,307 | **128** | (726, 1) |
| p954 | 15,365 | 438 | 128 | 17,312 | **128** | (727, 1) |
| p955 | 15,369 | 439 | 128 | 17,331 | **128** | (728, 1) |

The native-MT recurrence synthetic control passed 56/56; every source-fit preserved original byte values without contradictions. An independent manual GitHub Actions runner completed successfully and reported the complete table: [run 42280807142](https://github.com/FlareZ123/workplace-v2/actions/runs/42280807142). The [read-only single-file SFT](../agents/agent1/k04_printer_metadata_observability_sft.py) and its [six stage fixtures](../agents/agent1/k04_prior_six_stage_fixtures.json) preserve reproduction. The SFT explicitly asserts the p951 15,365 rank, 128 residual, top-octet 128 residual and unique stage724 donor.

## Cracking implications

1. Within each frozen full-source-compatible p950..955 model, learning any amount of mere `getrandbits(2)` first-draw metadata cannot rescue K04 when even the complete hidden **eight-MSB oracle** leaves its 128 target bits free. This differs from earlier individual contradictory `DEST` first-draw checks: it bounds the *information content* of metadata **even under an implausibly generous disclosure**, and covers all six conditional fixture vectors.
2. The complete-word donor census isolates a narrow, falsifiable potential next-source location for a **single** extra target bit: native stage `723 + (p-950)`. No original independent fullword donor for these exact stages was authenticated. The one-bit result is for a donor **in isolation**; combinations of several words may be synergistic, so it does not exclude a compound cross-source relation.
3. The zero-bit effect concerns the top octet of every omitted **nonselected stream position** in the specified fixed chronology. It does not exclude actual full 32-bit PRNG donor observations, a nonlinear metadata/chronology selection rule, alternative physical printer/capture producer, alternate MT stage assignment, or a separate independent copy of the original selected coupon. The surviving copied ACK2 has no independent physical integrity witness.
4. There is no K04 commitment match, newly authenticated original coupon bit, or K08 author-final word. The six previously accepted REC8 components stay unchanged; K04 and K08 remain MISSING and combined verification INCOMPLETE.

**Research direction:** stop treating additional sparse CLASS/DEST two-bit values as a plausible K04 missing-coupon solver *inside these six fixed generator geometries*. Concentrate on an actual full-value selected-original/capture relation, an independently attested output selector, or a materially different producer model; distinguish target-bit information gain from apparent source-state rank growth.

No original spool, route, acceptance, candidate or verifier file was modified.

## Six-fixture two-quartet complete target bridge

A follow-on calculation, executed against the exact same frozen original source model and the selected packet excluded before fitting, tests whether **both** causal four-word donor groups would determine the selected K04 output. For a selected start `p`, the earlier groups are `p-623..p-620` and `p-227..p-224`. Revealing each donor group as **four entire native MT19937 words** is a hypothetical 256-bit observation, not a source claim. Their observed independent target-rank contribution depends sharply on the donor combination.

| Selected start | Early hypothetical donor quartet | Later hypothetical donor quartet | Selected free bits after early alone | Later alone | Both |
| ---: | --- | --- | ---: | ---: | ---: |
| 950 | 327..330 | 723..726 | 128 | 127 | **0** |
| 951 | 328..331 | 724..727 | 128 | 127 | **0** |
| 952 | 329..332 | 725..728 | 128 | 127 | **0** |
| 953 | 330..333 | 726..729 | 128 | 127 | **0** |
| 954 | 331..334 | 727..730 | 128 | 127 | **0** |
| 955 | 332..335 | 728..731 | 128 | 127 | **0** |

This is a conditional, complete **source-to-selected-coupon reconstruction bridge** in all six model geometries, independently run in [manual GitHub Actions CI 42287416887](https://github.com/FlareZ123/workplace-v2/actions/runs/42287416887), source code revision `969a2d0b95a5ab22f5a602992b33a50bbe2df5fb`. The original spool equations and controls PASS, all six both-group residuals are zero. Agent15 had already proved the p951 eight-word donor bridge on 5 November; the six-layout extension is incremental. The critical limitation is that **neither donor quartet has been read from an independently authenticated original source**. Stage relationships alone cannot produce a valid K04 hash preimage. If a matching full-width donor is discovered, the 128-bit result is algebraically reconstructible without guessing the copied ACK; then the official original K04 commitment must be checked.

