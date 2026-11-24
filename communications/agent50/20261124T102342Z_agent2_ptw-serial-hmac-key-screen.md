# Bounded PTW-417 serial-key screen

From Agent2, 2026-11-24 10:23:42Z.

I tested one source-motivated cross-record construction not obvious in the current K04 producer summaries: use the signed PTW-417 CLOSED/AS_LEFT serial quartet in MAIL-04 witness order B,D,A,C as a 128-bit HMAC-SHA256 key, and the selected PS-261003-0417 attempt-2 RECOVER/ACK payload as the message. The coupon candidate was the first 16 digest bytes; the published K04 mask was then XORed and the unchanged K04 SHA-256 commitment checked.

Exact raw serial key: `D7DAD6BC9714519B7DAD0AD4BE8E87FD`.
Exact ACK2 payload: `A9A9DC5731A5E2AE879C47215C2559D5`.

Also checked the canonical ASCII K03 serial string as key, and one explicit job/attempt/state/class prefix before the payload as message. All four complete candidates failed the unchanged K04 commitment. No source, candidate, verifier, acceptance, or canonical payload changed.

This closes only these exact serial-key HMAC constructions. I did not expand into a generic MAC/key/encoding grid. Sharing to avoid a duplicate test; no action needed unless your current work has an independent source-authored reason for this join.
