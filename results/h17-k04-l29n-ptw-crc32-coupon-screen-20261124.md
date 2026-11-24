# L-29/N four-lane PTW CRC32 coupon screen

**Status:** bounded negative; no K04 candidate recovered.

## Question

Could the ESC-N / PS-261003-0417 coupon be a four-lane vector of references or per-record checksums derived from the four signed as-left PTW receipts associated with the L-29/N return set?

## Source-selected join

- The print-fleet register identifies PS-261003-0417 as ESC-N / L-29/N / FA-17 / H17-POL-17/A3.
- The retained binder order is ST-094, ST-081, ST-106, ST-099, ST-112.
- The separate +304 ticket-to-PTW analysis found four of five North tickets map to four distinct signed PTW bays, with an independent 2/2 L28 holdout. That mapping is a source-supported inference, **not an authenticated foreign key** and does not establish a ticket-to-PS suffix mapping.
- In binder order, the four available signed AS_LEFT receipts are ST-094 → PTW-398 / bay A, ST-106 → PTW-410 / bay B, ST-099 → PTW-403 / bay C, and ST-112 → PTW-416 / bay D. ST-081 → PTW-385 has no signed receipt in this export.
- The recorder format note specifies the zlib/IEEE CRC32 variant. This was used only as a plausible checksum serialization for the coupon; there is no source statement that the printer used CRC32.

## Candidate construction

The source-pinned script constructs 21 complete 16-byte candidates:

- 18 four-lane CRC32 vectors, using nine source-field representations (serial raw bytes, serial ASCII hex, full serial label, raw receipt JSONL record, permit label, permit-number bytes, ticket label, ticket-number bytes, and the corresponding posted A3 supplier row), each in big- and little-endian CRC output order.
- Three direct four-reference vectors: 32-bit permit IDs in big- and little-endian order, and four-digit ASCII permit IDs.

Each vector is tested both as a direct 16-byte component and after XOR with the published K04 mask. Candidate bytes are not printed or committed.

## Result

```text
binder_tickets=ST-094,ST-081,ST-106,ST-099,ST-112
inferred_signed_receipt_permits=PTW-398,PTW-410,PTW-403,PTW-416
inferred_signed_receipt_bays=A,B,C,D
missing_signed_receipt=ST-081->PTW-385
candidate_vectors=21
direct_component_hits=0
masked_coupon_hits=0
candidate_set_sha256=75f7000f680b750b9a247019a83242b9d0fc57c48b899bdec9851e613346dd08
```

This falsifies the bounded four-lane CRC32/permit-ID serialization family. It does **not** falsify the broader possibility of native PrevERP transaction references, the physical coupon, or a native PS-0417 spool object; it does not authenticate the +304 mapping as a foreign key.

## Reproduction

```bash
H17_SOURCE_ROOT=/path/to/extracted/h17-source \
  python agents/agent16/k04_l29n_ptw_crc32_coupon_sft.py
```

The script pins the supplier CSV, print-fleet register, seal receipts, recorder format note, recovery routing, and acceptance files by SHA-256. It prints only source-selection metadata, hit counts, and a candidate-set digest.

## Related evidence

- `results/h17-k04-fa17-ticket-ptw-ps-offset-join-20261120.md` — the +304 join, its L28 holdout, and the explicit limitation that it is not a ticket-to-PS foreign key.
- `results/h17-k04-l29n-set-vs-st112-ticket-boundary-20261121.md` — raw four-serial candidate boundary for the North return set.
