# Original ZIP-stream and printer join-key source-boundary pilot (5 November 2026)

**Agent13, normal research mode.** This pilot responds to the 04:47 Critic's request for an *independent compressed representation* and 13:06 Critic's proposed *collision-aware printer job assembly*. It uses the original 50,526-byte attached H-17 archive, SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`. The 46 extracted regular member contents are already known equal to `resources/`; this specifically checks **unextracted ZIP compression choices** and actual key collisions. No original verifier, source or candidate is changed.

## A. Compression-carrier test

Parsed all 56 local ZIP entries (46 deflated files, ten stored directories), **local** member extra fields and compressed byte intervals. Every one of the **46 original raw DEFLATE streams is byte-for-byte identical** to `zlib.compressobj(6, zlib.DEFLATED, -15)` applied to the corresponding unmodified member contents on Python 3.13's zlib. Every file has the standard four-word 16-byte signed data descriptor containing matching CRC and sizes. All 56 local entries are contiguous without padding or inter-record bytes. Neither the archive nor individual files contain ZIP comments, and the standard 22-byte EOCD is terminal.

A subtle but important parsing point: the local headers have **32-byte extra fields**, with UNIX UID/GID `0x7875` plus extended time `0x5455` containing *three* time values; the central-directory member extra is only **24 bytes**, with one extended time value. These fields are **not byte-identical**. The actual 56 local extras fall into six predictable filesystem-time templates (20 mail files share one); the all-files-local-header mismatch would mislead a direct `ZipInfo.extra` comparison. Their atime/ctime data add no observable individualized hidden message under this inventory.

**Inference:** An alternate legal DEFLATE encoding, unconsumed compression padding, locally inserted filler, ZIP comment, or deliberately altered compressed block stream is **not present** relative to the locally available standard zlib level-6 packing. This is evidence about the ZIP representation only: it does not exclude steganography in *uncompressed evidence contents*, a deliberately chosen archive input file order, or other external sources. It supplies zero K04 bits and zero K08 terminal words.

## B. Explicit spool assembly collisions

Parsed all **133** original copied printer records from the original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Grouping identical keys gives:

| Reconstruction key | Duplicate key groups | Extra rows collapsed |
| --- | ---: | ---: |
| `JOB` | 2 | 4 |
| `(JOB, ATTEMPT)` | 1 | 1 |
| `(JOB, CLASS, ATTEMPT)` | 0 | 0 |
| `(JOB, STATE, ATTEMPT)` | 0 | 0 |

The `(JOB, ATTEMPT)` collision is **0417 ATTEMPT1**: 16:45 `ACK CLASS=LABEL` and 18:01 `REQUESTED CLASS=RECOVER`. The **selected 0417 RECOVER ACK2 at 18:02 remains the sole record with `(JOB, ATTEMPT)=(0417,2)`**, so a pure exact-key join keyed at least by `(JOB, ATTEMPT)` cannot replace this selected copied payload by collision. At the coarser `JOB` level, 0417 has four states/events and 0420 has two; 0420's later 18:25 RECOVER ACK2 is a valuable intact heldout of coarser job-only cache behaviour. A synthetic duplicate of the selected ACK2 was correctly flagged in the test.

**Inference:** A collision-based *complete target-reconstruction* hypothesis needs a separately observed **coarse job-only cache or cross-event buffer-transfer rule**, including explicit consequences for 0420, before claiming that it changes selected original physical coupon bytes. Merely pointing to repeated identifiers or relabeling the route selector is inadequate. Simple whole-payload replay and lane mosaics already have separate previous negatives; no target SHA checks were launched in this pilot.

## Reproducer and outcome

Portable, read-only standard-library [single runnable source test](../agents/agent13/agent13_zip_and_spool_source_boundary_sft.py), run against the unchanged attached ZIP. Its 46 compression comparisons, descriptor checks, local-entry boundaries, six timestamp templates, collision count and injected-key-positive test all **PASS**. It performs no K04/K08 commitment guessing.

**Status:** no recovered original K04 physical payload or K08 author-final caption. The original six individual REC8/1 PASS checks stand; K04 and K08 remain MISSING; combined acceptance remains INCOMPLETE. The work narrows two independent-carrier hypotheses and points research toward a genuinely witnessed record/buffer transfer or new source outside these two encodings.
