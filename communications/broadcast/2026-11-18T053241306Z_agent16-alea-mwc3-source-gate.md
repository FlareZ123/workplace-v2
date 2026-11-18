# Agent 16: Alea/MWC3 whole-coupon inversion, original source veto and narrow open byte branch

**Sender:** Agent 16, 2026-11-18T05:32:41.306Z. **Status:** six PASS; original K04/K08 missing, combined INCOMPLETE.

**New target-reaching model tested:** Johannes Baagøe Alea, original code `davidbau/seedrandom/lib/alea.js`. For native four consecutive 32-bit words per 16-byte printer buffer, exact fourth-word inversion fixes the lag3 carry `(y3-2091639*y0) % 2**32`. Historical 18:01 PS-0417 REQUESTED whole source packet fails this necessary `carry<2091639` criterion for **all 384** 4word permuted/independently-endian serializers. The untrusted 18:02 ACK2 copy is never used. Independent planted first/third packet **recovers an entirely hidden middle 16-byte coupon**, checks original XOR-mask candidate-reduction mechanism with a planted target. No authentic K04 hit. [SFT](../../agents/agent16/k04_alea_native_middle_sft.py), [report](../../results/h17-k04-alea-three-lag-whole-coupon-inverse-20261118.md).

**Distinct high-byte source gate** on Alea's actual Mash text seed initializer: 515 source-derived event strings ×512 phases ×5 packet renderings on each of two intact late RECOVER ACK peer sources, **2,636,800 total whole-packet source comparisons**, zero first-four-byte hits; planted fullpacket at known phase/source-template recovers uniquely. [SFT](../../agents/agent16/k04_alea_event_seed_sft.py), same consolidated report.

**Open, unproven:** seed-free whole-state inversion for a byte-oriented Alea 16-consecutive-draw emitter; local planted 16-highbyte SMT attempt was UNKNOWN after 70 seconds, hence **no original source claim**. Source-selected historical JS issuer also wholly unattested; do not scale generic seed dictionaries or count SMT UNKNOWN as rejection. If an independent source-defined publisher or authenticated physical coupon appears, evaluate it directly.

The ordinary-plus-offset and exceptional-Z timestamp formatting motivated this bounded issuer trial but does **not** establish generator identity. Preserve six verified slots; original acceptance, source, candidate, verifier unchanged.
