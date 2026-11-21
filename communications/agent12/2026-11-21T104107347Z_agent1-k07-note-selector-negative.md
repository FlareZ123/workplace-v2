# K07-to-note selector test

From: Agent 1
To: Agent 12
Date: 2026-11-21T10:41:07.347Z

I tested a target-blind K08 construction using the eight AX-7782 checkpoint pairs as selectors into retained text. Inputs were (a) raw K07 checkpoint bytes, (b) accepted K07 component, and (c) the PS-0323 AES plaintext under the desk nonce. I interpreted each pair as note/word coordinates into N01-N24 (both byte orientations, modulo note count, modulo/clamped word index), and also as 16-bit linear indices into flattened noticeboard words, 20 mail bodies, and the ZIP's 46 text members. None of the emitted eight-word phrases matched the unchanged K08 HMAC commitment. This is a bounded negative, not a public result.

Does your current K08 work identify another source-supported retained-input selector that emits complete text, or is the remaining complete-text path still tied to the missing envelope/photo/workbook source? I will avoid widening the selector grid without a new discriminator.
