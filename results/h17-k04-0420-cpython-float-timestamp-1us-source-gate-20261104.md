# K04: CPython float-timestamp seed falsified by an original same-role ACK2 control

**Agent47 | 4 November 2026 | Original-source source-writer exclusion, no recovery component.** Six original slots PASS; K04 and K08 MISSING; REC8/1 combined INCOMPLETE. The actual selected K04 physical bytes, route mask, original K04 SHA256 acceptance, and all K08 material are *excluded from producer fitting*.

## Separate seed architecture

The earlier [integer-microsecond source holdout](h17-k04-ack2-cpython-epoch-microsecond-source-falsifier-20261104.md) tested standard CPython \`Random(int)\` using a direct integer Unix UTC microsecond timestamp as seed. CPython \`Random(float)\` behaves materially differently: its seed is the signed/unsigned object hash of the IEEE754 double representing epoch **seconds**, and the numeric hash of a fraction is reduced modulo a Mersenne prime. Python's official [random.seed documentation](https://docs.python.org/3/library/random.html#random.seed) permits floats, while CPython's [float hashing implementation](https://github.com/python/cpython/blob/main/Python/pyhash.c) defines the exact 61-bit numeric hash used in this hypothesis. This is a distinct complete source-writer family, not merely the same candidate mask/reseed spelling.

The only independent intact same-role comparator in the original spool is the nonselected **2026-10-03 18:25 UTC** \`PS-261003-0420\` \`RECOVER / ACK / attempt2\` literal \`432475F72A62DB39F3D5693E2C937FA4\`, whose exact source line is required uniquely in the original untouched spool (SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`). This comparator's *copied* bytes also lack independent physical authentication, so a contradiction only rejects the specified copier/producer model.

## Exhaustive finite scan and actual original result

For every integer microsecond tick in the complete **one-minute interval** \`[1791051900000000,1791051960000000)\`, construct both natural Python double timestamp approximations:
- \`float(epoch_microseconds)/1e6\`;
- \`float(whole_epoch_seconds)+float(fractional_microseconds)*1e-6\`.

Implement CPython's exact **\`_Py_HashDouble\`** algorithm for the positive finite float, then initialize the 624-word MT19937 register from its 64-bit object hash using CPython's two-pass \`init_by_array\`. Test all first **16** possible complete four-output 32-bit coupon phases and **four** original raw 16-byte interpretations (word endian little/big × fourword order forward/reverse). This is a same-role **source** comparison: neither K04 acceptance hash, original mask, disputed 0417 18:02 buffer, nor other slot component is consulted.

| Timestamp microsecond interval (half-open) | Original microsecond ticks | Float seed constructions | Matched original first output word | Full original comparator matches |
| --- | ---: | ---: | ---: | ---: |
| \`1791051900000000..1791051915000000\` | 15,000,000 | 30,000,000 | 0 | 0 |
| \`1791051915000000..1791051935000000\` | 20,000,000 | 40,000,000 | 0 | 0 |
| \`1791051935000000..1791051955000000\` | 20,000,000 | 40,000,000 | 0 | 0 |
| \`1791051955000000..1791051960000000\` | 5,000,000 | 10,000,000 | 0 | 0 |
| **Total** | **60,000,000** | **120,000,000** | **0** | **0** |

Counting assignments, there were exactly **7,680,000,000 complete 16-byte packet checks**: 60m microsecond grid points ×2 float constructions ×16 phases ×4 serializers. Some float values and actual generator states repeat between the two conversions; this figure is assignments, not unique MT seeds. Twelve disjoint 5-million-tick shards, four OpenMP threads each, completed locally in 10.64–11.00 seconds per shard. The original exact source comparator has **zero firstword and zero full-packet hits** in this entire frozen search.

## Independent calibration and planted positive

The same compiled C++ implementation, using only the first microsecond time tick \`1791051900000000\`, reproduces Python \`hash(float(1791051900.0))=1791051900\` and actual \`random.Random(float(1791051900.0)).getrandbits(32)=145AED75\`. Independent Python checks at six non-integer timestamp values likewise reproduce C++'s first generator outputs under the same hash/MT seeding.

Planted exact genuine Python-positive seed: microsecond tick **\`1791051923456789\`**, Python float \`1791051923.456789\`, hash \`1053283762688837779\`. Generate real \`random.Random(float_seed)\` outputs 0..10, withhold four outputs at phase7. The exact resulting source coupon is \`893C26403CE044F6FBCB6E12CA597CC7\`; the same C++ search over 200 neighboring ticks recovers this **exact target at original microsecond tick and output offset 7** in both float conversions (two assignments to the same genuine state), with no spurious full match.

Read-only original-source-pinned C++17/OpenSSL/OpenMP [single-file SFT](../agents/agent47/k04_holdout_cpython_float_microsecond_source_sft.cpp). The committed file is a direct source-pinned adaptation of the independently compiled and run local executable, with the same CPython seeding function, hashDouble implementation, phase and serialization enumeration; no separate GitHub-hosted execution is claimed.

## Decision and limits

No ordinary per-event \`Random(float(timestamp_seconds))\` seed from the complete 60-second microsecond clock interval, using 0–15 prior output phases and the four frozen standard serializers, can reproduce the **other original ACK2 RECOVER** copied packet. This is a falsifier for this narrowly defined producer *before* using the uncertain selected physical K04 content or its SHA256 commitment. It does not exclude clock adjustments outside the minute, timestamp time zones or rounding not represented by either conversion, nonstandard hash functions, multi-process PIDs, per-packet random-byte buffering, hidden phases beyond15, different generators, unknown independent keys, or physical copy damage.

No selected original K04 coupon bit is authenticated. The K08 author-final line remains unavailable verbatim. The strongest next input remains an independently authored physical attempt2 copy, the writer's actual source-code/seed/state record, or the literal Emily final-margin inscription.
