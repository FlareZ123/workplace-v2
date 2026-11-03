# K08 binary-component recovery without terminal caption reconstruction

**Agent47, 3 November 2026. Original K08 component not recovered.** The exact final Emily keeper-envelope words remain absent; the original six accepted slots still pass, K04 and K08 are missing, and combined REC8/1 acceptance remains INCOMPLETE.

## New mechanism tested

The untouched original verifier accepts a **16-byte K08 component** on SHA256 equality; the source route generates it using HMAC-SHA256 of the exact normalized missing caption. A different, speculative reconstruction path might construct the same component from independently retained **binary archive fields**, even without recovering the sentence itself. This experiment tests whether any two 16-byte source carriers can produce that component through a compact arithmetic/hash operation.

The original source has **no documented binary K08 relation**. This is an exploratory full-candidate test; a hit would need historical corroboration. It is distinct from the previously published 1–40-word literal-source HMAC spans, N-note indexed word extraction, short editorial rewrites, crossslot Reed–Solomon erasure interpolation and K04 source-word mosaics.

## Source set and frozen functions

The locally uploaded 46-file historical ZIP was read without modification. The selected disputed 18:02 UTC ESC-N printer ACK2 copied payload was **explicitly excluded**. Exactly **533 distinct 16-byte candidate inputs** were derived from exact 32-hex-character original evidence fields, recorder CONTROL fourword groupings in original/sorted/node-specific order, AX checkpoint eight-halfword groups, RC17 footer quartets, telemetry eight-halfword windows, original seal serial quartets, the six accepted REC8 components, several un-hashed reduction inputs, and the known HMAC16 values for Emily's surviving N02/N06/N17/N18 drafts and labels.

Source facts pinned in the executed local program include the notes SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, original K01 component SHA256, and exact N02 draft HMAC first16 `BF889359B0303F2B2B2FD96AE841210B`. The original K08 desk nonce and original K08 slot commitment were read unchanged.

Each unordered pair of source values `A,B` generated one complete 16-byte K08 candidate under each of **nine** rules:

1. `A XOR B`
2. `A + B modulo 2^128`
3. `A - B modulo 2^128`
4. `B - A modulo 2^128`
5. `SHA256(A XOR B)[:16]`
6. `SHA256(A || B)[:16]`
7. `SHA256(B || A)[:16]`
8. `HMAC-SHA256(desk_nonce, A || B)[:16]`
9. `HMAC-SHA256(desk_nonce, B || A)[:16]`

Each candidate's complete 16-byte value was hashed and compared against the original untouched K08 SHA256 commitment. The algebraic arithmetic uses 128-bit big-endian interpretation; concatenation and XOR operate on raw bytes. No partial acceptance oracle, modified verifier, or supplied final-caption text was used.

## Original experiment and positive control

- **533** original-source binary carriers.
- **142,311** unordered source-carrier pairs with repetition.
- **1,280,799** complete candidate assignments across the nine rules.
- **Zero** original K08 acceptance matches.
- **One** planted positive for a nontrivial XOR of two retained source values. The same enumeration recovered it.

The executed read-only source-pinned SFT is available as a session file `/mnt/data/h17agent47_20261103/k08_binary_bypass_sft.py`, SHA256 `a08c0727b2e2cb36a9836edfc69866871a1da835eb465292ec4fadbba19a677e`. A separately committed portable repository SFT [using Agent22's extended carrier extraction](../agents/agent47/k08_binary_component_source_pair_sft.py) preserves the mechanism. Its input set may differ slightly from the locally frozen 533-carrier implementation and should be executed on a fresh checkout before attributing identical cardinalities to that adaptation; the exact figures above are from the executed local script.

## Interpretation

These results exclude only the specified pairwise byte/arithmetic/hash/HMAC derivations from the locally selected original-source carriers. The failure gives **no original K08 caption word**, and no partial bits of the correct K08 component. The source does not assert that the binary records directly encode Emily's HMAC; adding arbitrary third operands, transforms or larger source sets without a selecting original cue would be an open-ended guess.

The conceptual distinction remains useful: recovering the **component value** is sufficient for the verifier, even if the caption is no longer reconstructible, provided a source-grounded alternative relation exists. The tested finite binary relations do not supply that relation. K04 and the original full recovery key remain unresolved.
