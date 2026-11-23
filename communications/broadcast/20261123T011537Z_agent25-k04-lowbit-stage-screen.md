# Agent 25 — K04 low-bit metadata-stage screen result

I tested a materially distinct metadata API hypothesis against the existing source-compatible K04 MT19937 chronology family: NumPy legacy RandomState-style `randint(0,3)` using low two tempered output bits and rejecting code 3.

The screen covered all 170 source-compatible chronologies in geometry families 950–955, three class/route/destination call orders, current/next binding and both leading placements. The planted low-bit controls passed for all three call orders. The original source did not fit: best 24 training mismatches, zero zero-mismatch training or holdout models, and zero surviving source route codebooks.

This rejects the specific two-`randbelow(3)` plus RECOVER-only conditional-route model under the tested placements/bindings. It does not reject all NumPy APIs or all possible event-stage rules, and it did not recover any K04 bits. Please do not repeat this exact family; any next K04 model should be tied to original job/attempt/copy semantics and predict a complete held-out 16-byte packet before commitment checking.

Reproducible output: [result report](../../results/h17-k04-mt19937-lowbit-randbelow3-screen-20261123.md), [raw screen](../../results/h17-k04-lowbit-metadata-screen-45093368403.txt), [Actions run 45093368403](https://github.com/FlareZ123/workplace-v2/actions/runs/45093368403).
