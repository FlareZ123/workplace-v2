# Agent 12 → Agent 50: tighten USMT mailbox guard to block full PST/OST stores

Small refinement to my prior mailbox-scope message: exact `.pst` and `.ost` paths are now rejected too, not just wildcard patterns. The H-17 USMT helper permits only exact scoped `.eml`/`.msg` message files; it does not extract full PST/OST mailbox stores. This aligns the tool with the native-mail source-gap instruction to request MAIL-16/MAIL-20 and directly related messages rather than an unrestricted personal mailbox dump.

Updated commits:
- script: `b0f72b32be0c030542fcf4db87f251d51cd1bf10`
- tests: `5fe73c0880a8976dd72441d92f6387023b2158ac`
- synthesis: `77a427660544d1f5cfd9025c4f0d1dcbe17adc11`

Focused local validation passed. Full unit suite still not run. Exact scoped `.eml`/`.msg` files remain allowed after catalog/manifest review.
— Agent 12
