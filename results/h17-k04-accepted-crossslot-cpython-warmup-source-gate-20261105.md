# K04: cross-slot authenticated binary seeds, long CPython warmup, intact-packet source gate

**Agent20, 5 November 2026, 17:00 UTC.** This is a new, bounded original-source **complete printer producer** search. **No original K04 selected coupon bit or K08 caption word was recovered**. The unchanged original six REC8 components remain PASS; K04/K08 and combined REC8 acceptance remain unresolved.

## Recoverability hypothesis

The 132 intact ordinary/late printer packets exhibit native MT19937 structural relationships under previous source-only analyses. A possible *different seed route* is an archive-derived 128- or 256-bit binary key initializing a single CPython `random.Random` whole-word generator, with substantial unobserved output consumption before the preserved first spool packet. A **complete 16-byte intact source packet** is a strong gate: a true candidate producer would reproduce all four consecutive 32-bit output words in an intact record before any selected 18:02 physical K04 coupon can be predicted.

Unlike prior searches for CPython integer-second clock seeds, free-form text labels, hypothetical first-cycle initialized-register arrays or selected-only seed32 hashes, this test uses exact original already-accepted REC8 binary components as input seeds, including Python's documented *bytes-seed* SHA512 extension, and permits a long contiguous warmup of **0 through 131071 32-bit draws**. No first-cycle p951 MT chronology or disputed copied selected packet is assumed.

**Original input set (ten 16-byte source carriers):** the independently verified six slots K01/K02/K03/K05/K06/K07; original K04 route mask; original K08 desk nonce; the eight-u16 selected raw **K02 telemetry prehash** (before its accepted SHA256); and eight 2-byte selected raw **K07 transfer prehash** (before SHA256). Input-source SHA256 pins verify the original acceptance, route, spool, telemetry and AX transfer file. The two prehashes are independently regenerated from original high-revision/GOOD/HOLD and committed-transfer selection rules rather than copied from a prior test.

For each carrier, test its **raw 16 bytes**, `SHA256(raw)` as 32 bytes, and `SHA256(raw)[:16]`, each under four Python `random.Random` constructors:
1. `Random(binary_bytes)`;
2. `Random(int.from_bytes(binary_bytes, 'big'))`;
3. `Random(int.from_bytes(binary_bytes, 'little'))`;
4. `Random(binary_bytes.hex())` as a UTF-8 text seed.

Those are **120 exact seed-constructor assignments**, with 131072 first-packet offsets per seed and four full 16-byte source packet presentations: word endian little/big and forward/reversed four-word order. Every candidate is a complete deterministic source packet, rather than a partial hash-prefix score.

## Original-source result

Read-only local original 46-member ZIP execution against first source printer packet (original row0, 07:00Z): `FBBBC54356483F5864BB3F06794518A5`. Source spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. **Selected disputed row129 is never decoded or compared**, and original K04 SHA256 target is not loaded. The program gates complete checks on a necessary equality between a packet's first or final 32-bit word under either byte order, allowing both packet reversal modes.

- **15,728,640** seed/start opportunities.
- **62,914,560** complete serialized packet presentations.
- **Zero** original 32-bit first/last-word gate hits.
- Consequently **zero** complete original intact packet matches.

Two genuine CPython-seeded full-packet synthetic controls are recovered at their exact planted offsets and serializations: `Random(K01_bytes)` at offset4099 under big-endian reversed fourword order, and `Random(int.from_bytes(K01_bytes,'little'))` at offset7011 under little-endian forward order. They test real Python's native MT generator and the exact packet comparator, including the tricky reversed-word first/last gate. All original source SHA pins and six individual accepted-component hashes passed. No artificial acceptance commitment or original K04 target candidate was used.

**Reproducer:** [Agent20 read-only source-pinned SFT](../agents/agent20/k04_crossslot_cpython_warmup_sft.py), Python standard library. The committed file matches the completed local original-archive implementation and was read back successfully from GitHub.

## Interpretation

Under this explicitly enumerated key-to-CPython-stream producer family, no authenticated selected coupon can be reconstructed because none of the 120 origins/seeds reproduces even an independently intact first spool packet. This remains a **conditional negative**, not evidence that the actual printer used CPython or that accepted archive components seeded its RNG. An unrelated seed, another initializer, a longer warmup, a distinct serializer, staged output omissions inside each 16-byte packet, or different generator could lie outside the family. The original source supplies no generator seed or startup phase directly.

The new approach evaluates an independently authenticated complete source object before pursuing K04 and tests a producer class with potential full-coupon prediction. It does **not** authenticate the lost physical coupon, recover K08 literal words, or change the canonical candidate or acceptance.
