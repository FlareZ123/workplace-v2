# K04 p951 LT-204 revision-cohort donor SFT

**Date:** 2026-11-13  
**Agent:** 3  
**Status:** Bounded source-derived extension; zero K04 commitment hits.

## Question

Do the alternate LT-204 DIAG_WORD revision cohorts provide complete 16-byte donor blocks that, paired with another retained source block, determine the four missing p951 MT19937 outputs at target stages 951–954?

## Construction

The existing p951 unique-gap pair model uses four-word gaps beginning at indices 328 and 724, with the disputed target at stages 951–954. Agent 43's original SFT had 11 distinct source blocks and tested 1,760 complete pair models.

The HST-4 export contains eight LT-204 DIAG_WORD sequence values (seq 0–7) in each of revisions 1–4 during the K02 freeze window. Revision 2 is already the selected K02 block. This SFT adds three complete historical revision cohorts as hypothetical donor blocks:

- Revision 1: GOOD / HOLD
- Revision 3: SUSPECT / HOLD
- Revision 4: GOOD / RUN

Each block is the eight raw_u16 values in seq order, encoded big-endian as 16 bytes. The exclusive-end revision-99 sample is excluded. The three cohorts are donor hypotheses only; they are not substituted for the K02 accepted reducer.

The original 11 source blocks plus these three cohorts produce 14 distinct blocks. The SFT tests every distinct block pair, both gap assignments, both byte orders and native/tempered interpretations.

## Result

| Measure | Result |
|---|---:|
| Distinct source blocks | 14 |
| Complete candidate models | 2,912 |
| Inconsistent models | 0 |
| Underdetermined models | 0 |
| K04 commitment hits | **0** |
| New K04 bits recovered | **0** |

Reproduction:
- Script: agents/agent3/k04_p951_lt204_revision_donor_sft.py
- Workflow: .github/workflows/agent3-k04-p951-lt204-revision-donors.yml
- Successful run: 43410255842
- Machine-readable output artifact: k04-p951-lt204-revision-donor-sft

The telemetry input hash is pinned in the script: 3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f.

## Interpretation and boundary

None of these three complete revision cohorts, paired with the retained source blocks under the p951 model, produces the committed K04 component. This closes this finite revision-cohort donor family; it does not authenticate the p951 chronology or prove that the HST and print systems shared a generator.

Do not expand this into arbitrary per-sequence revision combinations or another generic halfword scan. The arithmetic HST seq+200 / spool-job suffix relation remains a locator hypothesis, not an authenticated temporal join. The useful next evidence is the original PS-0417 attempt-2 native spool/coupon with independent media-integrity evidence, or an authenticated complete HST/native print-host export.

No candidate, acceptance commitment, route or verifier file was changed.
