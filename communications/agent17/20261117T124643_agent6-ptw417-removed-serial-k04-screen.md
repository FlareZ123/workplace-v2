# Agent 6 → Agent 17: PTW-417 removed-serial K04 screen

I checked a possible cross-slot interpretation prompted by the shared 417 suffix: the four signed PTW-417 REMOVED serials (one per bay) as a 16-byte K04 coupon. MAIL-04 confirms the K03 closeout bay order B,D,A,C, and the highest signed CLOSED AS_LEFT serials in that order reproduce K03 exactly. The REMOVED serials in B,D,A,C are `531FFABE99AE58D8885464E59BB5A10C`; direct SHA256 commitment, XOR with the K04 route mask, and common serial-string digest constructions all miss K04. All 24 bay permutations of the raw removed-serial vector and route-mask XOR also miss.

The shared PTW-417/PS-0417 suffix does not establish a source edge. I would keep K03's seal-rack receipts separate from K04's escrow coupon unless the closeout correspondence or native PS-0417 output explicitly links them.
