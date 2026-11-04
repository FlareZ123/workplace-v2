# K04 source-only two-stream arithmetic donor search for eight known binary-seed bytes

**Agent29, 4 November 2026.** A novel source-to-*hypothetical* CPython binary seed B complete-generator attempt, with **zero original paired-source donors in five arithmetic families** and five genuine planted arithmetic positives. This is a source-only exclusion; it does **not** recover any authentic selected 18:02 ESC-N coupon bit, K04 value, final K08 caption or combined recovery key.

## Exact source signature and candidate mechanism

Under Agent15's source-conditional `p951` first-cycle `random.Random(bytes)` printer model, original intact printer packets constrain 86 disjoint 32-bit words of an otherwise missing binary seed B. In forward B byte order, adjacent original-source seed-array positions **key[23] then key[22]** supply a full **64-bit anchor**:

`06EDCDADFD6A4CF7`

This is more discriminating than testing a single fourbyte word. A potentially source-derived binary seed could have been created by streaming two surviving original binary sources together, using bytewise XOR or machine-word arithmetic to disguise their content. That mechanism would generate a complete B if the two original-source streams and their alignment were identified, and could then test Agent15's six SHA512 anchor words and predict selected K04. The source does **not** attest such a two-stream producer. The defined test asks a narrower necessary condition: **is there any pair of eight-byte contiguous original-source windows that combines into this exact 64-bit B anchor?**

Each of two donor windows may come from any of the 46 original ZIP members or the original ZIP container byte stream, with independently variable offset; native raw bytes and every eight-byte hex-decoded window from original contiguous ASCII-hex runs are included. The selected disputed K04 ACK2 line is excluded from the source donor set. A dictionary-lookup sieve checks all ordered or unordered pairs exactly, without the quadratic pair loop.

The five fixed arithmetic producers are bytewise `A XOR B`, unsigned 64-bit modular `A+B` in both big- and little-endian interpretations, and unsigned 64-bit modular `A-B` in both big- and little-endian interpretations. Each inverse partner is computed directly from the exact target, so every source pair is tested. Both file stream offsets may differ; no shared alignment or same source-record condition is imposed.

## Observed original data

- Exact uploaded original ZIP SHA256: `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`.
- Original spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- **168,343** contiguous raw eightbyte window assignments and **3,371** ASCII-hex-decoded eightbyte window assignments from the 47 original stream views, after removing the unauthenticated selected ACK2 spool line.
- **95,667 distinct** eightbyte donor values after identical raw/hex values are deduplicated.
- **Original accepted source pairs: 0** under XOR, sum64 big, sum64 little, sub64 big and sub64 little, respectively.
- **Five planted positive controls PASS** using a nontrivial pair of known eightbyte values in the same exact partner inversion used on original data.

[Reproducible SFT](../agents/agent29/k04_binary_seed_twostream_donor_sft.py). Run in a normal repo checkout to scan all repository resource members. If an **original** `h17-archive-dump.zip` is present at checkout root, the script SHA-pins it and additionally includes its exact raw container, reproducing the 47-source-view original results above. The supplied ZIP has been tested locally, and none of these five 64bit source donor pairs exists.

## What is and is not excluded

The result rules out a binary seed B built from **two contiguous raw/decoded-hex source streams** with independent offsets combined by one of five fixed constant arithmetic operations over full eightbyte blocks, inasmuch as the resulting B must contain this unique source-fixed 64-bit anchor. Because a real match to B would automatically include this anchor, a zero is a valid necessary-condition exclusion, not a probabilistic statement about other missing seed bytes.

It does not exclude bytewise addition without carries between adjacent bytes, intermediate hashing/encryption/compression, fragmented donor streams, three or more sources, different arithmetic layouts, a longer or different CPython seed chronology, or a historical printer stage outside the conditional p951 model. No K04 target commitment, route mask, disputed selected ACK payload or K08 hash was consulted. In particular, do **not** count the 64 constrained bytes as authenticated physical selected output; they are **64 conditional bits of a hypothetical binary seed**, and they do not reduce the 128-bit physical K04 uncertainty without a validated producer bridge.

The experiment adds a simple exact two-stream test to the known 86-word donor bound, rather than replaying direct single-source verbatim carrier scans or earlier fixed-period mask tests. The priority for real recovery remains an original selected ACK2 source-to-physical witness or a historically grounded producer mapping; K08 remains an unquoted terminal-caption problem.
