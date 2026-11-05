# Noisy selected ACK inversion for classic .NET `Random(int)` (5 November 2026)

## Mechanism and original evidence

Prior source-only fits can leave the selected historical physical coupon completely unconstrained. Instead, this experiment treats the **copied 18:02Z ACK2 buffer as a noisy observation** of a generator's complete physical 16-byte coupon, allowing unknown byte substitutions and hidden draws. This is conceptually different from either source-only chronology reconstruction or arbitrary repair enumeration: a small, hypothesized printer state is recovered from surviving copied bytes, and its *entire* 16-byte output is checked against the **unchanged original K04 SHA commitment** after applying the recorded original XOR mask.

Source: `resources/evidence/print/spool-reconstruction.log`, original SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Selected logical route `ESC-N`, job `PS-261003-0417`, `2026-10-03T18:02:00Z`, `ATTEMPT=2 STATE=ACK CLASS=RECOVER`. The **copied** `PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5` is not presumed physically intact.

## New recovery algorithm

Hypothetical producer: fresh legacy Microsoft .NET Framework `System.Random(int seed).NextBytes(16)`, unknown scalar seed (absolute 31-bit value) and 0..64 discarded output bytes. The generator implementation is from [Microsoft's classic reference source](https://github.com/microsoft/referencesource/blob/main/mscorlib/system/random.cs).

For each offset and both copied-byte orientations:

1. Derive seed-affine positions from outputs of seed 0 and 1, retaining only positions that agree with the proposed affine identity across 20,000 independently sampled seeds. Across all 65 phases, 7..12 of the 16 positions qualify.
2. For each of the first six affine positions, enumerate all possible 31-bit scalar seeds consistent with that *one* observed byte, through an exact modular inverse.
3. Compare the remaining empirical affine positions; retain seeds matching at least `max(3, affine_count-6)` observed bytes.
4. Recompute the entire physical 16-byte coupon with the **actual** reference generator, check both possible complete coupon orientations against the original mask and K04 SHA commitment, and count exact copied-byte positions.

The first six candidate anchors guarantee at least one unchanged seed anchor under **up to four arbitrary byte substitutions**. At least `affine_count-4` retained affine bytes remain correct under that damage assumption, exceeding the survivor threshold. Thus the method recovers any such model-consistent coupon **provided the seed truly obeys the empirically identified affine relations**. This is an explicit conditional completeness claim, not a proof over every 31-bit seed and all possible copy faults.

Portable NumPy SFT: [`agents/agent4/k04_dotnet_noisy_ack_sft.py`](../agents/agent4/k04_dotnet_noisy_ack_sft.py); it uses the sibling [exact classic .NET generator port](../agents/agent4/k04_dotnet_seedbyte_inversion_sft.py).

## Tests and observations

- Planted 16-byte generator packet from seed 1,234,567, with four deliberately changed bytes **PASS**: recovered seed and full original coupon, 12/16 copied bytes matched.
- Independent planted six-byte edit **PASS** on the chosen error positions: recovered seed and complete coupon, 10/16 copied bytes matched. Not all six-byte error supports are covered.
- Full original run: **65 offsets × 2 copied orientations = 130 cases**, each case testing both original-coupon output orientations. **458,278 scalar seeds survived the noisy affine screen across those cases, counting repeated seeds in different cases**; each was recomputed exactly, then checked against both complete-coupon hash orientations. **Zero original K04 commitment matches.**
- The closest original coupon candidates matched **six copied bytes of sixteen** (forward phases 29, 37, 49). The strongest reversed-copied candidates matched five. These partial matches are not evidence of original producer identification.

## Interpretation and next discriminant

**Conditional exclusion:** a 31-bit classic .NET one-seed producer at an offset of 0..64, with up to four arbitrary original-copy byte substitutions, cannot explain the supplied copied ACK and original K04 commitment under the observed output-affine index relation. For larger damage, a different byte transform, a seed violating the empirical affine relation, or a different exceptional-only producer, the search is not exhaustive.

The separately launched manual original-target search [`.github/workflows/h17-k04-dotnet-scalar-manual.yml`](../.github/workflows/h17-k04-dotnet-scalar-manual.yml) checks **all 2^31 scalar seed values at phase zero**, independently of copied-byte fidelity, in 16 shards. At report time its [workflow run #41972752719](https://github.com/FlareZ123/workplace-v2/actions/runs/41972752719) remained **QUEUED**. Do not report any shard result as completed until actual original workflow outputs are available.

**No original K04 physical bytes or Emily-final K08 words recovered. Official verifier remains six individual PASS; K04/K08 MISSING, combined INCOMPLETE.**
