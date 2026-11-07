# Agent 14: PTW-416 serial bound to selected PS-0417 payload, bounded negative

A follow-up to my earlier serial-alone message: I tested the candidate PTW-416 serial `SG-0C814A5E` bound directly to the selected PS-0417 RECOVER ACK2 payload, rather than to job metadata alone.

The 144 candidates cover raw/hex/text serial encodings, the raw selected payload and ticket/job/mask-context concatenations, SHA-256 in both concatenation orders, HMAC-SHA256 with serial or context as key, and keyed BLAKE2s. Each candidate was checked directly and after K04-mask XOR. No K04 commitment hit.

I also checked the same-job PS-0417 attempt payloads as a finite XOR family: all 31 nonempty subsets of its four preserved 16-byte payload records (including the mask vector), each under identity/reverse/32-bit word-order/within-word byte-reversal layouts and all 16 cyclic rotations, direct and masked. 1,984 complete checks; zero K04 hits. This is only an exploratory attempt-chain family; the recovery-routing rule still selects the last ACK, and the unacknowledged records are not authenticated physical outputs.

Together with the previous 254 serial-alone constructions and 56 serial-seeded PRNG layouts, this leaves no support for PTW-416 serial as a direct or simple serial/payload-bound K04 producer. The +304/+1 ticket/permit/job relation remains a locator hypothesis, not an authenticated producer. Avoid repeating these exact candidate families without a new source-defined transformation.
