"""Complete K04 two-source 128-bit arithmetic issuer pilot (Agent35, 4 Nov 2026).

Uses the unchanged, 532-unique historical source-carrier construction already
implemented and source-pinned in Agent22's prior SFT. Unlike the latter's MT
future-donor syndrome, this trial models the physical coupon itself as a
two-share GF(2) XOR or 128-bit modular add/sub of existing archival blocks.

Selected copied ACK2 excluded. Original targets, mask and resources read-only.
Run: python agents/agent35/k04_crosssource_pair_arithmetic_sft.py
"""
from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
upstream = ROOT / 'agents/agent22/k04_all_original_future_donor_pairs_sft.py'
code = upstream.read_text(encoding='utf-8')
# Import only the original-data 532-carrier constructor, stopping before
# Agent22's separate 36-million-pair MT recurrence experiment. This keeps
# the identical source selection without duplicating a 100-line extractor.
prefix, delimiter, rest = code.partition('\nx556,x557,x558=s.source_words()\n')
assert delimiter and 'assert len(src)==532' in prefix
scope = {'__name__': 'agent35_reused_carrier_extractor', '__file__': str(upstream)}
exec(compile(prefix, str(upstream), 'exec'), scope)
source = scope['src']
assert len(source) == 532
assert bytes.fromhex('A9A9DC5731A5E2AE879C47215C2559D5') not in source

mask = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
original = bytes.fromhex('930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0')
items = list(source)
mod = (1 << 128) - 1
# Genuine planted two-donor coupon (not original K04) tests the same
# enumerator in a case it must recognize.
planted = bytes(a ^ b ^ m for a, b, m in zip(items[1], items[-2], mask))
planted_digest = hashlib.sha256(planted).digest()
planted_hits = 0
original_hits = []
checked = 0
for i, a in enumerate(items):
    x = int.from_bytes(a, 'big')
    for j in range(i, len(items)):
        b = items[j]
        y = int.from_bytes(b, 'big')
        for op, v in (
            ('xor', x ^ y),
            ('add', (x + y) & mod),
            ('sub_ab', (x - y) & mod),
            ('sub_ba', (y - x) & mod),
        ):
            coupon = v.to_bytes(16, 'big')
            for stage in ('masked_coupon', 'direct_component'):
                component = bytes(c ^ m for c, m in zip(coupon, mask)) if stage == 'masked_coupon' else coupon
                digest = hashlib.sha256(component).digest()
                checked += 1
                if digest == original:
                    original_hits.append((i, j, op, stage, component.hex().upper()))
                if digest == planted_digest and op == 'xor' and stage == 'masked_coupon':
                    planted_hits += 1
assert checked == 532 * 533 // 2 * 4 * 2 == 1_134_224
assert planted_hits >= 1
assert original_hits == [], original_hits
print('SOURCE_BLOCKS', len(source), 'PAIR_ASSIGNMENTS', 532 * 533 // 2)
print('COMPLETE_K04_CANDIDATE_ASSIGNMENTS', checked)
print('SYNTHETIC_MASKED_TWO_SHARE_POSITIVE_HITS', planted_hits)
print('ORIGINAL_K04_MATCHES', len(original_hits))
print('SOURCE_SELECTOR_ACK2', 'excluded')
