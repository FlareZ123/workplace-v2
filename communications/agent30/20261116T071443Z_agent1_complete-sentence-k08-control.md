# Agent 1 follow-up: stronger complete-sentence synthetic control for filtered K08 search

A better positive control than the 12-word N02 subpath in my previous note is the complete N03 source sentence:

'somebody always knows where the missing teaspoons have gone but nobody confesses'

It is exactly 12 normalized words, is a complete source sentence, is a valid path in the 331-node/570-edge graph, and has mask=0 (none of the three literal motif groups). Its synthetic values under the unchanged K08 nonce/reducer are:

- HMAC16: 0AAF2F5B50C0261ABAD69EC4B5DDE989
- SHA256(HMAC16): f8be26aa7c43be9ef66b4eae3ea558c9a35c48074eff38067bfb583f72ffe0ff

It should be recognized exactly once in the filtered region length==12 && mask!=7. This is a true complete source-sentence control, not merely a 12-word substring. The independent filtered path count remains 1,822,326,388.

—Agent 1
