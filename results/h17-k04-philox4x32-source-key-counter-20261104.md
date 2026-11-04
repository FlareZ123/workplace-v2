# K04 Philox4x32-10 counter-based emitter with source-heldout packet controls

**Agent 16 | 4 November 2026 | New bounded producer mechanism, original K04 NO_MATCH.** The unchanged authentic recovery status remains six individually PASS components (K01/K02/K03/K05/K06/K07), missing K04/K08 and combined REC8/1 INCOMPLETE.

## Question and producer distinction

Unlike a stateful Mersenne Twister, xorshift, PCG, SHA/HMAC or AES-CTR stream, **Philox4x32-10** produces a full 128-bit block deterministically from a 128-bit counter and a 64-bit key. It is a recognized counter-based generator with four native 32-bit outputs per block. This property could, *if a supported printer implementation and counter/key convention existed*, generate a complete original K04 coupon directly from an exact job identifier, without copying the disputed ACK2 payload. This is an **experimental mechanism, not an inference that the historical printer used Philox**: no surviving firmware, vendor instruction or print-coupon documentation selects it.

Official algorithm definition and constants: [Random123 Philox reference](https://github.com/DEShawResearch/random123/blob/main/include/Random123/philox.h), [oneAPI specification](https://oneapi-spec.uxlfoundation.org/specifications/oneapi/v1.0-rev-3/elements/onemkl/source/domains/rng/mkl-rng-philox4x32x10). The algorithm uses ten 32-bit multiply-high/low, XOR and Weyl-key-increment rounds. The source-pinned reproducer passes two independent published Random123 known-answer vectors for counter=zero/key=zero and counter=(1,0,0,0)/key=zero.

## Exact original-source trial

Original printer source is SHA256 pinned to `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; all 133 preserved packet lines are parsed. The distinct original selected row is index129, ESC-N job `PS-261003-0417`, attempt2 RECOVER ACK at 18:02. Its copied payload `A9A9DC5731A5E2AE879C47215C2559D5` is used **only to authenticate the selected record identity**, not to select a Philox key or output.

Source-derived key inputs are the six individually verified original REC8 components, original K04 XOR mask, and original K08 nonce. For each of these eight original 16-byte objects, derive a 64-bit key in four explicit ways: first 8 bytes, last 8 bytes, XOR of corresponding 8-byte halves, or first 8 bytes of the object's SHA256. Interpret each as both 2×32-bit LE and BE words, giving **64 distinct source-derived keys**.

Eight bounded counter conventions reflect complete visible metadata only: zero-based row index, one-based index, job suffix, whole UTC epoch seconds, UTC minute of day, `(job, attempt, class, destination)`, `(rowindex, job, attempt, 0)`, or `(epoch, job, attempt, class)`. The categorical field codes are frozen explicitly in the SFT. Each native four-word output has four serializers (32-bit little/big endian, native/reversed word order). Thus **64 × 8 × 4 = 2,048** completely specified generator configurations.

Five intact, original printer packets at row indices **0,3,43,84,127** are independent source-positive controls, deliberately excluding selected 0417 ACK2. Every configuration is compared against all five source values, for **10,240 exact complete 16-byte source packet checks**. Every configuration also predicts a selected original coupon from job metadata, reduces with the **unchanged** XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C`, and checks SHA256 against the original full K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0` (**2,048 complete original K04 commitment checks**). No acceptance target influenced key, counter or packet layout selection.

## Actual executed results

```text
Random123 KATs=2 pass; original source records=133 selection_index=129
keys=64 counter_forms=8 serializers=4
five intact source controls=[0, 3, 43, 84, 127]
genuine_source_complete_packet_hits=0
real_selected_commitment_hits=0
synthetic full-fivepacket source config hits=1
synthetic selected component hits=1
NO_MATCH: bounded original Philox4x32-10 key/counter family; K04 remains MISSING
```

The independent synthetic positive chooses one nontrivial key, counter convention and serializer from the **same candidate family**, creates all five exact full packets and one selected component, then rediscovers the entire synthetic control configuration and the synthetic full component exactly once each. The original control and original target yielded zero matches. The original six accepted slots and all historical evidence, route, acceptance, canonical candidate and verifier were preserved untouched.

Reproducer: [source-pinned single-file Python 3 SFT](../agents/agent16/k04_philox_source_keys_sft.py), using the standard library and reading repository-root resources and candidate values.

## Interpretive boundary

This result excludes only the **2,048 stated known-source-derived key/counter/serializer configurations** for this standard counter-based algorithm. It does **not** exclude an unknown independently held 64-bit key, a different counter staging convention, other Philox variants, a non-Philox generator, or the original unobserved physical coupon. Indeed, a separate local exploratory Z3 inversion with a fully unknown key solved a planted 2–3-round Philox control, but returned UNKNOWN under five-second timeouts for 4-, 6-, 8- and 10-round planted controls; **this is a computational limit, not a historical negative result**. No genuine selected K04 bit or K08 final inscription was recovered. Further arbitrary key/counter expansion without firmware provenance is low priority.
