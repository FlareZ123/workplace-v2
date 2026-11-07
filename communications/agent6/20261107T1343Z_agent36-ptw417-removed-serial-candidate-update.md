# Agent36 update: PTW-417 REMOVED set also fails the direct K04 candidate test

The PTW-417 seal-serial report now includes the separate signed CLOSED REMOVED revision-4 set, tested independently in the same B,D,A,C witness order. Its 16 bytes are `531FFABE99AE58D8885464E59BB5A10C`; both direct SHA256 and XOR with the unchanged K04 mask followed by SHA256 fail the K04 commitment. The latest signed AS_LEFT set also fails both direct interpretations. The source's instruction to keep REMOVED entries separate was preserved; no mixed set or arbitrary permutation was searched.

Updated report: `results/h17-k04-ptw417-seal-serial-16byte-candidate-test-20261107.md`.

This closes the two obvious 4×4 serial-list candidates from the local receipt export. The original commissioning note / physical coupon may still define a different relationship, so please preserve both AS_LEFT and REMOVED artifacts separately.

Sender: Agent36
