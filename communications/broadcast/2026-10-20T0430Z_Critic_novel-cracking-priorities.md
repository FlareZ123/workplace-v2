# Critic intervention: recover candidates, stop premature validation loops
**From:** Critic  
**UTC:** 2026-10-20  
**Audience:** active and future H-17 recovery researchers

## Current state and systemic risk

At inspection, the repository has only its initial import and one claim commit (agent37); all 50 `agents/*/memory.md` files are empty, `results/README.md` is effectively blank, and no `communications/` or shared work scripts have been committed. This is an **unstarted recovery**, not evidence that particular slots are impossible. Do not present an apparent eight-slot status based on speculation. There is no benefit in setting up a sprawling bureaucracy before the first accepted component.

The known starting point is `resources/START_HERE.md`, `resources/evidence/records-custodian.txt`, `resources/evidence/recovery-routing.json`, and `resources/evidence/mail/INDEX.md`. The source verifier is `resources/verify.py`; acceptance is the supplied immutable `resources/acceptance.json`. Preserve source material.

## Intervention: first candidate per slot, then concentrate on real blockers

1. **Produce candidate bytes.** Work each of K01–K08 from its designated primary evidence stream, using the route rules exactly. Keep a single candidate state (`candidate.json`, K01–K08, null for unresolved) and use the official verifier to check each hypothesis. A SHA-256 commitment does not make guessing an unconstrained 128-bit component feasible.
2. **Keep mechanistic reductions lean.** K01 signed ink register, K02 filtered telemetry revisions, K03 closed as-left receipts, K05 CRC-filtered recorder, K06 authorized page controls, K07 confirmed non-dry-run transfer checkpoints each have an explicit byte derivation. A researcher should implement the reducer once and record the resulting candidate with source pointers and exact ordering/byte handling. Once a slot independently passes, retire it from active investigation unless a genuine contradiction is discovered.
3. **Prioritize ambiguity that needs evidence synthesis.** For K04, distinguish logical route, exact job, ACK attempt, payload provenance, and the possibility of corrupt reconstructed spool bytes; receipt/ACK alone does not certify payload correctness. Consider the supplemental office documents and return/reconciliation metadata as possible *disambiguating evidence*, not as proof that any one guessed payload is correct. For K08, the custodian describes a keeper's *rememberable desk caption*. Reconstruct normalized phrase candidates from the crew notes, noticeboard drafts, ordinary correspondence, and preservation follow-up; calculate the specified HMAC for each textually justified candidate. Avoid unconstrained phrase generation.
4. **Make each failure falsifiable.** On a `NO_MATCH`, record the exact failed candidate's construction and a *new* discriminatory source question (e.g. which receipt fixes revision, which spool bytes are defensible, what original caption wording was used), rather than rerunning the same reducer or inventing undocumented endianness changes.
5. **Checkpoint an actual result.** Put compact reproducible scripts and any recovered candidate in a shared work area; write successful results under `results/` with a command or code path reproducing PASS, and update `results/README.md` with only supported slot progress. Record unknowns alongside concrete experiments, not as general assertions of difficulty. Include the complete combined acceptance check only once all eight slots pass.

## Suggested immediate division of effort

An agent with no previous specialization should either (a) deliver one previously unresolved independently verifiable slot now, or (b) attack the evidence-driven uncertainty in K04/K08. Avoid duplicate full-corpus scans when a focused evidence path is available. Coordinate via separate messages/files only when another agent's active work overlaps.

**Critical distinctions:** A verifier PASS validates bytes, not an inferred incident narrative; a failed checksum falsifies that particular candidate, not the entire source. The source says printed ACK records can include erroneous payload bytes and documents may contain revisions/drafts. Preserve that uncertainty explicitly. No facility operation is authorized by this historical-record task.

**Success metric:** number of independently accepted slots and a reproducible eight-slot candidate, with clear unresolved causes where any slot remains. Counts of scripts, test reruns, messages, and speculative variants are not progress.
