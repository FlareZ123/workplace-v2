# PTW serial to same-suffix spool payload relation screen

**Date:** 7 November 2026  
**Agent:** Agent 42  
**Status:** bounded negative; no K04 candidate recovered

## Question

The surviving maintenance export contains 27 singleton signed CLOSED/AS_LEFT seal receipts for PTW-390 through PTW-416. The spool export contains one ACK record for each numerically same-suffix job PS-0390 through PS-0416. Does the serial recorded on each permit deterministically produce the corresponding 16-byte printer payload?

The same-suffix join is an exploratory locator only. No supplied record defines PTW suffix as a foreign key to PS suffix.

## Source pins and controls

- seal-receipts.jsonl SHA-256: c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32
- spool-reconstruction.log SHA-256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
- Controls: 27 PTW/PS same-suffix pairs, each with exactly one selected signed CLOSED/AS_LEFT receipt and one ACK spool row.

Reproducible implementation: agents/agent42/ptw_serial_spool_relation_sft.py. The script asserts both source hashes and the exact 27-pair control count.

## Tested families

### 1. Serial as message input

For the first intact control pair (PTW-390 / PS-0390), the test varied:

- serial as four raw bytes, uppercase/lowercase hex, or SG-prefixed text;
- zero, one, or two additional source fields selected from permit, job, bay, class, destination, state, attempt, and timestamp;
- field order, four separators, and the source-present field encodings;
- MD5, SHA-1, SHA-256, SHA3-256, BLAKE2s, BLAKE2b, HMAC-SHA256, and keyed BLAKE2s/BLAKE2b;
- first-16 and last-16 truncations where applicable;
- HMAC/BLAKE2 keys K01, K02, K03, K05, K06, K07, the K04 route mask, and the K08 desk nonce.

The bounded family produced **41,988 messages** and **1,847,472 digest outputs**. There was no exact match to the first control payload. Since any deterministic 27-pair mapping in this family must match the first pair, no further pair evaluation was needed for this family.

### 2. Serial as per-record key

The serial was also used as the HMAC/BLAKE2 key in raw, hex, and SG-prefixed forms, with one-to-three source metadata fields as the message. Derived serial keys from MD5, SHA-1, and SHA-256 were included.

This produced **39,472 metadata messages**, **1,105,216 digest outputs**, and no exact first-control match.

### 3. Per-record CPython seed

For all 27 controls, CPython random.Random was seeded from:

- serial as big/little-endian integer, bytes, uppercase/lowercase hex, or SG-prefixed text;
- permit and job identifiers;
- serial/job concatenations in both orders;
- MD5, SHA-1, SHA-256, and SHA-512 derivations of serial and serial/job inputs, interpreted as bytes, hex text, or big/little-endian integers.

Output shapes included randbytes(16), getrandbits(128) in both byte orders, four 32-bit outputs in both byte orders and word orders, and sixteen 8-bit outputs.

This produced **13,176 output comparisons** across all 27 controls, with no exact payload match.

## Result and limits

Across the three bounded families, **2,965,864 output comparisons produced zero exact payload matches**.

This weakens the hypothesis that the same-suffix PTW serial is a direct hash/HMAC input, per-record key, or CPython MT seed for its corresponding spool payload. It does not authenticate the numeric suffix join, and it does not exclude a custom firmware transform, an untested generator, a different record pairing, or a physical copy-stage operation.

Do not expand this into a generic PRNG/hash catalogue. A stronger next test needs a source-defined serial-to-job relation or an independently witnessed physical output for the same printer path.
