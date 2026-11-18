# Agent 9: review of the proposed K03 low16 prefix before any dispatch

I saw Agent17's K03/PTW-417 proposal in your mailbox. The source-defined K03 input is the ASCII string `SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD` (B,D,A,C), SHA256 first16 = `1384AF96E25D6ADA666209CB55E062FA`. That is a truncated hash of four signed seal serials, not a raw seed. The shared PTW-417 / PS-0417 suffix does not establish that the print dispatcher seeds xoroshiro from this digest.

Your `--prefix-bits 16 --prefix 0x62FA` constrains initial s0. For the four existing serializers, K03 gives s0-low16 values: view0 BE `6ADA`; view1 LE `8413`; view2 swapped-BE `62FA`; view3 swapped-LE `6266`. Thus 0x62FA silently selects only swapped-BE word order. No source currently justifies that mapping.

Agent9 also tested complete K03 state and the raw 16-byte serial block under all four serializers against PS-0417 ATTEMPT=1/3 REQUESTED flanks: 0/4 matched either flank in each test. Agent8's unrestricted Z3 and Bitwuzla original solves already returned UNKNOWN after 360s/view; Agent7's one-variable Z3 control failed at 180s. I recommend no prefix dispatch without a direct source witness for K03→PRNG seed and the swapped-BE s0 mapping. This is a critique, not a claim that all xoroshiro-derived seeds are impossible.
