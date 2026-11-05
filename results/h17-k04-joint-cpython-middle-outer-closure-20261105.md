# H-17 K04: iterative joint CPython middle/outer initialized-state and MT source closure

**Agent45 | 5 November 2026 | Completed 16/16 original-source CI jobs, no new selected-bit constraint.** This experiment combines two earlier, distinct CPython `init_by_array` source inverses, then repeatedly reinjects their implied initialized-state fixed bits into the exact MT19937 original-source recurrence. It excludes the disputed selected ESC-N ACK2 copied bytes from all constraints and never accesses the K04 mask, K04 target commitment, K08, or original verifier. The actual printer producer is **not** authenticated as CPython.

## New hypothesis and method

Agent45's [outer-word inversion](h17-k04-p951-cpython-inverse-state-seed-length-falsifier.md) left 71 hypothetical 1..623-word CPython integer-seed lengths under a conditional p951 first-output printer chronology. Agent9's [exact 2-adic middle-word inversion](h17-k04-p951-cpython-middle-word-inversion.md) independently contradicted five, leaving 66. Neither earlier analysis iterated **middle-word fixed-bit consensus → outer-word nonlinear inverse → 132 intact printer packet MT recurrence → fresh seed-key residue domains**.

The new [source-pinned executable](../agents/agent45/k04_seed_joint_middle_closure_sft.py) uses the existing two validated inverses, with the following combined iteration for each surviving source length: apply the outer inverse; derive all exact 32bit middle-word solutions via complete high-two-bit enumeration and low-bit lifting; inject only consensus bits common to all middle completions; propagate through the native MT forward/backward recurrence; redo seed-residue constraints against the sharpened source. Repeat to stability, with maximum eight rounds. Each hypothetical seed length is independent and assigned to exactly one of 16 shards by remainder modulo16.

Original printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, rows 0..132. Selected row129 is explicitly withheld by the original reducer. Source-only gate uses exact native bits and the genuine initialized `init_by_array` modular equations. A planted original-acceptance hit is irrelevant to this work because **no commitment is read**.

## Executed original data and calibrated controls

[GitHub Actions run 42045025082](https://github.com/FlareZ123/workplace-v2/actions/runs/42045025082) ran on source commit `4984b021135ae1a2768938f2f3627e456db7e94c`, 5 Nov 14:26 UTC. All **16/16 shards completed SUCCESS**. All sixteen source logs were individually read and their independently disjoint length counts reconciled:

| Source-only count | Complete 16-shard result |
| --- | ---: |
| Lengths 1..623 satisfying original residue sieve | **144** |
| Surviving independent outer-word/MT source check | **71** |
| Surviving initial exact middle-word inversion | **66** |
| Newly contradicted through joint iterative propagation | **0** |
| Surviving fully combined source model | **66** |
| Selected K04 native coupon bits fixed in any surviving model | **0/128** |

Each shard's printed `ADDITIONAL_EXCLUSIONS` was empty; all `max_fixed=0`, `total_fixed=0`. On shard0, **six genuine CPython integer-seed controls** at lengths374/394/623 (two variants each) passed the entire **combined** inference and preserved their actual generator-selected native words. The 16 job success states enforce source SHA pin, implemented assertions and absence of synthetic false contradictions. This supports correct execution of this finite combination, not historical identification of the 2026 printer.

## Meaning and next decision

The logically stronger nonlinear constraint combination does **not** improve the seed-length survivor set or determine a bit of the missing coupon. This closes the specific hypothesis that middle-word feedback by itself breaks p951 source nonidentifiability. It does not prove CPython is the real writer, exclude longer seeds or alternate stream epochs, or establish the integrity of the copied source ACK2.

To pursue K04, require a **different causal source relationship** that observes output bits at selected unknown native stages or a complete original physical coupon object. Repeated repropagation with the same initialized-state equations has no demonstrable further value. K08 author-final text was not touched. Original six accepted slots remain PASS, K04/K08 MISSING, combined REC8 INCOMPLETE.
