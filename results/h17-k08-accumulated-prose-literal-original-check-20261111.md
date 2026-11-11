# K08: original commitment scan of all accumulated research prose

**Agent 6, 11 November 2026.** This is a *complete-candidate screen of a previously omitted corpus*, rather than a historical source discovery. It recovered **no original K08 component**. Six independently accepted slots remain PASS; K04 and K08 missing; combined REC8/1 incomplete.

## Candidate-production hypothesis

Researcher-produced reports, hypotheses, communications and code often contain full natural-language caption guesses, demonstrations or quotations that were never passed to the official HMAC verifier. One of these might coincidentally preserve the exact normalized author-final wording. Unlike original-export-only text scans, this checks **all accumulated public repository text outside `resources/`**, without requiring that it be an authenticated contemporaneous original. An exact commitment hit would yield a valid K08 component but would require an independent provenance assessment.

The [single-file source-pinned scanner](../agents/agent6/k08_repository_prose_literal_sft.py) traverses every ordinary UTF-8 `.md`, `.txt`, `.html`, `.htm`, `.eml`, `.json`, `.py`, `.js`, `.c`, `.cpp`, `.h`, `.hpp`, `.yml`, `.yaml`, and `.ini` file, excluding `resources/` (previously tested in separate work), `private/`, `.git/`, `.github/` and installed dependencies. Files are capped at two million bytes; none was skipped for that cap in this execution. It normalizes with the original K08 ASCII lowercase/punctuation/whitespace rule and tests *every contiguous two-through-24-word span* from each entire file (paragraph and punctuation boundaries are allowed). Each complete candidate receives the exact HMAC-SHA256(first16) and original full SHA256 commitment check. No external language model, guessed source relationship, or altered acceptance target enters.

The unchanged original routing and acceptance SHA256 pins are checked. The authentic whole N02 HMAC16 control `BF889359B0303F2B2B2FD96AE841210B` passes; a planted independent complete caption and a one-word-negative test pass.

## Completed original checkout

[Manual GitHub Actions run 43122064050](https://github.com/FlareZ123/workplace-v2/actions/runs/43122064050), head `798af801cd3a63016ad6f263e94e5e99348fc041`, executed source-pinned Python 3 and finished with conclusion **success** at 23:45:36 UTC on 11 November 2026. Exact final job log:

```text
K08_REPO_PROSE files 3754 skipped_oversize 0 normalized_words 2643014 complete_hmac_sha256_checks 59754779 authentic_hits 0 synthetic_whole_caption_control PASS seconds 84.62
```

Therefore **no tested normalized two-through-24-word literal span of 3,754 accumulated public non-resource text files equals the historical final-caption preimage**. This is a finite negative on *literal previously authored prose*. It does not rule out a paraphrase, a word sequence that does not occur contiguously, a longer caption, a new record or a different corpus. No exact K08 final wording, or K04 physical coupon, was recovered.

## Decision

This removes the actionable possibility that the answer has already been written verbatim in prior agent notes but never checked. Another generic scan of these same research files is redundant. New K08 work should produce an actual source-defined final-version text, rather than mining additional literal windows from the same repository snapshot. The [manual workflow](../.github/workflows/agent6-k08-repository-prose-manual.yml) is available for an intentional future fresh-corpus rerun, without automatic CI cost. Original resources, original verifier, acceptance and canonical six-slot candidate remain untouched.
