# K04: AX-7782 retry-checkpoint delta as a direct coupon candidate

**Date:** 2026-11-26  
**Status:** Bounded exploratory candidate family; no accepted K04 candidate.

## Question

AX-7782 is the committed eight-chunk (1 MiB per chunk) transfer of the same incident object. Each chunk has attempt-1 and attempt-2 two-byte checkpoints. Since eight 16-bit per-chunk values form a 16-byte vector, test one source-motivated complete-output hypothesis: the K04 escrow coupon is a direct vector formed from the retry checkpoints (or their per-chunk delta), with the published K04 mask applied exactly as specified.

This is a dimensional/source-structure hypothesis only. No source states that transfer checkpoints are the escrow coupon, and a checkpoint is not chunk content.

## Method

1. Read only AX-7782 `CHUNK` records for sequence numbers 0–7.
2. Require both attempts 1 and 2 for each sequence.
3. Validate parsing/order independently against K07: concatenate the greatest-attempt checkpoint for each sequence as two-byte big-endian values, compute SHA-256, take the first 16 bytes, then verify its SHA-256 against the K07 acceptance commitment.
4. Construct eight 16-bit vectors:
   - attempt 1;
   - attempt 2;
   - attempt-1 XOR attempt-2;
   - attempt-2 minus attempt-1 modulo 65536;
   - attempt-1 minus attempt-2 modulo 65536;
   - attempt-1 plus attempt-2 modulo 65536;
   - attempt-1 AND attempt-2;
   - attempt-1 OR attempt-2.
5. For each vector, test both big- and little-endian checkpoint encoding and forward and reverse chunk order. Concatenate to 16 bytes, XOR with the exact K04 `masked_component`, and compare SHA-256 of the resulting component to `acceptance.slot_sha256.K04`.

## Result

- The independent K07 parser/ordering check **passed**, confirming the AX-7782 latest-checkpoint vector was parsed in the acceptance-defined order and byte representation.
- **32** direct coupon candidates were tested.
- **0** matched the K04 acceptance commitment.

No checkpoint values, mask bytes, candidate bytes, or candidate digests are reproduced here.

## Interpretation and limits

This rejects only the bounded direct constructions listed above. It does not test or imply recovery of the 8 MiB AX-7782 object, and it does not rule out a source-authenticated relationship involving the actual chunk contents or native spool media. The checkpoint fields are two-byte audit values, not a substitute for the underlying 1 MiB chunks.

Do not retry this family with more byte permutations or arbitrary arithmetic. K04 still requires either the native PS-0417 coupon/queue-job record or a genuinely different, source-grounded complete-output construction. Keep the existing K04 mask, acceptance commitment, and verifier unchanged.

## Reproduction

Run from the repository root:

```python
import hashlib
import json
from pathlib import Path

root = Path("resources")
audit = [json.loads(line) for line in
         (root / "evidence/transfers/transfer-audit.jsonl").read_text().splitlines()
         if line.strip()]
routing = json.loads((root / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((root / "acceptance.json").read_text())

rows = [r for r in audit
        if r["kind"] == "CHUNK" and r["transfer"] == "AX-7782"
        and r["object"] == "IR-261003-H17"]
by = {(r["seq"], r["attempt"]): int(r["checkpoint"], 16) for r in rows}
assert set(by) == {(seq, attempt) for seq in range(8) for attempt in (1, 2)}

a = [by[(seq, 1)] for seq in range(8)]
b = [by[(seq, 2)] for seq in range(8)]
mask = bytes.fromhex(routing["K04"]["masked_component"])
target = acceptance["slot_sha256"]["K04"]

def encode(values, endian, reverse):
    values = list(values)
    if reverse:
        values.reverse()
    return b"".join(v.to_bytes(2, endian) for v in values)

# Acceptance-defined K07 check: SHA256(checkpoint-chain)[:16].
k07_chain = encode(b, "big", False)
k07_component = hashlib.sha256(k07_chain).digest()[:16]
assert hashlib.sha256(k07_component).hexdigest() == acceptance["slot_sha256"]["K07"]

ops = {
    "attempt1": a,
    "attempt2": b,
    "xor": [x ^ y for x, y in zip(a, b)],
    "attempt2-minus-attempt1": [(y - x) & 0xffff for x, y in zip(a, b)],
    "attempt1-minus-attempt2": [(x - y) & 0xffff for x, y in zip(a, b)],
    "add": [(x + y) & 0xffff for x, y in zip(a, b)],
    "and": [x & y for x, y in zip(a, b)],
    "or": [x | y for x, y in zip(a, b)],
}
tested = 0
matches = []
for name, values in ops.items():
    for endian in ("big", "little"):
        for reverse in (False, True):
            coupon = encode(values, endian, reverse)
            component = bytes(x ^ y for x, y in zip(coupon, mask))
            tested += 1
            if hashlib.sha256(component).hexdigest() == target:
                matches.append((name, endian, reverse))

print({"K07_parser_check": "PASS", "K04_candidates": tested,
       "K04_commitment_matches": matches})
```
