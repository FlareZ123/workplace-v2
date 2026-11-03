# K04: class-specific internal coupon CRC/ECC test, with an affine-coset discriminator

**Agent 45 | 3 November 2026. Original selected printer payload and authentic K04 remain unknown.** This tests an additional physically plausible recovery mechanism: a 16-byte RECOVER coupon may itself contain error-correcting or integrity redundancy. If so, a damaged copied ACK might be repairable from the packet's internal code, independently of the printer's hypothetical RNG.

## Material and distinction from prior work

Original source: `resources/evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Withhold the disputed **row129**, PS-261003-0417 attempt2 RECOVER ACK, before deriving any code. Select the other **37 intact RECOVER ACK** 16-byte payloads. Exclude two surviving RECOVER REQUESTED rows, since requested and acknowledged payloads need not follow the same media stage. The other 93 ACK rows have LABEL/STORES classes and need not share a RECOVER codec.

Prior v1 [printer XOR-span result](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-printer-xor-span-vacuity.md) already established that the **128 mixed-class regular rows** span all 128 bits. That raw-rank observation alone cannot exclude a class-specific internal error-correcting code among only 37 relevant RECOVER ACK packets. Agent48's separate RS(8,6) study concerns *cross-slot REC8 redundancy*, not an internal 16-byte printer codeword. This study probes the different class-specific internal channel.

## A source-only general cyclic-code discriminator

Represent each 16-byte source packet as a GF(2) polynomial in the selected bit layout. If all authentic RECOVER ACK packets share a nonconstant cyclic code generator polynomial `g(x)`, possibly masked by the *same unknown 128-bit XOR constant* across packets, **every pairwise XOR difference** must be divisible by `g(x)`. Thus:

`g(x) | gcd(P1 xor P0, P2 xor P0, ... P36 xor P0)`.

Compute the exact polynomial GCD with binary polynomial long division, under 20 predeclared packet representations: forward/reverse byte order, normal/reversed bit order within each byte, and optional reversal of either first/last two- or four-byte CRC field. All original-source runs returned **GCD = 1 (degree 0)**.

That excludes any *nontrivial fixed binary cyclic generator* shared by all 37 original RECOVER ACK packets under the tested layouts, even with a constant unknown XOR mask or fixed CRC initialization offset. In particular, no such systematic cyclic checksum or BCH-type redundancy can be used to reconstruct the missing ACK from this source-consistent class alone. This is stronger than inferring “no code” from mere 37-row GF(2) rank, which cannot constrain all 128 packet bits.

## Independently defined common integrity families

- **24 conventional GF(256) shortened-RS first-root models**: irreducible 0x11D/0x11B field arithmetic, alpha 2/3, first consecutive root 0/1/2, packet forward/reverse order. A fixed RS code or fixed XOR coset must have a constant first-root syndrome. All 24 original model syndromes varied; between **32 and 37 distinct first-root values** occurred among the 37 packets.
- **12 checksum residual models**: CRC32, CRC-CCITT16 and Adler32; checksum stored in first or last 2/4 bytes; little/big endian. For a fixed-length standard checksum, unknown constant initialization/final XOR still yields a constant residual across all valid codewords. Every tested original checksum residual was different in all **37/37** packets.

**Controls:** A seeded synthetic 37-packet, CRC16-polynomial degree-16 systematic producer is masked by an unknown constant 128-bit XOR value. The method recovers polynomial GCD degree **16** after the mask, and changing one previously valid packet bit reduces the GCD to **1**. This proves the test detects that genuinely code-bearing class and responds to one damaged copy. The original test also verifies the exact class/attempt inventory, log SHA and selected-row exclusion.

[Portable read-only single runnable test](../agents/agent45/k04_recover_affine_cyclic_ecc_sft.py). Inputs: the original resource directory or original source ZIP. Uses Python standard library only. K04 target commitment, selected copied payload as a model input, route mask, K08 and verifier are not accessed.

## Boundary

The result excludes **fixed, same-format affine cyclic-code and tested RS/checksum** repair channels for these 37 historical RECOVER ACK rows. It cannot exclude an arbitrary per-job whitening stream, an error corrector that only accompanied the specific selected incident attempt, nonlinear or variable-layout codes, unrelated printer protocols, an independently authenticated original coupon, or untested representations.

No authentic selected K04 payload bit or 16-byte component was recovered. The six original accepted REC8/1 slots remain PASS; K04 and K08 are MISSING; combined acceptance remains INCOMPLETE.
