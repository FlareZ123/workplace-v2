# K04 p951: exact CPython seed-term inversion excludes 73 additional key lengths

**Agent 45 | 2 November 2026 ~20:12 UTC | Original-source-only conditional producer falsifier; K04 and K08 still missing.**

## New method and quantified advance

Under the **same historically unverified** p951/first-output CPython MT19937 seed-array producer hypothesis used by Agent19, the earlier [64-term seed-length sieve](h17-k04-p951-cpython-firstcycle-seed-length-sieve.md) left 144 candidate initial integer seed lengths among 1..623. This investigation derives **full missing initialized-state words** from reused CPython key-array residue terms, then projects them through the exact MT19937 output-state recurrence against independently preserved intact printer payloads.

| Check on original source | Conditionally surviving CPython seed-array lengths 1..623 |
| --- | ---: |
| Agent19's 64 complete/onebit-uncertain key terms (reproduced unchanged) | **144** |
| **New** inverse key-term constraints plus iterative candidate-domain propagation | **118** (26 newly inconsistent) |
| **New** exact MT recurrence consistency after injecting source-forced initialized bits | **85** (33 more inconsistent) |
| **Extension:** enumerate one-bit-uncertain neighboring words, then repeat both checks | **71** (6 more inversions + 8 MT contradictions) |

The initial exact-neighbor method excludes **59** of the previous 144 lengths. The subsequent one-bit-neighbor extension excludes **14 more, totaling 73** additional lengths. In this conditional first-cycle model, **all seed lengths 1..363 now fail**, and the first length not rejected by these particular necessary checks is 364. The remaining 71 lengths are *not proven viable seeded streams*. Seed length 624 and longer, other output-origin phases, other chronology vectors, nonstandard MT initializers and alternative producers are outside this test.

## The structural innovation

Let the native initial 624-word CPython register be \`S\`, \`G\` the standard \`init_genrand(19650218)\` reference, and \`F_c(x)=c(x XOR (x>>30)) modulo 2^32\`. The official \`init_by_array\` mixing arithmetic implies, for stable nonwrapping indices i=4..623, a necessary key term:

\`\`\`text
P = (S[i-1]+i-1) XOR F_1566083941(S[i-2])
Q = (S[i]+i) XOR F_1566083941(S[i-1])
T[i-1] = Q - (G[i] XOR F_1664525(P)) modulo 2^32
\`\`\`

For an integer seed represented by \`n\` little-endian 32-bit words, the terms \`T[j]\` and \`T[j+n]\` must be identical whenever both are defined. Agent19 previously compared only 64 source-derived \`T[j]\` domains with at most one initially unknown state bit. This experiment uses those established 64 term domains as *anchors* but reaches neighboring triples whose third or first state word was previously almost entirely unknown.

Since both mixing multipliers are odd, \`F_c\` is invertible modulo 2^32 (multiply by \`c^-1\`, then invert \`x XOR (x>>30)\` using one additional XOR-shift). Given a candidate key term and the two fixed neighboring original state words, derive the missing first or third full state word exactly. Reject a length if **every** candidate source term contradicts any pre-existing printer-fixed state bit. Otherwise propagate the bitwise consensus of all surviving values, derive new key terms, and iterate. Finally inject only the resulting new state bits into the original 132 intact source-packet MT closure, detecting exact output-recurrence contradictions.

This is a stronger, deterministic necessary-condition inversion than the predecessor's pairwise residue comparison. It also differs from the prior numeric seed dictionaries, short-seed inversion and arbitrary printer copy repairs.

### Concrete independently checkable counterexamples

- **Length 249**, the predecessor's first survivor: source term at \`j=494\` has possible values \`50049923\` and \`D0049923\`. The same residue requires it at \`j=245\` (\`i=246\`). With original complete \`S[245]=9A4175B7\` and \`S[246]=2079EE69\`, inversion demands \`S[244]\` equal \`A2386E73\` or \`F725CB48\`. Both have the high bit set, whereas the separate original printer-source closure already fixes **S[244] bit31=0**. Thus n249 is eliminated without an unknown seed search or the K04 acceptance hash.
- **Length 307** initially survives the inversion stage but fails after one propagation cycle: a newly fixed state makes key-residue term \`j=563\` inconsistent with the same-key residue domain.
- **Length 392** initially satisfies the key-residue propagation itself, but reinserting its inferred initial bits into the original MT source closure creates a conflict at native relative index **-57**. This is an intact printer-stream contradiction. Length 557 similarly conflicts at -208.

These examples are conditional consequences of the stated original p951 index vector and producer. No acceptance digest, disputed selected packet, mask or other slot was used to select or eliminate a length.

## Reproduction, controls and genuine limits

[Single-file SFT](../agents/agent45/k04_p951_seed_residue_inverse_sft.py) requires only Python standard library and the unchanged \`resources/evidence/print/spool-reconstruction.log\`, SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`. It excludes row129 before parsing its words. It asserts original counts **144 → 118 → 85**, the 364 first survivor, the specific 249/307/392 and 406/511 exclusions, and **four zero original selected-state masks** for every survivor.

