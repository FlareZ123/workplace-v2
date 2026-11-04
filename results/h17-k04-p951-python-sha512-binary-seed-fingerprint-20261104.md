# K04: source-derived 192-bit SHA-512 fingerprint for a hypothetical binary Python seed

**Agent 15 | 4 November 2026 UTC.** A new *source-constrained complete-seed discriminator* under the unverified printer p951/CPython first-output first-cycle model. **Six exact 32-bit words (192 bits) of a potential SHA-512 digest are recovered from original intact printer packets, with the selected coupon excluded.** The six are a model-conditional fingerprint of the proposed **seed input**, not physical selected-coupon bits. Original K04 remains MISSING and K08 remains MISSING.

## New route toward a full source-seed producer

Python's standard `Random(bytes, version=2)` seeds from `B || SHA512(B)`: convert the concatenation as a big-endian integer and initialize the Mersenne Twister using its little-endian 32-bit words. For hypothetical original integer seed-array lengths **606..623**, the lowest sixteen `key[j]` words are wholly determined by the 64-byte `SHA512(B)`, regardless of the size or bytes of `B`.

With initialized 624-word CPython register `S`, invert the documented two-pass `init_by_array` equations at triple `S[j-1],S[j],S[j+1]` to obtain `T[j]=key[j]+j mod 2^32` for a source-constrained triple in the single-pass regime. The earlier [source-reconstruction report](h17-k04-p951-gf2-seed-initialization-cross.md) used such terms chiefly for *integer-key-length repetition*. This investigation recognizes a distinct cryptographic implication: for low indices `j<16`, the same exact terms are **byte slices of the unknown seed's SHA-512 digest**. Those slices can screen a specific original binary seed candidate `B` before any K04 target or copied ACK is consulted.

The 132 unchanged intact original printer packets, with the disputed row129 withheld before decoding, give a GF(2) base of **rank 15,365** for the hypothetical native register. CPython's mandatory `S[0]=80000000` increases rank to **15,397**. Six source-fixed triples produce these exact 32-bit big-endian SHA-512 digest words of `B`:

| `key[j]` = digest big-endian 32-bit chunk | Original-source required value |
| ---: | --- |
| 3 | `04ADA358` |
| 4 | `70935318` |
| 5 | `61C74260` |
| 9 | `900C8064` |
| 10 | `3C3DF54F` |
| 11 | `B8BC5EA5` |

The chunk offset into `SHA512(B)` is `[64-4*(j+1) : 64-4*j]`, interpreted as a big-endian integer. Every candidate `B` under this producer/length hypothesis must satisfy **all six exact conditions**, a 192-bit source-only candidate filter. It can eliminate or exceptionally identify a small candidate corpus of binary seeds by a single standard-library SHA-512 evaluation per seed, instead of enumerating candidate K04 coupons. The 192 constrained bits do **not** mean 192 authenticated bits of the missing 128-bit selected K04 payload.

## Additional original-source SHA-512 fingerprint via the CPython seed-key index wrap

The baseline six SHA-512 words contribute 192 constrained digest bits to **every** remaining n606..623. The initialized-register source also fixes two near-terminal reverse key terms that earlier investigations used for key-length repetition rather than SHA-512 fingerprinting:

- `T[607]=13231B97` exactly, because original S606..608 are all fixed.
- `T[608] ∈ {5D3DC8B5, DD3DC8B5}`, because original S609 has one unresolved high bit.

In standard CPython `init_by_array`, the key is cyclically indexed by `j mod n`, and the additive constant is the same residue. For `n606..608`, these original native-register terms therefore refer directly to **additional digest words** `key[0..2]` from SHA-512's appended 64-byte suffix. They produce the following *additional* SHA-512 digest chunks over the six baseline words:

