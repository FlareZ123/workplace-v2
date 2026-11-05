# K08: single-byte obfuscated literal-caption transport across all original evidence files

**Agent 49 | 5 November 2026 | 7,164,804 distinct original-source complete normalized captions; zero original acceptance matches.**

## Target-reaching hypothesis

The source-derived K08 captions N02/N06 and old envelope labels N17/N18 are preserved as ordinary text, but the terminal final keeper caption is only referred to by MAIL11, MAIL20 and N23. A different literal-transport mechanism from editorial paraphrase could have retained the missing text in an encoded binary/string field, recoverable by a common trivial one-byte copier transformation. The source does **not** identify such an encoder or a terminal phrase carrier; this is a bounded exploratory test for that possibility.

## Exact original-source test

Original read-only `resources/evidence/` 42 files, including the recorder binary and the encrypted 2025 PDF bytes, with original SHA256 checks pinned on the crew note, route, acceptance files. For each file independently, apply:

1. All 256 bytewise XOR transforms, `decoded[i]=raw[i] XOR k`.
2. All 256 bytewise modular subtract transforms, `decoded[i]=(raw[i]-k) mod 256`.
3. Standard Latin-1 ROT13 on ASCII letters, preserving other byte values.

For each decoded stream, extract maximal contiguous printable ASCII runs of **at least eight bytes**. Tokenize ASCII alphanumeric words; test all contiguous **2–24 word** subruns with at least seven normalized bytes. Normalize words as lowercase joined by one space, then perform the untouched original K08 reducer: `HMAC-SHA256(desk_nonce, candidate)[:16]`, followed by SHA256 of those 16 bytes versus the full original K08 acceptance digest.

The test counts **7,164,804 distinct normalized original-source candidates** after deduplication, with **zero authentic K08 commitment matches**. The ordinary original-source control strings N02 first draft, N17 standby label, and N18 commissioning label are all extracted intact. An independent synthetic final-looking phrase hidden under XOR key `0x93` is recovered via the same 256-key decoding and nested commitment calculation. The test does not change original evidence or any commitment.

[Source-pinned single-file reproducer](../agents/agent49/k08_xor_add_rot13_literal_transport_sft.py). The exact local computation took approximately 31 seconds; the committed portable code uses the same source, search grammar and expected unique count.

## Scope and next direction

This closes the specified **single-byte XOR/modular-add and ROT13 literal-carrier family**, including hidden strings whose recovered text is 2–24 words contained in one printable run. It does not cover multi-byte repeating keys, full-block ciphers, compressed or separately fragmented text, UTF-16 text, captions crossing line breaks, or a final phrase absent from the export. The emitted candidate set is still conditional on the displayed text-window grammar. It does not authenticate any true K08 word.

This is mechanically distinct from v1's 618,316 **untransformed UTF-8** source spans and the numerous prose-edit and language-model-generation attempts, and from v2 Agent5's encoded **HMAC16** cross-record common-pad tests: here the candidate message itself is reconstructed from a hypothetical encoded **literal plaintext carrier**.

The original REC8 verifier still accepts only K01,K02,K03,K05,K06,K07; K04 and K08 are unresolved and combined acceptance remains INCOMPLETE. No recovered physical K04 bits or final author-selected K08 words are claimed.
