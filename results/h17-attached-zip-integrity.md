# H-17 supplied ZIP versus live workplace-v2 source: exact Git-object integrity check

**Agent 4 | 20 October 2026, UTC.** This checks whether the user-supplied `h17-archive-dump.zip` contains evidence different from the GitHub source snapshot. It makes no claim about authenticity of the underlying incident records or completeness of the original acquisition.

## Independently observed fingerprints

- Attached ZIP: **50,526 bytes**, SHA-256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`.
- Extracted source: **46 regular files**, of which **42** are under `evidence/`.
- Using a separate local temporary Git object store and stage of **only** extracted `evidence/`, its tree SHA-1 is `0196e2bc6b207b8065f50698273db9581ca3f286`.
- Live GitHub REST recursive tree for `FlareZ123/workplace-v2` at 20 October lists `resources/evidence` as **the identical tree object** `0196e2bc6b207b8065f50698273db9581ca3f286`. This Git tree identity binds directory structure, names and exact blob bytes for all 42 evidence files together.
- The four extracted non-evidence original files match the corresponding GitHub blobs:

| ZIP source | Local Git blob SHA-1 | Live repository Git blob SHA-1 |
|---|---|---|
| `START_HERE.md` | `68d4e2d80223df852b513e0154c2dcf0a00eb70c` | same |
| `acceptance.json` | `8e92ad69039cb4e24dcd6cc75dba49dfcc03e8cb` | same |
| `candidate.template.json` | `1210a711bf6b7267246d72cf61796e1723c35dad` | same |
| `verify.py` | `059e075c71acb5f7d68e03a2614daa76d3c54331` | same |

There is **no newly added or changed original evidence material in this uploaded ZIP relative to the current v2 repository**. Unlike textual spot checks, this exact tree-object comparison covers binary PDF bytes, machine records, every extracted email and file paths. The live repository does include separate agent-authored candidate/reducer files, excluded from this original-source comparison.

## Acceptance recheck in isolated local extraction

A local `candidate.json` populated with the six already-published accepted components was run against the ZIP's **unmodified** `verify.py` and `acceptance.json`:

```json
{"slots":{"K01":"PASS","K02":"PASS","K03":"PASS","K04":"MISSING","K05":"PASS","K06":"PASS","K07":"PASS","K08":"MISSING"},"passed":6,"combined":"INCOMPLETE","combined_sha256":null,"accepted":false}
```

The verifier's process exit code is nonzero, consistent with `accepted=false`, not a runtime exception.

## Consequences and caveats

1. The uploaded ZIP cannot independently resolve K04 or K08 through a source-version difference. The two unknowns and their provenance limitations remain as recorded in [the evidence coverage matrix](h17-evidence-coverage.md) and [the prior-art gate](h17-v1-prior-art-gate.md).
2. Source identity does **not** certify that the copied ACK payload is correct or that a keeper caption absent from the export never existed. It proves only equality of the local extracted source and repository snapshot, without relying on hashes claimed by those sources.
3. For progress toward eight/8 acceptance, prioritize a distinct original source of the final ESC-N ACK coupon or the final keeper-margin wording. Do not conflate another identical export copy with independent corroboration.

### Reproduction outline

Hash the supplied ZIP with SHA-256; extract into a clean directory. In a fresh empty temporary Git index/object store, stage only the extracted `evidence/` directory and inspect its tree object SHA. Compare that value with the GitHub API `git/trees/main?recursive=1` entry for `resources/evidence`; compare the other four original blobs separately. Then run the untouched offline verifier against the existing six-slot candidate. No network access is needed for local hashing or acceptance; repository tree comparison requires only read-only GitHub access.


## Reachable Git source-history inventory (additional source-location check)

The linked predecessor repository [workplace-v1](https://github.com/FlareZ123/workplace-v1) has exactly **four accessible default-branch commits touching `resources/`**, inspected with the read-only GitHub commit/history and recursive-tree endpoints. The source-file sets at successive retained snapshots were:

| UTC / predecessor commit | Regular files under `resources/` | Actual source-tree delta |
|---|---:|---|
| 17 October 2026, `5e03668c3652` | 43 | Original 38 evidence files, four reference/checker files, and `AGENT_PROMPT.txt` (task instructions, no REC8 coupon/caption) |
| 18 October 2026, `dc04788bf7dc` | 42 | `AGENT_PROMPT.txt` was removed; none of the original evidence/checker byte blobs changed |
| 20 October 2026, `ca43daaec3cd` | 46 | Exactly four new `evidence/h17-supplemental-office-files/` objects added: PDF, fleet note, reconciliation CSV, bookmarks |
| 20 October 2026, `8beda6625e89` | 46 | Editorial `START_HERE.md` change only; no archive data modifications |

All 38 pre-supplement original evidence blobs and the acceptance/verifier blobs are unchanged across these reachable snapshots. Comparing old and current filenames identifies **no historically deleted, target-bearing original coupon or caption source in the accessible default-branch `resources/` history**. The historical deleted `AGENT_PROMPT.txt` was inspected; it solely contained the earlier assignment and procedural scope. This check is constrained to retained commits reachable via the default-branch `resources/` path history, and cannot establish anything about pruned/unreachable Git objects, unaudited branches, original off-repository custody or unpublished media.

The ZIP/tree check above remains the stronger result for the actual source files supplied to this invocation.
