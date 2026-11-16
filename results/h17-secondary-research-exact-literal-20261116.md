# H-17 exact recovery candidate search across prior research artifacts (16 November 2026)

**Agent 39. No seventh REC8/1 component recovered.**

This experiment asks a different question from previous printer-producer and K08 phrase-grammar screens: whether a previous agent had already **written a complete correct K04 raw component / physical coupon, or exact K08 final caption**, without recognizing its acceptance.

A standard-library [read-only SFT](../agents/agent39/h17_prior_literal_miner_sft.py) scanned the current `agents/`, `results/`, `work/` and `communications/` text artifacts. It deliberately excluded `private/` and the 46 original resources, which have their own earlier literal scans. It extracts standalone 16-byte hexadecimal and Base64 tokens, both halves of standalone 32-byte hex digests, consecutive C-style hex byte arrays, and complete quoted or short plain-text lines. Each candidate is checked in the appropriate complete original reduction: K04 literal directly or as XOR-masked copied coupon, with forward/reverse byte orientation; K08 exact normalized phrase HMAC16 followed by SHA256. Original K01 SHA and authentic known N02 HMAC are positive implementation controls.

**Executed remotely** from clean repository checkout in [GitHub Actions run 43898474716](https://github.com/FlareZ123/workplace-v2/actions/runs/43898474716), conclusion SUCCESS:

- **4,782** readable research text artifacts / **254,901** lines examined.
- **1,605** distinct complete 16-byte candidate values and **28,123** distinct normalized whole-text candidate phrases.
- **Zero** matches for either original target commitment. Original K01 and N02 independent controls PASS.

This excludes only **literal complete values in the declared secondary artifact representations**. It cannot find a source that is absent from the repository, a value generated only at runtime, strings split across distant lines, altered or translated originals, or the physical printed coupon or final margin. It gives zero extra authentic K04 bits and zero final K08 words, and **must not be expanded into another unselected transform catalogue**.

**Recovery decision:** K01/K02/K03/K05/K06/K07 PASS; K04/K08 unresolved; combined REC8/1 INCOMPLETE. The supplied archive, target commitments, official verifier and canonical partial candidate remain unchanged.
