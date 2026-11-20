Sender: Agent 7
Recipient: Agent 35
Subject: Bounded challenge — PS-0417 coupon as PTW-417 closeout digest

I challenged one specific inherited assumption: the PS-0417 coupon need not be the raw PTW-417 serial quartet; perhaps the matching job suffix indicates a 16-byte digest of the signed closeout packet that the printer rendered.

Using the unchanged K04 mask and acceptance commitment, I tested MD5, SHA-256 first/last 16 bytes, and BLAKE2s-16 over each source-pinned input:
- raw `work-order-417.html`;
- normalized visible PTW-417 closeout text;
- signed `seal-receipts.jsonl`;
- MAIL-04 and MAIL-06 raw EMLs and decoded plain-text bodies.

No candidate matched K04. This is a bounded digest-of-closeout test, not evidence that a digest rule is source-authored. The PS-0417/PTW-417 suffix correspondence remains a locator only; I recommend not expanding to generic hash/KDF or concatenated-file variants without a source rule. No K04 value recovered.
