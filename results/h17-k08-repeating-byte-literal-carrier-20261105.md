# H-17 K08: original-source repeating-byte literal transport screen

**Agent12 | 5 November 2026 | K08 remains unresolved.** This probes a different source-to-literal mechanism from one-byte XOR/ROT13 carrier sweeps and source-keyed 16-byte pads: **unknown repeating XOR or modular-add byte keys of period up to eight**, where a terminal normalized caption might have survived as an obfuscated *text string* in any original evidence file. Nothing in the original source attests such an encoder, so this is a bounded exploratory screen.

## Source, inference and result

The 42 original files under `resources/evidence/` contain **112,388 bytes**. Crew-note source SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` and original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747` are pinned by the executable test. Source files and the official acceptance/recovery rules are read-only.

For each candidate contiguous original ciphertext window, independently permit **every possible 256-valued byte key at each position of the period**. A window is feasible if *all* decoded bytes belong to the fixed alphabet ASCII letters/digits/space/common sentence punctuation. This is an exact necessary condition, independent of speculative words, and requires only a tiny eight-lane bitset intersection per window. The two tested period/length frontiers are 48 contiguous decoded characters with period 1–4, and 64 contiguous decoded characters with period 1–8, each under both bytewise XOR and modular subtraction (decryption of modular-add ciphertext). Select windows with at least one raw byte outside ASCII printable/tab/newline/carriage return, because the hypothesis tests a binary-looking carrier, excluding routine unencoded text.

**Original outcome:** all **four** frontiers have **zero feasible encoded windows**. Consequently, this defined mechanism produces no original K08 complete caption candidates. This is stronger for the exact specified long-text representation than simply failing to guess a particular phrase, but says nothing about captions shorter than the windows or encoded with a longer/nonperiodic key, alternate alphabet, fragmentation, UTF-16, compression or ordinary undamaged ASCII.

Independently, a known-plaintext calibration scans four verbatim existing Emily notes/labels (N02, N06, N17, N18) for exact repetitions under *all* arbitrary repeating XOR/add pads of period 1–16, requiring at least 12 bytes of periodic consistency. **158** matches appear, all zero-pad direct appearances in the original crew-note file. **Zero nonzero-key known-caption replicas** occur anywhere in the 42 files. This is a source-only transport calibration, not proof no terminal caption was separately encoded.

Synthetic controls PASS: one entire old label encrypted with an actual period-4 XOR key, one long unknown-plaintext window encrypted with that key, and an independently modular-add encrypted long window are all detected and decoded at their known positions. The arbitrary-window feasibility test is exact for its fixed length/alphabet/period and does not depend on language-model ranking.

## Reproducer, limits and decision

[Single-file read-only SFT](../agents/agent12/k08_periodic_literal_carrier_sft.py) runs from the repository root through its own path resolution and uses Python plus NumPy. An equivalent local original-source run completed with `SOURCE_FILES 42 BYTES 112388`, `KNOWN_LABEL_MATCHES 158 nonzero_pad 0`, and zero feasible windows at the four frontiers, with three planted positives. The original source ZIP evidence and nonce were never changed.

Do **not** generalize this negative into an absence of the final caption, and do not add arbitrary ciphers without a source-proposed transport stage. A more productive new hypothesis would establish a specific historical author-to-envelope literal custody transition or a source-keyed final-only representation absent from this periodic-byte class. K01/K02/K03/K05/K06/K07 remain accepted; K04 and K08 remain unresolved and the combined verifier has not passed.
