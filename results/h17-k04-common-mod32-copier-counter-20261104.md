# H-17 K04: 32-bit common modular counter copier fault, complete original commitment exclusion (4 Nov 2026)

**Agent 42. New complete target-facing bounded experiment. Original source K04 hits: ZERO across 25,769,803,776 tested assignments.** One genuinely planted full-coupon target was recovered exactly once. This does **not** recover K04 bytes or K08 wording; original six accepted components remain PASS, the two missing components remain MISSING, and combined REC8/1 is INCOMPLETE.

## Distinct hypothesis

The surviving 18:02 ESC-N copied ACK2 payload contains four opaque 32-bit words. Its SHA is not authenticated as the physically printed coupon. One specific plausible *copy-stage counter displacement* is that a common unknown 32-bit integer was **added modulo 2^32 to each physical 32-bit coupon word** when the log was recorded. A monotone lane number may have entered the same integer counter.

This is genuinely distinct from Agent2's [source-value subset additive retry](h17-k04-retry-additive-word-producer-sieve.md), which adds different combinations of four *known* same-job buffers, and from Agent41's [unknown shared north/south 16byte additive pad](h17-k04-cassette-shared-additive-pad-five-groups-20261104.md), where a second source cassette cancels the shared pad. It is also distinct from an identical perword XOR error (bitwise addition has independent carries) and independent four-byte replacements. **The source documents do not attest a counter displacement, let alone any selected arithmetic slope.** This is a frozen exploratory architecture.

Let `C_i` be the four 32-bit words from the exact selected copied payload `A9A9DC5731A5E2AE879C47215C2559D5`. For all 32-bit `k`, original word byte orientations `little` and `big`, and counter slope `s∈{-1,0,+1}`, construct a whole *hypothetical physical coupon*:

```
Q_i = (C_i - k - s*i) mod 2^32, i=0,1,2,3
coupon = serialize(Q_0,Q_1,Q_2,Q_3, original word endian)
component = coupon XOR 8556C8CB6140A7F9A5123AC7571BEE1C
```

For every assignment check the **complete, unchanged original** SHA-256 component target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The three slopes include a uniform added counter (`s=0`) and rising/falling perword counter increments (`s=±1`). The two byte views each preserve the order of all four original 32bit word lanes; no arbitrary word permutation or invented independent perturbations.

## Execution and reproducibility

Use [single-file original-source-pinned C/OpenSSL SFT](../agents/agent42/k04_modular_counter_sft.c). The original 46-member uploaded ZIP was extracted read-only and validated for each shard, using independent original SHA256 source pins:

- Printer reconstruction: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Recovery routing: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.
- Acceptance: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

The fast single-block SHA256 compression is independently tested against OpenSSL's general `SHA256()` on a complete planted coupon. A synthetic physical coupon is generated from the original copied bytes under little endian, slope+1, unknown counter `k=A5301F69`. The *same 64-shard full target loop* finds its synthetic SHA256 exactly once, in shard41. No original target match occurs anywhere. This is a planted **test** digest, never the official acceptance commitment.

Each shard enumerates exactly `2^26 = 67,108,864` disjoint key values; 64 shards cover all `2^32` unsigned 32-bit keys. Each shard checks all six fixed serializer/slope branches, hence `64 × 2^26 × 2 × 3 = 25,769,803,776` complete original full-SHA256 computations. A five-process local runner checked 64/64 shard exit statuses, each shard's six mode summaries and exact count, every original hit count zero, and the unique planted-positive count one. SHA256-compression and full original-target comparisons were performed on unchanged component reductions, with selected ACK2 copied payload as input.

```text
RUN_COMPLETE {
  "shards":64,
  "keys_per_shard":67108864,
  "models_per_key":6,
  "complete_checks":25769803776,
  "original_hits":0,
  "planted_hits":1,
  "planted_key":"A5301F69",
  "planted_shard":41,
  "seconds":311.3
}
```

The original local 64-shard result JSON SHA256: `ba8481c523580140c21d5f49e550ebbf2947789dfe4e2091e12a04bbe20a3d06`. The local executed C source SHA256 is `4039324d1aa8335de95f21e7b2f97347e2320d696c745532d8a9a25bc2e8225d`; the checked-in file differs by **four bytes in introductory comments only** and uses the identical hashing and coupon enumeration path. GitHub code committed as `5c1cde3c4cdcdc74693f60e6770a6e3ce357872d`; remote file readback succeeded. This was a **local completed** full test, not a GitHub Actions run.

## Boundary and next crack

**Exactly excluded:** copying the physical 16byte coupon by adding a single unknown common 32-bit word offset plus slope−1,0,+1 per 32bit lane, in either endianness, with lane order fixed, and original route XOR. The result does **not** exclude perword independent offsets, nonlinear differentially clocked encoding, copy-stage missing words, byte-lane reassembly, another physical source, or unrelated actual coupon bytes. The nonce and K08 caption are independent of this test.

No reason now to increase the same 32bit k range (it is complete) or repeat the exact arithmetic model. A stronger successor would need a source-observable **counter value or transformation selector** from a second original physical/print witness, or a true same-class heldout that predicts an *entire* historical coupon before the target hash is consulted. Otherwise pivot to a distinct producer, **not** a more permissive arbitrary k/drift parameter lottery.

Official evidence, source-selected six components, route, acceptance, verifier and canonical candidate were not modified.
