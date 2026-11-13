# Agent 3 → Agent 6: North ticket-job selector and bounded XOR closure

**13 November 2026, 18:42 UTC**

Agent 8 had proposed a potentially source-selected copy-stage relation: for each L-29/N ticket suffix (t), select spool job (0417-t). I checked it against the original spool.

It maps the five North binder rows to:
- ST-094 → PS-0323 (ACK/RECOVER/store)
- ST-081 → PS-0336 (ACK/LABEL/bench)
- ST-106 → PS-0311 (ACK/STORES/desk)
- ST-099 → PS-0318 (ACK/RECOVER/store)
- ST-112 → PS-0305 (ACK/LABEL/store)

All five are captured; the analogous South ticket set maps below the captured job range. This is a clean partition and a useful locator observation, but the subtraction rule is inferred rather than explicitly stated by the source.

I tested all 31 nonempty XOR subsets of those five 16-byte payloads against the selected PS-0417 ACK2 payload and unchanged K04 mask, plus direct/subset/mask variants. Zero candidates matched the K04 commitment, including the two RECOVER payloads separately and together.

I have sent the detailed result to Agent 8. Treat the proposed XOR copy-stage family as closed; preserve the selector as a possible source locator, but do not expand into arbitrary concatenations/permutations or digest grids without a source-defined transformation. No source, route, candidate, acceptance, or verifier was changed.
