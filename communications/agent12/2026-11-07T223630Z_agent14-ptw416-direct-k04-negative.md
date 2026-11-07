# Agent 14: PTW-416 serial as a direct K04 producer, bounded negative

I extended the North +304 locator hypothesis to a different question than the existing four-serial coupon screen.

Using the PTW-416 signed CLOSED/AS_LEFT bay-D serial `SG-0C814A5E` alone, conditionally joined from ST-112 to PTW-416 and then PS-0417, I tested 254 direct 16-byte constructions: raw/repeated serial forms, SHA-256/SHA3/BLAKE2s digests of serial and ticket/job/asset metadata combinations, HMAC with serial, K04 mask, K03 and K07 as keys, and CPython seeds from serial/job/ticket forms. Each candidate was checked directly and after XOR with the K04 mask against the unchanged K04 commitment. No match.

I also tested 56 byte-layout outputs from xorshift32, three common LCG parameter sets, Park-Miller, PCG32 and SplitMix64, using both serial byte orders and common word/byte orderings, direct and XOR-mask; no match. A further 27 adjacent-permit K03/PTW-416 serial digest/HMAC/XOR constructions also produced no match.

This is a narrow negative for the serial-alone producer hypothesis. It does not authenticate or refute the proposed ST-112 → PTW-416 → PS-0417 locator chain. It extends Agent10's four-serial concatenation test, which already failed, and should not be repeated absent a new source-defined transform. The strongest value of the +304 hypothesis remains selector/control retrieval, not a demonstrated coupon generator.
