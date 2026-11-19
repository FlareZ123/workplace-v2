# K04 AX-7782 per-sequence retry-delta coupon: rejected

**Agent 25 | 19 November 2026 | source-pinned single-candidate test**

## Question and frozen construction

The committed AX-7782 transfer contains two 2-byte checkpoint attempts for each of eight 1 MiB chunks of object `IR-261003-H17`. I tested one finite construction: treat the per-sequence retry difference as a 16-byte coupon.

The operation was fixed as follows:

1. Select AX-7782, whose source ledger has one `COMMIT`, `dry_run=false`, `chunks=8`, and object `IR-261003-H17`.
2. For each sequence `0..7`, compute the bytewise XOR of its attempt-1 and attempt-2 2-byte checkpoints.
3. Concatenate those eight 2-byte deltas in ascending sequence order.
4. Apply the K04 rule exactly: XOR this 16-byte coupon candidate with `masked_component`, then SHA-256 and compare with the unchanged K04 commitment.

This is a source-motivated hypothesis, not a rule authenticated by the K04 routing record. No byte-order, sequence-order, transfer-ID, or alternative-delta variants were added.

## Exact result

| Seq | Attempt 1 | Attempt 2 | XOR delta |
|---:|---|---|---|
| 0 | `6224` | `8947` | `EB63` |
| 1 | `4DFB` | `CEDC` | `8327` |
| 2 | `F3B8` | `B9CC` | `4A74` |
| 3 | `CA3D` | `73BA` | `B987` |
| 4 | `1888` | `B7E8` | `AF60` |
| 5 | `F22A` | `7BE6` | `89CC` |
| 6 | `3DB0` | `3302` | `0EB2` |
| 7 | `8769` | `C5C9` | `42A0` |

- Coupon candidate: `EB6383274A74B987AF6089CC0EB242A0`
- K04 mask: `8556C8CB6140A7F9A5123AC7571BEE1C`
- Masked component candidate: `6E354BEC2B341E7E0A72B30B59A9ACBC`
- Candidate SHA-256: `006f8bd6a6e8ccad3920baa9a9c7cfef04a4ab03c6b3c4f47c6ff2d9d7470b79`
- Required K04 SHA-256: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`
- **Outcome: no match.**

## Positive control: accepted K07 chain

The same parsed AX-7782 rows, using the documented greatest-attempt-per-sequence rule, produce:

- Selected checkpoint input: `8947CEDCB9CC73BAB7E87BE63302C5C9`
- K07 component (first 16 bytes of SHA-256): `93495F5E425AB8E592123DABAEB68545`
- SHA-256 of that component: `b8884f0ba97f1e3432ddc0e7f14f7ac516ff24430e7c42321af16aad59302680`
- Required K07 SHA-256: `b8884f0ba97f1e3432ddc0e7f14f7ac516ff24430e7c42321af16aad59302680`
- **Outcome: exact match.**

The positive control verifies the transfer parse, sequence ordering, attempt selection, byte concatenation and SHA-256 implementation. The K04 failure is therefore not caused by a transfer-selection or serialization error.

## Evidence pins and reproduction

The reproducer pins these SHA-256 values:

- `evidence/transfers/transfer-audit.jsonl`: `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`
- `evidence/transfers/queue-note.txt`: `2040af92096bd270352a7c5e4a587ae3a0a26485c2c2a10240ce8504465c788f`
- `evidence/recovery-routing.json`: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json`: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

Run from the repository root:

```bash
python agents/agent25/k04_ax7782_retry_delta_coupon_sft.py
```

The existing Agent48 direct transfer-chain screen tests raw checkpoint choices and sequence/byte views; this test is distinct because it constructs one XOR-delta word per sequence. The result is nevertheless negative. Do not expand this into a retry-delta variant sweep or treat it as evidence for the missing coupon.

**Decision:** close this single retry-delta candidate. K04 remains MISSING; K08 remains MISSING; the six accepted slots and original verifier are unchanged. A successful recovery still requires an independently justified complete 16-byte coupon construction or an authenticated native printer object.
