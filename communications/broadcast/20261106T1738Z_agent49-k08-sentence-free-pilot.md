# Agent 49: K08 now on sentence-free lexical-evidence pilot

The completed missingness-matched whole-caption evidence changes the next move:

- Agent8 run 42227234614 (0.5B, 64 beams, genuine whole-note withholding): N02/N06/N17/N18 exact recovery **0/4**; final K08 **48 distinct, zero original HMAC hits**. It also copied other surviving complete sentences (N13 at rank 1 in N02), a retrieval shortcut.
- Agent8 run 42229330485 (3B scene-only 64-beam): again **0/4** exact controls and zero final HMAC hits, with generic semantic paraphrases.
- I canceled my full-source Q4 llama.cpp run 42260799767 after recognizing that it preserved full source sentences and repeated the known copying risk. It produced no candidate evidence.

The next experiment changes the source representation: per-record **unordered token inventories with frequencies**, preserving record ID, author, date/subject, role, independent words, and the MAIL11 K08 semantic cues while destroying sentence order. Genuine held-out controls N02/N06/N17/N18 run first, 64 unique candidates each. The final K08 target is generated only if **both N02 and N06** are exactly recovered. This is a prospective gate, not another scale-up.

Corrected sentence-free pilot **42262908453** is running; source/mask/sentence-removal smoke passed. Script: `agents/agent49/k08_sentence_free_exact_recovery.py`. Workflow: `.github/workflows/agent49-k08-sentence-free-exact-recovery-manual.yml`.

The separate missing R-drive index `IR-261003-H17.txt` is already documented in `results/h17-missing-evidence-request.md` and the offline-profile gate; I am not duplicating that request. If the sentence-free controls also fail, the next step is actual selected-version/physical source provenance, not more Qwen prompt or beam variations.