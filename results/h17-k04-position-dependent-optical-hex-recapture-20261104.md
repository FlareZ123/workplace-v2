# K04 original ACK copy: position-dependent visual-hex recapture family

**Agent 10 | 4 November 2026 | complete original-target search, read-only original.** Two nested, precisely defined optical-transcription models produced **zero accepted original K04 values** over **524,288** and **33,554,432** complete candidates respectively. Each scope recovered one planted six-nibble full-coupon positive. **K04 remains missing**, as does K08; the six established slots and original combined-INCOMPLETE state are unchanged.

## Why this differs from prior copy-stage tests

The reconstructed source-selected 18:02 UTC `PS-261003-0417` ACK2 copied payload is `A9A9DC5731A5E2AE879C47215C2559D5`. MAIL16 explicitly says its surviving buffer lacks an independent payload checksum; the original K04 mask and SHA256 target distinguish possible physical originals. Previous work exhaustively rejects arbitrary four-hex-nibble replacements (v1 Agent40), global *uniform* invertible affine maps on all hexadecimal symbols (v2 Agent1), arbitrary four whole-byte pairs and lane geometries (v2 Agent19 and related). This experiment uses **an independently position-selectable, nonaffine glyph-confusion channel on potentially more than four hexadecimal digits**, with no predefined maximum number of altered positions. Its candidate set can alter every ambiguous position independently while keeping uncommon glyphs intact.

This is an **exploratory copying hypothesis**, not an assertion that the historical buffer was actually OCR-transcribed. Neither the recovered source nor the mail documents a particular optical font or authenticates the original paper coupon. The SFT looks only at the selected copied text and fixed original acceptance; no hidden original may be inferred from a negative result.

## Frozen complete-candidate mechanism

For each of the 32 characters of the **copied** original payload, choose either the original glyph or any of the following substitutions. All choices at distinct positions are independent. There is no replacement of a character outside these defined sets.

| Copied glyph | Strict alternatives | Medium alternatives |
|---|---|---|
| `A` | `4` | `4` |
| `4` | `A` | `A` |
| `8` | `B` | `B` |
| `3` | `8` | `8` |
| `D` | `0` | `0` |
| `C` | `0` | `0` |
| `E` | `F` | `F` |
| `1` | `7` | `7` |
| `7` | `1` | `1` |
| `5` | none | `6` |
| `2` and `9` | none | none |

All other positions stay unchanged. Read the candidate 32-hex-character payload as sixteen raw bytes; XOR each byte with the **unchanged** recorded route mask `8556C8CB6140A7F9A5123AC7571BEE1C`. The resulting 16-byte K04 candidate is SHA256-hashed and compared against the **full 256-bit unchanged** K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The strict product has exactly **2^19 = 524,288** complete assignments. The medium model adds one independently switchable `5 → 6` alternative for the six copied `5` positions, giving **2^25 = 33,554,432** complete assignments. The strict family is contained within medium; report their sizes separately, **not** an artificially added total of distinct candidates.

## Original execution and controls

The local C++/OpenSSL source-pinned SFT was compiled with OpenMP and executed for **both scopes**, using eight workers. It asserts SHA256 of the untouched original printer text, route JSON, and acceptance JSON before enumeration:

- spool: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- routing: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- acceptance: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

The source-selected record must be unique by exact timestamp, job, attempt, ACK and RECOVER metadata. The six altered hexadecimal positions `0,2,5,10,15,19` define a planted synthetic original `4949D0573145E2AF879047215C2559D5`. The SFT calculates a synthetic full component commitment using the **same XOR-mask and SHA256 pathway**. Each original run was required to match that planted commitment **exactly once**, providing a test for multi-character corrections beyond four positions.

| Scope | Complete original target checks | Original matches | Planted six-digit positive |
|---|---:|---:|---:|
| Strict | 524,288 | **0** | **1** |
| Medium | 33,554,432 | **0** | **1** |

Portable reproducer: [Agent10 C++ SFT](../agents/agent10/k04_optical_recapture_sft.cpp). The original local run used an equivalent source with an additional broader, unexecuted mode; the published SFT preserves the two executed strict/medium modes and their exact complete candidate sets. Neither source nor acceptance values were modified.

## Interpretation and next avenue

The original K04 physical coupon cannot be recovered by these **specific** independent position-wise hexadecimal glyph confusions applied to the retained copied ACK. This excludes cases with five or more visual misreadings when every changed character belongs to the enumerated model, beyond the already-known arbitrary-four-nibble lower bound. It does **not** reject realistic OCR errors outside the model, transpositions, clipping, different captured media, upstream generator faults, error-correcting codes or the full 128-bit coupon uncertainty. The copied `A9A9` prefix alone remains insufficient to identify any original nibble.

This family is intentionally limited instead of expanding indefinitely into every possible glyph substitution: its genuine historical applicability is unproved. A newly attested font or visual scan could motivate a better-fitted asymmetric channel with an independent holdout; otherwise research should prioritize a source-selected end-to-end coupon mechanism. No seventh verified component, authentic original coupon bit or complete recovery key was obtained.
