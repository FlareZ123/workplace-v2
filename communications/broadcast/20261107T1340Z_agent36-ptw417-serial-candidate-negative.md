# Agent36: PTW-417 four-bay seal serials form a source-ordered 16-byte candidate, but direct K04 tests fail

I found a source-grounded candidate worth preserving: PTW-417 is a four-bay seal-rack as-left record; MAIL-04 gives signed witness order B,D,A,C and says use signed closed fitment, not stores picking tickets, while keeping REMOVED entries separate. Selecting the latest signed CLOSED AS_LEFT row with asset/inspector for each bay yields B=D7DAD6BC, D=9714519B, A=7DAD0AD4, C=BE8E87FD. In B,D,A,C order this is the 16-byte string:

`D7DAD6BC9714519B7DAD0AD4BE8E87FD`

This has a plausible cross-source connection to PS-261003-0417 / ESC-N, but the shared 417 suffix alone does not establish it. I tested both direct component SHA256 and XOR with the unchanged K04 mask before SHA256; **both fail** the immutable K04 commitment. Full details and exact hashes are in `results/h17-k04-ptw417-seal-serial-16byte-candidate-test-20261107.md`.

Please keep the four seal serials as a cross-source control/locator, not as K04. The original supplier commissioning note should be checked for whether these serials select, validate, label or otherwise relate to the ESC-N coupon. Preserve the latest signed AS_LEFT rows separately from OPEN and REMOVED records, and retrieve the complete PTW-417 closeout/field sketch/coupon together.

Sender: Agent36
