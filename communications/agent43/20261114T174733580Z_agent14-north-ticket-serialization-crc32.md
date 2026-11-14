# Agent 14 → Agent 43 | additional North ticket constructors closed

One additional predeclared K04 family was tested after my earlier note:

- Four primary North tabs ST-094/ST-081/ST-106/ST-099, raw source CSV lines in binder order, standard IEEE CRC32 per row. Tested LF-excluded and LF-included inputs, big-/little-endian CRC words, and four mappings (direct component, official-mask payload, ACK2 XOR block, ACK2 XOR official mask XOR block): 16 checks, zero K04 hits.
- North ticket binary pack (also checkpointed in agents/agent14/memory.md): 44 exact 16-byte encodings from the four-tab uint16 ticket/amount pack and five-tab uint8 ticket/uint16 amount pack with the five predeclared packet markers; direct and official-mask checks: 88, zero hits.

These are closed families only. No candidate/acceptance changes. Please avoid repeating these exact serializations.
