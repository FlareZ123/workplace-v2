# K08: exhaustive ordered one-word selections from all eight Emily notes

**Agent 11, 3 November 2026.** The original K08 commitment had **zero matches across 723,945,600 distinct complete eight-word captions** under a finite record-structured mechanism. A synthetically planted complete caption matched **exactly once**, and the original N02 HMAC control passed. This is a scoped negative, not a recovered K08 word. Six accepted REC8 slots remain valid; K04/K08 and combined acceptance remain unresolved.

## Independent structural hypothesis

The preserved crew-board file has exactly eight note entries authored by Emily: **N02, N06, N10, N13, N17, N18, N20, N23**. Unlike the older nonce-index selector (Agent 17, `agents/agent17/k08_nonce_indexed_eight_notes_sft.py`) and the 19:04 structured ID/mail-index pilot (Agent 24, `results/h17-k08-structured-note-mail-index-shuffle-pilot-20261103.md`), this experiment makes **no guessed per-note index choice**. It tests the entire ordered one-token-per-note message channel.

The construction is based on the hypothesis that the final keeper caption is an eight-word text whose word at position i occurs somewhere in Emily's ith surviving note. The source itself does not attest this encoding, the caption's exact length, or the use of older N17/N18 envelope labels. This is an exploratory complete-candidate mechanism with a clear exhaustive bound.

## Source-to-candidate construction

Immutable original source: `resources/evidence/crew/noticeboard-and-desk-notes.txt`, SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. For each of the eight Emily notes in ascending N-ID, strip an explanatory prefix through the first colon when one exists, lowercase, and tokenize maximal ASCII alphanumeric spans. Deduplicate word identities *within* each note while preserving first occurrence order. This gives the ordered per-note vocabulary sizes:

`N02=12; N06=10; N10=21; N13=18; N17=7; N18=5; N20=24; N23=19`.

Take the Cartesian product, join eight tokens by one ASCII space, and calculate the original K08 commitment reduction:

`SHA256(HMAC_SHA256(hex desk_nonce, UTF8(candidate))[:16])`.

Use the original desk nonce `5F933DA6A1BD03C32DA5CBC25344F497` and original K08 SHA256 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`; do not mutate these or the official checker. The enumerated strings are pairwise distinct because each note's vocabulary was deduplicated. The exact exhaustive count is `12×10×21×18×7×5×24×19 = 723,945,600`.

## Executed original-data outcome

The C++17/OpenSSL SHA256 SFT preinitializes the 64-byte HMAC inner/outer pad states and evaluates the complete K08 reducer exactly once per distinct phrase. It partitions work by each of the twelve first-word possibilities and uses independent threads. The source-digest pin and the known original N02 first-draft prehash control `BF889359B0303F2B2B2FD96AE841210B` are asserted.

- **Original commitment:** 0 matches in all 723,945,600 complete eight-word captions.
- **Synthetic planted complete caption:** `watch stays meant mugs watch back wanted in`; exactly **one** match within the same exhaustive search, exercising the full HMAC16/outer SHA256 path.
- **Independent small pilot:** 60,328,800 candidates (first N02 unique token only), 0 original hits; full test covers the other eleven first tokens too.
- **Full original run:** completed in 134.991 wall seconds on the supplied attached original 46-member ZIP's crew-notes file. The source and verifier/acceptance files were read-only.

Reproducer: `agents/agent11/k08_emily_eight_sft.cpp` (C++17, OpenSSL libcrypto). Compile and run against the original crew-notes path. The script prints both exact commitment hit counts, planted hit count, per-prefix counts, and wall time.

## What this changes

The actual K08 normalized caption cannot be **exactly eight words, one word from each Emily note in original N02→N23 order**, under the stated ASCII tokenization and explanatory-prefix exclusion. This excludes a complete structural carrier that is substantially larger than the earlier 5,367,600 nonce-indexed eight-note family. It does not rule out different ordering, omission of N17/N18 as superseded labels, multiple words from one note, unseen words, a free editorial rewrite, or an independent original margin. No authentic K08 word has been recovered.

This branch should not be reflexively widened to arbitrary combinations and word orders: without independent evidence for the eight-note carrier, such superfamilies quickly become another unconstrained caption lottery. A new exact version-selection mechanism or source-authenticated final caption would justify renewed targeted computation.