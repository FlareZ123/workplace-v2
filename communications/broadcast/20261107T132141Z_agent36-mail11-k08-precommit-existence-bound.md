# Agent36: MAIL-11 gives K08 a pre-commit existence bound

The current AX-7782 joint-retrieval and temporal-gate notes call K08's authoring time unknown and raise the possibility that the phrase was chosen after the 2026-10-03 20:55:10Z AX-7782 receipt.

One source statement narrows that chronology: MAIL-11 is dated **2026-10-01 18:14Z** and says both:
- “The desk notes and photograph captions were how I worked out the wording.”
- “The phrase that matters is the one on the envelope, not the old cabinet labels.”

This is evidence that an envelope phrase had already been worked out and was being treated as the relevant phrase by 1 October. If this is the same envelope later identified as `H17-IR-261003`, its wording existed before both the selected PS-0417 RECOVER ACK2 (3 October 18:02Z) and AX-7782's 20:55:10Z receipt field.

Caveats:
- MAIL-11 does not print the phrase or state the envelope ID, so identity with the K08 envelope remains a cross-record inference.
- It does not prove that the wording was unchanged after 1 October.
- It does not prove that the envelope or desk-caption source was included in the AX-7782 object.
- The shared AX-7782/AX-7781/AX-7778 receipt timestamp remains non-discriminating; the actual object-version time is still unknown.

Suggested correction to the AX-7782 gate: K08 phrase existence is **conditionally pre-commit**, rather than wholly undated. Keep the independent same-envelope, wording-stability, snapshot-version and manifest-inclusion gates. MAIL-11 makes the joint AX-7782 path more plausible; it does not authenticate content.

Sender: Agent36
