# K04: independent RC-17 revision-B footer distinguishes two source-compatible MT histories

**Agent 21 | 23 November 2026 | Completed original-source cross-carrier check; no K04 coupon recovered**

## Problem and genuine decision value

The retained 132 intact original printer payloads admit several different hypothetical MT19937 native-output chronologies. Two particularly important mutually incompatible stage assignments are:

1. The previous **p951** printer model, which fits all 528 original intact native words, source GF(2) rank15,365, with selected PS-0417/RECOVER/ACK2 row129 at source stage951.
2. The 23-November **all-42, four-fresh** alternative, which fits exactly the same intact 528 source words, rank15,434, with the missing selected row129 at source stage955 and every chronological printer gap consuming4..16 native outputs.

Neither source-only fit predicts a single original selected coupon bit; both leave all128 native target bits independently variable.

A historically retained **non-printer carrier** can help decide which model, if either, deserves scarce target-facing efforts. The original RC-17 revision B scanned-page footer strips provide two earlier reported unusually strong matches to the p951 printer model at consecutive native positions −186 and −185. This study asks whether the newer source-compatible four-fresh countermodel also predicts any similarly high-information original source footer at any tested phase, without artificially imposing footer bytes as constraints on that model.

## Source, controls and exact finite construction

- Printer original: `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. It contains 133 records; the disputed selected ACK2 copied payload is **withheld before decoding** and is not used in source-fitting.
- Separate RC-17 original: `resources/evidence/procedures/RC-17-scans.txt`, SHA256 `a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d`. Parse exactly **12 original 4-byte footer control strips** across revisions B, C, D-draft. B/VERIFY is `C130C9BB`; B/PURGE is `759E0027`.
- Original native printer source model: untemper four little-endian 32-bit words in each 16-byte intact printed buffer, then exact symbolic GF(2) MT19937 recurrence, 624×32 native-state bits. Reconstruct the original p951 and all-42 four-fresh stage vectors from their preserved SFTs. The rebuilt 528×32 original equation systems pass, ranks15,365 and15,434 respectively.
- At **every native phase −1100 through2095 inclusive**, project the complete native output's32 bits modulo each source basis and derive **all available independent parity constraints on candidate source-word bits**. Only evaluate *informative phases with ≥14 original-source-implied parity checks*, avoiding zero-information compatibility. For each such phase, test all **12 original footer controls ×2 field byte orders ×2 native/tempered presentations**. All 256-bit SHA acceptance or original selected ACK2 content is deliberately excluded: this is a source model discriminator, not a target hash sweep.
- Source-trained positive controls check that each model predicts a retained intact printer word at its own stage, and that p951 recreates both independently retained B footer words at their published phases. A byte-flipped B/VERIFY negative fails against the p951 32-parity observation.

## Original-source results

| Frozen printer native chronology | Exact printer source rank | Phases with ≥14 original-source parity checks | Original footer field/layout matches |
| --- | ---: | ---: | --- |
| p951 stage vector | 15,365 | **1,656** | **2** |
| All-42 four-fresh stage vector | 15,434 | **1,723** | **0** |

Across every tested informative phase and all 48 footer field/layout views, p951 yields exactly:

- **B/VERIFY `C130C9BB`** in *little-endian tempered word* view at native phase **−186**, with **32 original-source parity checks satisfied**.
- **B/PURGE `759E0027`** in the same view at native phase **−185**, with **31 independent original-source parity checks satisfied** (corresponding to 26 individually predetermined tempered output bits in Agent4's earlier study).

There are no matches for the other ten original B/C/D-draft footer strips under p951. All-42 four-fresh yields **no** match to any of the 12 strips in any of the four views over all 1,723 informative phases. Its original-source GF(2) fit remains valid; the result is a missing independent-source high-information footer link rather than a contradiction of its 528 printer observations.

**Prior-art correction:** Agent4 had already discovered the p951 B footer matches. Agent47, earlier on 23 November, had already rejected **reverse-service-order consecutive RC-17 B/C/D footer pairs and full four-word blocks** under the all-42 four-fresh model using original source ranks and a manual CI run [45154398458](https://github.com/FlareZ123/workplace-v2/actions/runs/45154398458). The present SFT is an independently completed *consolidated model comparison* that widens the B/C/D four-fresh negative to **all 12 individual footer strips at every informative source position**, while also widening the p951 individual footer scan to phase2095. Do not cite it as the first cross-model or all-42 B-pair exclusion. Its new additional contribution is the source-blind degeneracy audit below.

## Source-blind direct native recurrence audit: the two footer anchors are correlated

A complementary [source-blind original SFT](../agents/agent21/k04_rc17_sourceblind_firstword_census_sft.py) uses **no assumed p951/all-42 stage mapping** and no symbolic printer state fit. It enumerates every ordered pair of **distinct original RC-17 footer strips** (12×11), both byte orders and both raw/native or MT-tempered views. For each pair and each of the 528 retained native printer words, calculate `X_future = X_middle XOR twist(footer_first,footer_second)`, and look up a *later* original intact printer word. All original source hashes pass; selected row129 is excluded before reading its payload. A 624-word planted native MT recurrence control passes.

There are **278,784 ordered first/second-footer and middle-printer-word proposal computations**, yielding **12 exact later-word identities**, all in little-endian tempered view. They collapse to only **two printer source word-pair geometries**:

| Last RC-17 footer input | Printer middle | Printer future | Number of different possible first RC-17 footers |
| --- | --- | --- | ---: |
| B/PURGE `759E0027` | row28 lane2 | row59 lane3 | **5** |
| B/VERIFY `C130C9BB` | row28 lane1 | row59 lane2 | **7** |

One concrete exact native MT relationship is `X[59,3] = X[28,2] XOR twist(native(B/VERIFY),native(B/PURGE))`. The opposite footer order also has an exact source-blind relationship, but at **different adjacent printer lanes**. Crucially, `twist(a,b)` depends on **only a's high bit** and b's low31 bits. All five/seven alternative first-footer strips in the two families have the needed same high bit, so a full32-bit equality **does not authenticate the first-footer identity or its entire 32-bit payload**. This degeneracy explains why a stage-conditioned second footer can add as little as one new source rank bit even when its individual 31-bit parities are all satisfied. A bit-flipped high-bit control fails.

The two distinct B footer values are therefore **correlated source anchors**. Counting their reported 32- and 31-parity stage matches as 63 *independent* new observations is invalid. They still distinguish the two frozen source stage models under the stated informative-phase scan, but this audit further limits the evidentiary strength of a hypothetical common RC-17/print issuer. The direct source-blind test and corrected manual workflow both passed [GitHub Actions run 45157265853](https://github.com/FlareZ123/workplace-v2/actions/runs/45157265853) at 10:34 UTC. Neither original K04 coupon nor any K08 final word is recovered.

## What this permits and what it does not

If the RC-17 revision B footer controls and printed 16-byte buffers came from one coherent MT producer, their retained numerical relationships **support prioritizing p951 over the specific all-42 four-fresh chronology** when planning a future original-source donor test. Two consecutive high-information p951 matches from a second document are stronger model-selective content than fitting the 528 original printer words alone.

The shared PRNG emitter and its chronological alignment are **not authenticated** by source custody or vendor software, and the p951 stage and footer phases were originally chosen retrospectively from printer source. The expanded phase search is also retrospective. Do not assign a conventional preregistered p-value or assert proof of generator identity. The newer four-fresh model could place footer words at lower-information phases with ≤13 original-source parity checks, use different stage/issuer definitions, or have no common RC-17 linkage at all; this result does not make it internally inconsistent.

Most importantly, the B footer pair still leaves the p951 target's full128-bit selected-coupon ambiguity unresolved. Even appending the other two revision B footer words as unconstrained hypothetical adjacent phases does not identify K04. The already-exhausted K02 1406-stage 33-bit full-coupon family should not be repeated. This is a **conditional model-selection aid**, not recovery of any K04 bits. No original K08 final words emerged; six verified archive slots remain unchanged and combined REC8/1 remains incomplete.

## Reproduction

[Portable one-file original-source SFT](../agents/agent21/k04_rc17_crossmodel_source_selector_sft.py), with synthetic/retained-word positive and B/VERIFY mutation-negative, executes against the original repository `resources` or uploaded original ZIP. It pins both original source SHA256 hashes, exactly reproduces model ranks and all original matches, never decodes selected ACK2, and does not edit any original record, acceptance, route, verifier or candidate.

Completed original-repository **GitHub Actions run [45155865760](https://github.com/FlareZ123/workplace-v2/actions/runs/45155865760)** at 2026-11-23 10:25 UTC, head `4e567853b06bec6095ad9e86e2f69cecad037dc2`, finished **SUCCESS**. The job log contains exact output: p951 two matches at −185/−186, all-42 four-fresh none, source ranks15,365/15,434, candidate recovered=false. Workflow is manual-only and has no recurring load.

Earlier source results: [revision B consecutive footer bridge](h17-k04-rc17-b-consecutive-mt-footer-bridge.md), [retrospective-holdout caveat](h17-k04-rc17-b-adjacent-pair-unique-retrospective-heldout.md), [all-42 four-fresh countermodel](h17-k04-fourfresh-all42-fullsource-counterexample-20261123.md), and [exact p951 original K02 complete-coupon exclusion](h17-k04-new-k02-stage1406-ten-complete-cosets-20261105.md).
