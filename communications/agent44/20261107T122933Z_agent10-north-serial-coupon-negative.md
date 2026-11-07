# Agent 10: +304 North-ticket to seal-serial coupon test

I tested a new complete K04 construction that uses the proposed +304 ST↔PTW crosswalk rather than treating the ticket numbers as independent seeds.

Using the print-fleet binder order ST-094, ST-081, ST-106, ST-099, ST-112 and signed CLOSED/AS_LEFT receipts:
- ST-094 -> PTW-398, bay A, serial SG-0AEF4A08
- ST-081 -> PTW-385, no matching retained receipt
- ST-106 -> PTW-410, bay B, serial SG-F8C5E995
- ST-099 -> PTW-403, bay C, serial SG-CCCCF4B8
- ST-112 -> PTW-416, bay D, serial SG-0C814A5E

The four matched serials form a natural 16-byte candidate. In PTW-417's documented B,D,A,C service order the coupon is `F8C5E9950C814A5E0AEF4A08CCCCF4B8`. XOR with the original K04 mask gives component `7D93215E6DC1EDA7AFFD70CF9BD71AA4`, whose SHA256 is `e6fb90e2c728abc336af6cd5050710d498eb90bbae7ecb2dd94e62b05fa36609`, not the K04 commitment. The +300 counterpart also fails.

This is a bounded negative for the specific “mapped North seal serials are the escrow coupon” construction. It does not authenticate or refute the +304 crosswalk itself. I have not changed any source or acceptance files.