| Assumed key length | Additional digest chunk(s) from original source | Digest bits constrained in total |
| --- | --- | ---: |
| n606 | `key[1]=13231B96`, `key[2] ∈ {5D3DC8B3, DD3DC8B3}` | **255** |
| n607 | `key[0]=13231B97`, `key[1] ∈ {5D3DC8B4, DD3DC8B4}` | **255** |
| n608 | `key[0] ∈ {5D3DC8B5, DD3DC8B5}` | **223** |
| n609..623 | No additional digest chunks from these two late terms | **192** |

A two-option 32-bit word constrains 31 bits. These 255/223/192 figures are independent positions in a **hypothetical seed's SHA-512 digest**, not authenticated original K04 coupon bits, and do not support identifying the unknown source seed without a historical candidate.

The updated SFT independently recomputes both late original-source terms from the **same 132 original intact printer packets** and additionally executes two complete synthetic source-spool positives at n607 and n608, besides n606 and n623. For each seeded stream, it verifies the authentic `T[j] = key[j mod n] + (j mod n)` value appears in the source-derived term set, including the wrap boundary. **[CI run 41746140738 SUCCESS](https://github.com/FlareZ123/workplace-v2/actions/runs/41746140738)**. This is a stronger fingerprint for n606..608, with no target commitment used in selection.

## Reproducible synthetic and original-source controls

The [standalone Python SFT](../agents/agent15/k04_p951_sha512_seed_fingerprint_sft.py) builds its own 1,601-word symbolic native MT linear recurrence, derives the source register basis and the exact low key words, and pins original printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. It never decodes the disputed selected ACK2 row129, reads no route mask or K04/K08 commitments and does not touch the original verifier. The source constraints are independent of whichever K04 component would eventually be accepted.

To detect accidental mathematical or byte-order inversion, the SFT constructs **two complete synthetic genuine CPython `random.Random(bytes)` printer spools** with 2,360–2,430-byte non-UTF-8 binary seed inputs, at key-array word counts 606 and 623. Each synthetic spool uses exactly the original 133 source-index positions and withholds row129; its 132 source packets alone reproduce six authentic SHA-512 digest chunks of its *known* random bytes seed. Both full-source controls pass exactly, making the recovered fingerprint a demonstrable seed-identification discriminator on systems actually generated by this model.

The same script then reconstructs the original 132-row source and asserts exactly the six values above. [Actions run **41745304538** completed SUCCESS](https://github.com/FlareZ123/workplace-v2/actions/runs/41745304538). Original target-hash matches were not requested or claimed.

## Relationship to the separate text-seed exclusion

The companion [UTF-8 source-byte impossibility](h17-k04-p951-cpython-utf8-text-seed-source-gate-20261104.md) uses direct higher key-word constraints `T22` and `T608` to exclude **text** seed arrays of n364..1229. A **binary** CPython seed can legitimately contain `F7`, `C6`, or other invalid UTF-8 bytes, so that argument does not apply to arbitrary `bytes`.

For the remaining original n606..623 model branch, however, a binary seed `B` would have to supply both (a) the exact SHA-512 192-bit fingerprint here, and (b) source-forced raw bytes `FD 6A 4C F7` at the last 28..24-byte region of its input (the full source basis removes an earlier ambiguous `7D...` case). The 46 files of the supplied 50,526-byte ZIP contain no such raw four-byte substring. This excludes **verbatim individual source-file inputs and their direct substrings** as the seed `B`, but does not exclude independently generated, encoded, or source-transformed binary seeds.

## Stronger source-to-binary-seed reconstruction and donor threshold

A further use of the **same existing 94 source-fixed/near-fixed CPython key terms** is to interpret `key[j]` at `j>=16` as actual four-byte pieces of **the binary seed input B** immediately preceding the 64-byte SHA-512 suffix. The inverse key word's big-endian byte representation has the exact offset in the original seed:

```text
B[len(B)-4*(j-15) : len(B)-4*(j-16)] = key[j].to_bytes(4,"big")
```

The equation holds for every possible n606..623 for key positions `16<=j<=602`, and is agnostic to leading partial seed words. The original intact 132 printer rows supply **86 disjoint constrained original binary-seed word positions**, much stronger as a direct source-matching signature than the six SHA-512 digest chunks alone:

| Direct seed-input constraints | Value |
| --- | ---: |
| Distinct four-byte positions `j=16..602` supported by original data | **86** |
| Full 32-bit fixed words | **62** |
| Two-option 32-bit words differing in one bit | **24** |
| **Individual seed-input bits fixed under the generator model** | **2,728** |
| Distinct four-byte allowed values across those positions | **110** |

Illustrative exact source constraints: `key[22]=FD6A4CF7`, `key[23]=06EDCDAD`, `key[601]=49342EC0`; `key[602]∈{64589C88,E4589C88}`. The `seed(bytes,version=2)` case must satisfy all 86 position-constrained values **and** the six digest chunks, plus the optional wrap constraints for n606..608. As before, **these are bits of a hypothetical seed input**. They do not fix or authenticate the missing selected 16-byte K04 coupon.

### Original-file donor coverage and a minimum-fragment theorem

On the **exact original uploaded ZIP** (ZIP SHA-256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`), compare all 110 permitted four-byte values against the 46 original regular member bodies **and the raw ZIP container**. Scan each sliding four-byte raw window and every sliding eight-hex-digit window of maximal ASCII hex runs, with both nibble phases included.

- **47 carrier streams**, 168,658 raw four-byte windows and 4,765 decoded-hex four-byte windows scanned.
- **Zero** matches to any of the 110 source-required seed word values.
- Synthetic control injected the source-required `key[22]` as raw bytes and `key[23]` as ASCII hex; the unchanged scanner recovered **exactly two** seeded hits.

This produces a stronger, rigorously bounded conclusion than the earlier isolated `key[22]` absence: **a proposed B made solely by concatenating contiguous raw-source or decoded-hex carrier fragments would require at least 87 separate fragments.** Proof: all 86 constrained four-byte seed windows are disjoint and none occurs intact in any permitted carrier. Each such window must therefore straddle at least one concatenation boundary; one boundary can interrupt at most one of the 86 disjoint windows. Hence there must be at least 86 boundaries and at least 87 pieces.

The theorem is strictly about **verbatim concatenation of original preserved byte spans**, including direct hex decoding, under a generator model whose historical application remains unknown. It does not rule out a seed drawn from OS randomness, a seed made from external/unrecovered material, a cryptographic transform, an encrypted/compressed-derived seed, arbitrary per-byte transformations, or a different print production method. The lack of four-byte matches is expected when comparing only 110 random-looking values against a small archive; it is a conditional provenance bound, not an independently positive signal of CPython.

Reproducer: [source-pinned sparse-seed donor SFT](../agents/agent15/k04_p951_sparse_seed_donor_sft.py), which re-derives the 86 word domains from the original 132 safe source packets using the fingerprint SFT, includes a two-path planted positive, and accepts the uploaded ZIP for full 47-stream coverage. Local execution against the original uploaded ZIP independently reproduced the exact counts above. The complete binary-seed derivation is also now included in [the companion 4-spool SFT](../agents/agent15/k04_p951_sha512_seed_fingerprint_sft.py); its newest CI invocation is queued while other research workloads run, so no unobserved CI success is claimed here.

## Limits and useful next crack

The source documents never establish CPython, the p951 output positions, a first-output initialization epoch, or the specific binary seed. All assertions here are conditional on that model. A matching six-chunk SHA512 fingerprint is **strong evidence for a specific proposed seed within the model**, but it is not by itself proof of the physical printer/copy stage. An actual complete seed can be advanced to a full withheld selected-output prediction and checked with the untouched original K04 slot commitment.

New actionable research, if a historically attested binary source `B` emerges: compute `SHA512(B)` once and check these six chunk positions; only if all match regenerate the original source stream and selected 128-bit coupon. Do not manufacture open-ended binary transformations simply to fit 192 known digest bits. **K01/K02/K03/K05/K06/K07 six PASS; K04/K08 unresolved; REC8/1 combined INCOMPLETE.**
