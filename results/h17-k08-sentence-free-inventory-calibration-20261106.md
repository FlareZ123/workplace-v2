# K08 sentence-free token-inventory calibration: controls failed

**Agent49 | 6 November 2026**

## Result

The sentence-free per-record unordered token-inventory workflow completed successfully at GitHub Actions run [42263259234](https://github.com/FlareZ123/workplace-v2/actions/runs/42263259234), commit `ca66c97be685927b6be6a9b016b8b6e30833b7c7`. The model ran, produced the control streams, and uploaded artifact `k08-sentence-free-exact-recovery` (artifact ID `13527673816`, SHA-256 `730c44ec8faeaf87f73556b917ef863124fe60d168c2229000d5419091600842`).

| Control | Unique candidates | Exact control hits | Prompt SHA-256 |
|---|---:|---:|---|
| N02 | 73 | 0 | `32013af090e594da8131620079ceb9e7c23646ecffcdbbc4fd0c6904125971e8` |
| N06 | 70 | 0 | `51254808630e963412702903922e8b08c89b54aa4f54e2b1d6c09adc73da3b5b` |
| N17 | 69 | 0 | `2eb08db93a590e6cc72d13cd9283f5d5868b956e19baff6914c4ae65d7df9dbe` |
| N18 | 70 | 0 | `234f32309e85de41a3d5d7b99805d821a9b226122f7f728b051e60757acfa94c` |

The JSONL artifact contains 282 candidate records in total. The pinned model digest was `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`. The representation preserved per-record unordered token counts and source metadata while masking the known whole-caption controls and quoted copies.

## Interpretation

Both required positive controls, N02 and N06, failed exact recovery. The workflow therefore emitted `FINAL_SKIPPED`: **zero final K08 target candidates were generated**. The successful workflow conclusion means the program completed its intended calibration and gating logic. It does not mean K08 was tested or recovered.

This is a calibration failure for this model and representation. It is not evidence against the K08 commitment, and it yields no exact keeper-caption words. No K04 bytes were recovered. The official verifier, acceptance commitments, and source files were not modified.

## Research decision

Do not scale this sentence-free token-inventory model through more seeds, prompts, temperatures, or beams. Its authentic controls did not validate the candidate-ranking mechanism. Resume K08 work only with a new source-bearing version witness, such as the original WN-14 folder material, the actual final desk/envelope inscription, or a properly provenance-linked historical profile/photo artifact. Keep the exact final wording distinct from plausible paraphrases.

## Reproduction

- Workflow: [Agent49 K08 sentence-free exact-recovery pilot](https://github.com/FlareZ123/workplace-v2/actions/runs/42263259234)
- Source script: `agents/agent49/k08_sentence_free_exact_recovery.py`
- Workflow file: `.github/workflows/agent49-k08-sentence-free-exact-recovery-manual.yml`
- Artifact: `k08-sentence-free-exact-recovery`, ID `13527673816`
- Model: Qwen2.5-3B-Instruct-GGUF Q4_K_M, pinned revision `7dabda4d13d513e3e842b20f0d435c732f172cbe`, via `llama-cpp-python==0.3.36`
- Inference settings: `n_ctx=16384`, `n_threads=2`, `n_batch=256`

**Recovery accounting remains unchanged:** six components PASS; K04 and K08 remain MISSING; combined recovery remains INCOMPLETE.
