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
6. As a separate cross-source correction pilot, XOR the selected PS-0417 attempt-2 ACK payload with each of four 16-byte AX-7782 donors: the accepted K07 component, the raw attempt-2 checkpoint chain, the raw attempt-1 checkpoint chain, and the attempt-1/attempt-2 retry-XOR vector. Apply the K04 mask and test the K04 commitment.

## Result

- The independent K07 parser/ordering check **passed**, confirming the AX-7782 latest-checkpoint vector was parsed in the acceptance-defined order and byte representation.
- **32** direct checkpoint/retry coupon candidates were tested.
- **4** bounded PS-0417-ACK2 × AX-7782 cross-source correction candidates were tested.
- AX-7778 is also marked `COMMIT dry_run=false` for the same object ID, although K07's final receipt selects AX-7782. A separate 32-candidate screen tested AX-7778's latest checkpoint vector and per-chunk operations between AX-7778 and AX-7782 (direct, XOR, both directional modular differences, addition, AND, OR; both endiannesses and forward/reverse chunk order).
- **0 of 68** candidates across these three bounded families matched the K04 acceptance commitment.

No checkpoint values, mask bytes, candidate bytes, or candidate digests are reproduced here.

## Interpretation and limits

This rejects only the bounded direct checkpoint/retry, PS-0417 × AX-7782 correction, and AX-7778/AX-7782 checkpoint-vector constructions. It does not test or imply recovery of the 8 MiB AX-7782 object, and it does not rule out a source-authenticated relationship involving the actual chunk contents or native spool media. The checkpoint fields are two-byte audit values, not a substitute for the underlying 1 MiB chunks.

Do not retry this family with more byte permutations or arbitrary arithmetic. K04 still requires either the native PS-0417 coupon/queue-job record or a genuinely different, source-grounded complete-output construction. Keep the existing K04 mask, acceptance commitment, and verifier unchanged.

## Reproduction

Run from the repository root:

```python
import hashlib
import json
import re
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

# Bounded cross-source correction pilot: selected PS-0417 ACK2 XOR one AX-7782 donor.
spool = (root / "evidence/print/spool-reconstruction.log").read_text()
m = re.search(r"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-F]+)", spool)
assert m
ack2 = bytes.fromhex(m.group(1))
attempt1_chain = encode(a, "big", False)
retry_xor = bytes(x ^ y for x, y in zip(attempt1_chain, k07_chain))
cross_donors = {
    "K07 component": k07_component,
    "K07 raw chain": k07_chain,
    "attempt1 raw chain": attempt1_chain,
    "retry XOR": retry_xor,
}
cross_matches = []
for name, donor in cross_donors.items():
    coupon = bytes(x ^ y for x, y in zip(ack2, donor))
    component = bytes(x ^ y for x, y in zip(coupon, mask))
    if hashlib.sha256(component).hexdigest() == target:
        cross_matches.append(name)

print({"K07_parser_check": "PASS", "direct_candidates": tested,
       "direct_matches": matches, "cross_source_candidates": len(cross_donors),
       "cross_source_matches": cross_matches})
```


## Reproduction of the second committed-transfer control

The following adds the AX-7778 comparison to the reproduction above. It is deliberately limited to the latest attempt-2 checkpoint for each chunk of each transfer; it does not promote AX-7778 over the custodian-selected AX-7782 transfer.

```python
other = {(r["seq"], r["attempt"]): int(r["checkpoint"], 16)
         for r in audit if r["kind"] == "CHUNK"
         and r["transfer"] == "AX-7778"
         and r["object"] == "IR-261003-H17"}
assert set(other) == {(seq, attempt) for seq in range(8) for attempt in (1, 2)}
other_latest = [other[(seq, 2)] for seq in range(8)]
selected_latest = b  # AX-7782 attempt 2, already validated against K07

cross_ops = {
    "AX-7778 latest": other_latest,
    "AX-7782 latest": selected_latest,
    "xor": [x ^ y for x, y in zip(other_latest, selected_latest)],
    "AX-7782-minus-AX-7778": [(y - x) & 0xffff for x, y in zip(other_latest, selected_latest)],
    "AX-7778-minus-AX-7782": [(x - y) & 0xffff for x, y in zip(other_latest, selected_latest)],
    "add": [(x + y) & 0xffff for x, y in zip(other_latest, selected_latest)],
    "and": [x & y for x, y in zip(other_latest, selected_latest)],
    "or": [x | y for x, y in zip(other_latest, selected_latest)],
}
cross_tested = 0
cross_hits = []
for name, values in cross_ops.items():
    for endian in ("big", "little"):
        for reverse in (False, True):
            coupon = encode(values, endian, reverse)
            component = bytes(x ^ y for x, y in zip(coupon, mask))
            cross_tested += 1
            if hashlib.sha256(component).hexdigest() == target:
                cross_hits.append((name, endian, reverse))
assert cross_tested == 32
print({"AX7778_AX7782_candidates": cross_tested,
       "AX7778_AX7782_matches": cross_hits})
```

This is not a claim that the checkpoint fields are chunk checksums or that the two committed transfers contain identical bytes. The shared object ID motivates the bounded comparison; it does not establish a coupon derivation rule.

## Adversarial review and stopping rule

Agent50's review is recorded at `communications/agent16/20261126T185301Z_agent50-ax7782-direct-coupon-review.md`.

- The 32 direct AX-7782 layouts partially overlap Agent10's earlier 120-candidate screen: 12 exact candidate/layout combinations overlap. Three of the four PS-0417 ACK2 correction candidates also overlap that prior screen. The 32 AX-7778/AX-7782 cross-transfer candidates are a separate bounded family.
- No supplied source defines the AX-7782 checkpoint fields as a coupon or correction for PS-0417. The selected PS-0417 ACK2 is timestamped `2026-10-03T18:02:00Z`; the AX-7782 commit receipt is `2026-10-03T20:55:10Z`. The later transfer may be a later copy of the bundle, but the shared object identifier and ordering do not establish a byte-level correction dependency.
- **Stop this checkpoint-arithmetic line here.** No further direct, XOR, modular-arithmetic, or cross-transfer checkpoint permutations are justified without a newly authenticated source rule. The next useful K04 evidence is the original PrevERP `posted-items-26.xls`, `reversal-register.htm`, and `SEP26/index.htm`, or a native PS-0417 queue/coupon record with provenance.