It also independently tests 128 three-word random modular inversions (256 inverse calls) and **12 initial plus 14 extended end-to-end genuinely seeded CPython streams**. The initial controls include: two each with seed lengths 249, 307, 364, 392, 509 and 623. Every synthetic source uses the exact original 133-position hypothetical p951 spool-index pattern, withholds its selected packet, reconstructs register masks, carries out key-domain propagation and MT recurrence, and checks the fixed bits against the true initialized register and all four true selected native state words. All **26** full-spool synthetic controls pass, including seed lengths that the **historical** source rejects. These positives detect false rejection caused by mistakes in the inversion or mask propagation. They do not authenticate the printer's actual firmware.

The **source itself does not establish** a CPython producer, first-cycle origin, seed length or physical copy integrity. The p951 chronology also conflicts with a separately hypothesized ordinary CLASS sampler at row84; this contradiction has not been resolved. For every one of the remaining 71 length hypotheses, all four selected K04 native state words still have **zero individually fixed bits** under this propagation. No actual K04 coupon bit or K08 final word was recovered. The unchanged REC8 acceptance remains six individual PASS, K04/K08 MISSING, combined INCOMPLETE.

**Next discriminating attack:** invert the middle initialized-state word in each key triple rather than only the first/third; it occurs twice inside the nonlinear mixing expression and might add new original-source constraints. Alternatively project multiword inverse-domain relationships into exact target-quotient linear equations. These are concrete different methods that may go beyond the 85-length necessary-condition bound, but a complete original coupon still requires a historically viable generator model that reaches selected indices.

## Follow-up: one-bit-uncertain neighboring state extension (~20:23 UTC)

The first inversion required both neighboring `S` words completely fixed. The original source has 96 additional register words with **31** fixed bits, leaving one unknown MSB. For every repeated-key equation with unknown outer `S` word, independently enumerate its two neighboring input words when each has at most one missing bit. The fixed key domain has one or two values, so the complete inverse yields at most eight possible fullword values. Filter against original observed state masks and propagate only bitwise consensus. This is a conservative superset: correlations discarded by the enumeration cannot produce false exclusions.

Applying this to the 85 initially surviving n values gives **6** new direct inverse contradictions (n406,479,499,500,538,539) and **8** further native-source recurrence conflicts (n413,462,510,511,517,523,530,537). There are **71** remaining possible lengths under the full *conditional* screen. The first allowed remains **n364**; source words at selected indices951..954 still have zero individual fixed bits for every survivor.

An exact new original witness is **n406**: source anchor `T[514]` takes `203D56E6` or `A03D56E6`; the repeated key residue demands this at `T[108]` (i109). Source independently fixes `S[108]=B5E66F66`, `S[109]` lower31=`00C08FCB`, and **S[107] MSB=0**. Across both source-term choices and both high-bit completions of `S[109]`, the inverse always yields `S[107]` equal `A0431703` or `F53073D8`, both highbit1, contradicting the original printer observation. That is the extra one-bit-neighbor constraint; it did not arise from the earlier exact-neighbor method.

The SFT now asserts 144→118→85→**71** and additionally runs **14 full synthetic originally seeded control streams** across lengths364,406,479,499,511,539,623 (two seeds each). All 14 pass the new enumerated-neighbor inference and subsequent MT closure, and known synthetic selected words remain consistent. Combined with the earlier 12 full controls, **26/26 end-to-end positives** pass. The historical printer and K04 target remain unverified.
