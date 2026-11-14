# 14 November 2026: completed frozen K04 MT64 and K08 Cowper tests

**Original result:** zero accepted new components. Original K04 and K08 remain missing; the six previously accepted slots and REC8/1 checker are unchanged. These are finite conditional mechanism tests, not claims about the historical printer or Emily's actual source.

## K04: source-frozen 312-word MT19937-64/HST constructor

Completed the already-committed `agents/agent13/k04_mt64_hst312_complete_sft.py` locally, with `ROOT` mapped to the byte-identical supplied ZIP extract at `/mnt/data/h17-now`. The stand-alone executable otherwise preserved its search model, exact original target, source checks and synthetic continuation. Original sources:

- `spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- `freeze-export.jsonl` SHA256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`

Observed stdout, reproduced exactly:

```text
synthetic native MT64 continuation PASS 312/312
models 504 complete K04 checks 1008 hits 0 best heldout whole-packet controls 0
```

The 504 predefined histories/layouts/serializers and both future-packet policies yielded zero original K04 commitment matches and zero exact withheld complete-packet controls. This closes that **exact** constructor, not every MT64 producer or independent source relation. No original target bits were recovered.

## K08: frozen signed WN-14 → Cowper Part II page/word coordinates

Executed the previously unrun `.github/workflows/agent4-k08-cowper-wn14-pageword.yml`. First run [43541614274](https://github.com/FlareZ123/workplace-v2/actions/runs/43541614274) found an input-guard bug: original MAIL-14 wraps `A, then B, then C,` and `then D remains the order` across a newline. Source guard was fixed without changing any candidate-generation coordinate.

Second run [43541782195](https://github.com/FlareZ123/workplace-v2/actions/runs/43541782195) fetched an unsigned page-121 image (63,361 bytes, 1025×1337), differing from the prior source-pinned signed-image calibration (97,450 bytes, 1025×1516). It appropriately returned `ACCESS_OR_CALIBRATION_MISMATCH`, not a K08 no-match.

Signed-image acquisition was repaired using the same public Google Books Playwright viewer procedure as the established Agent49 source capture, without changing the frozen page/word pairs, book, edition, OCR convention, source groups, K08 nonce or acceptance. The single requested page set is calibration 121 plus pages 4,171,28,122,205,96,67,201. Third run [43542117255](https://github.com/FlareZ123/workplace-v2/actions/runs/43542117255) completed and committed original page bytes and OCR evidence under `results/assets/cowper/part2-wn14/`. Calibration **passed exact original page-image SHA256** `3b1e1b88244b2c0e15eeabf1f3f0d72d4cc6f0127256c55e0bc8e3978c3d0083`.

The frozen byte-pair page/word mapping selected exactly:

```text
a should At away a Why the We
```

K08-normalized phrase `a should at away a why the we` gave HMAC16 `97225D964C198211328E9035E912C272` and component SHA256 `2365078084faa3e335a3f025585c803e531e532e2dc8fa635c17d146852623b8`, **NO_MATCH** against original K08 component SHA256 `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. Inspect [result JSON](assets/cowper/part2-wn14/result.json) and the page-image packet to reproduce.

This closes only the frozen conditional WN-14 pair-coordinate constructor in the stated Cowper Part II edition. WN-14 is attested as an ink control source, and Cowper is a hypothetical map-back book identity; the supplied source does not attest the byte-pair page/word reading. Do not extend to nearby editions, page orders, offsets or OCR grammars absent a new causal clue.

## Research decision

Neither completed test provides an accepted K04 coupon nor an exact K08 caption. Retain the six accepted slots, original verifier, original commitments and source files untouched. Redirect to a different complete-object construction or independent target-bearing relation; further repairs or nearby parameter sweeps on these two branches are not justified.
