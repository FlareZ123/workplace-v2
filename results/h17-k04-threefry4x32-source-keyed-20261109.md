# K04: a source-keyed Threefry4x32 whole-coupon issuer test (9 November 2026)

**Agent 10 | original unmodified H-17 export | 768 complete candidate coupons, zero original K04 acceptance matches.** The six accepted components remain unchanged. K04/K08 are unresolved; combined REC8/1 remains INCOMPLETE.

## Why this distinct producer was evaluated

The actual 3 October printer export retains 133 opaque 16-byte records, including two independent late RECOVER acknowledgements, PS-261003-0420 attempt2 and PS-261003-0448 attempt1. The selected PS-261003-0417 attempt2 ACK physical coupon cannot be authenticated from its copied bytes. The previously source-screened Philox4x32 and ChaCha producers do not automatically exclude **Threefry4x32-20**, a different standardized counter-based word generator with ARX operations and a full 128-bit key. A source-keyed fixed counter function could directly produce a complete selected coupon without repairing disputed copy bytes.

This is a **speculative source-keyed issuer**, not an attested manufacturer algorithm. It has neither a historical printer implementation witness nor a reason to privilege any tested event-counter layout.

## Source, exact model, and authentic holdouts

Read-only original-file pins:

- printer reconstruction SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`;
- original K04 route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`;
- unchanged full K04 component commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The eight fully source-preserved 16-byte potential keys are the **six individually SHA256-accepted components** K01,K02,K03,K05,K06,K07 and the **two original route fields** K04.masked_component and K08.desk_nonce. All six accepted fields are checked against original slot commitments before use. For each source key, test both native endian word interpretations, twelve frozen event-counter layouts using the original job/attempt/UTC/class/destination/index, two output word endian modes, and natural/reversed output word order. Each assignment creates exactly one complete selected 16-byte coupon through Random123 Threefry4x32-20, XORs the unchanged original route mask, and compares the **full 256-bit K04 commitment**.

The same issuer assignment is independently applied to the two nonselected intact late RECOVER ACK records. Its *complete source-packet matches* are counted before any selected K04 acceptance inference. The selected 0417 ACK2 copied payload never enters key/counter fitting or candidate generation.

## Executed result

The original ZIP was extracted locally, and the exact stand-alone Python test [`agents/agent10/k04_threefry4x32_source_keys_sft.py`](../agents/agent10/k04_threefry4x32_source_keys_sft.py) was run against its unchanged data:

```json
{
  "model": "Random123 Threefry4x32-20 keyed by eight authentic source fields",
  "source_packets": 133,
  "heldout_other_acked": 2,
  "source_holdout_complete_hits": 0,
  "target_complete_sha_checks": 768,
  "original_K04_hits": [],
  "reference_kats": 3
}
```

The implementation passes all three official Random123 Threefry4x32-20 known-answer vectors, including zero, all-one and digits-of-pi key/counter inputs. The original extraction includes exactly one selected 0417 ACK2 and two nonselected late RECOVER ACK controls. Thus, **0/1,536 complete control-packet comparisons** and **0/768 full original K04 commitments** match the tested issuer. The accepted K01/K02/K03/K05/K06/K07 hashes are independently asserted by the test.

Reference algorithm and official vector source: [DEShawResearch/random123 Threefry header](https://github.com/DEShawResearch/random123/blob/main/include/Random123/threefry.h), [official Random123 vectors](https://github.com/DEShawResearch/random123/blob/main/tests/kat_vectors).

## Interpretation and allocation

This directly excludes the specified **eight-key/twelve-counter/four-output-serialization Threefry** candidate family and shows no independent historical source support for it. It does **not** exclude other source keys, a real printer-specific counter/nonce, another engine, a damaged-copy channel, or a physical coupon absent from the export. No genuine K04 bit or K08 final word was recovered.

The independent late-packet failure makes arbitrary enlargement of key or nonce dictionaries low priority. A true source-based counter/issuer attribution would be required to justify another Threefry expansion. The canonical candidate, original route, acceptance file and verifier were left unchanged.
