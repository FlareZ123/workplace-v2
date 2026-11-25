# H-17 archive recovery | working entry point

**Current state, 23 November 2026:** The original REC8/1 verifier accepts K01, K02, K03, K05, K06 and K07. **K04 and K08 remain unresolved. Combined acceptance is INCOMPLETE.** The success criterion is K04 PASS, K08 PASS and combined REC8/1 PASS using the untouched original verifier.

The authoritative short decision map is [results/README.md](results/README.md). It links the current experimental boundaries, source limitations, reusable code and substantive results. Start there rather than relying on older directions preserved below.

## Work that advances recovery

- **K04:** Construct the complete 16-byte component from surviving records through an explicit producer, selection, copy-stage or cross-record relation. The retained PS-261003-0417 RECOVER attempt-2 ACK and route mask alone yield a rejected candidate; the physical coupon is not authenticated by that ACK.
- **K08:** Construct the complete final wording attributed to Emily, normalize it exactly as specified by the source, derive its HMAC-based 16-byte component and test it against the original commitment. The final envelope inscription is unquoted in the supplied export; drafts and scene descriptions do not fix the wording.
- **Broader interpretation:** Reconsider whether an inherited producer, selector, stage, authoring rule or independence assumption is wrong. The maintainer confirms solvability and explicitly permits research under uncertainty in [MAINTAINER_OVERRIDE.md](MAINTAINER_OVERRIDE.md). Neither missing original is a prerequisite for exploratory reconstruction.

For a new mechanism, identify the exact retained inputs, the deterministic construction, its complete output and how it differs materially from tested alternatives. Use a withheld historical complete-object control when one exists. Its absence does not bar a bounded exploratory test; report the limitation. An original commitment hit is a candidate, while historical authenticity must be considered separately.

**Do not confuse search volume with recovered information.** The recent K04 donor, printer-state, modem analogy, copy-error and transfer variants and the many K08 word-grammar, source-bigram, anagram and caption-composition grids have produced bounded negatives, not accepted missing components. Consult [the current decision map](results/README.md) and [the prior-art/equivalence index](results/h17-experiment-equivalence-gate.md) before extending their exact domains. A combination of unsupported cues is still an unsupported causal model; find a new source-dependent relation rather than another adjacent parameter sweep.

## Source integrity and practical boundaries

The source bundle is a **working preservation export**, not a certificate that all originals survived. The selected physical coupon, native printer object and author-final caption are absent from this export. These remain conditional passive-intake opportunities if genuinely authorized originals arrive through an independent route. The human-custodian inquiry is closed. Do not contact that custodian again, probe protected services, or operate or alter equipment. Do not modify the original evidence, [commitments](resources/acceptance.json), [verifier](resources/verify.py) or [canonical candidate](candidate.json) to manufacture acceptance.

**BX25-08 preservation restriction:** The supplied PDF is hash-only under the later 20/24 November source-specific notices. Do not open, decrypt, OCR, render, extract, scan or rely on any derivative. Preserve only the original encrypted bytes and pinned SHA-256. The earlier 10 November authority correction does not override this later restriction; see the [current decision map](results/README.md).

Reuse existing tests and parameterized runners. Avoid creating a workflow for a single speculative test or a series of commits about the same negative result. Keep one reproducible report for a substantive experiment, update the live map only when the next research decision changes, and communicate across agents when doing so prevents duplication or unblocks a specific mechanism.

## Reference material

- [Live recovery decision map](results/README.md)
- [Evidence-derived component definitions and acceptance boundary](results/h17-recovery-status.md)
- [Current negative-family and equivalence map](results/h17-experiment-equivalence-gate.md)
- [Official source/evidence directory](resources/)
- [Reusable recovery and intake tools](work/)
- [Maintainer's solvability and research mandate](MAINTAINER_OVERRIDE.md)
- [Complete historical README through 16 November](README.archived-through-20261116.md)

The archived README retains dated research pivots, acquisition specifications, earlier Critic directions and historical background. It is retained for context; current instructions and current research decisions are in the maintainer directive and live decision map.
