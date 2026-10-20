# Agent 9 — H-17 source-led REC8 recovery

## Claim
- Claimed normal-mode identity 2026-10-20T07:44:47Z under `agents/agent9/.lease.json`.
- This incarnation's randomized mode draw was 2 (normal); Critic mode not applicable.
- User supplied `h17-archive-dump.zip` and `prompt.md`; no Work mode used.

## Independently reproduced baseline
- Extracted the provided ZIP without altering original files; wrote a **local** six-slot candidate copy, not the repo source files.
- Executed ZIP's unchanged `python verify.py --candidate candidate.json --json` from extracted root.
- Exact result: K01, K02, K03, K05, K06, K07 `PASS`; K04/K08 `MISSING`; `passed=6`, `combined=INCOMPLETE`, `accepted=false` (exit 1 for incomplete).
- Current remote `candidate.json` already carries those six correct components and null K04/K08. No duplicate submission required.
- `README.md` forbids per-commit workflows.

## Specific live provenance/read checks
- Read `resources/START_HERE.md`, `results/README.md`, `results/h17-recovery-status.md`, `results/h17-v1-prior-art-gate.md`, evidence coverage and custodian request.
- Reviewed original recovery routing, records-custodian warnings, full 24-note crew-board transcription, relevant mails 08/10/11/16/18/20, print-job 0417 lines, supplemental office note/bookmarks and untouched acceptance checker.
- K04 exactly: route ESC-N to `PS-261003-0417`; 2026-10-03T18:02Z RECOVER attempt-2 ACK payload `A9A9DC5731A5E2AE879C47215C2559D5`, XOR original `8556C8CB6140A7F9A5123AC7571BEE1C` => `2CFF149C50E54557228E7DE60B3EB7C9` (original commitment NO_MATCH). Later attempt 3 is merely REQUESTED. Dispatch ACK does not certify payload byte integrity.
- K08 exactly: HMAC key `5F933DA6A1BD03C32DA5CBC25344F497` and normalization are supplied, but final personal marginal caption absent; N02/N06 drafts, N17/N18 older envelope labels, N13/N20 thematic notes only.
- Explicit source constraints: missing original `file:///R:/Records/INDEX/IR-261003-H17.txt`, possible historical offline printer-host job file and user-profile R: mapping. These are retrieval hypotheses, **not supplied original evidence**.
- No new source found in GitHub issue #1 comments (only agent8/10 requests and synthetic-validation instructions). A web search of exact K04/K08 digest and corporate-domain phrases had no relevant results. Public company site not accessible through normal web reader; predecessor verified public pages and reported no target-bearing material. No protected site was accessed.
- Confirmed predecessor `workplace-v1` claims 180+ source/puzzle reports against byte-identical core files. Broad low-order substitutions, bit flips, contiguous four-byte replacements, wordlane XOR, orientation fixes and K08 literal spans were already tested. Avoid duplicate CI and uncalibrated guesses.

## Frontier and next work
- **Source-independent target recovery has not been achieved**: new authenticated K04 selected coupon bits 0/128; authenticated K08 final words 0; combined REC8 unavailable. No invented bytes should replace null slots.
- Check for genuinely newly added authorized source material (original printer coupon/print-host offline spool, final keeper margin/photograph, original archived R: index, printer-state witnesses). Hash original bytes before interpretation, require independent provenance, then use read-only `work/h17_witness_intake.py`.
- Another model worth testing only if source-grounded is a producer-state donor whose originally *withheld intact* output is correctly predicted; refer to v1 MT nullspace and 1412/1866 donor gates. Avoid further hypothetical model/rank reports without target-bearing observation.
- Proposed documentation status: no novel seven/eight-slot recovery; do not elevate this replay to a result. Existing `results/README.md` and custodian issue #1 remain truthful.

## Repo links
- `results/README.md`: canonical state; `results/h17-v1-prior-art-gate.md`: cross-repo negative tests
- `results/h17-original-witness-intake-gate.md`: original coupon and caption intake
- `results/h17-evidence-coverage.md`: source audit
- `results/h17-missing-evidence-request.md`: original needed records
