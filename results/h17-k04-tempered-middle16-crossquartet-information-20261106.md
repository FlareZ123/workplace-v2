# K04 hypothetical tempered middle-bit carrier: a target-causal 13-bit information channel

**Agent23 | 6 November 2026 UTC | exact conditional GF(2) result.** The selected physical K04 coupon remains **unrecovered** and 0/128 historical selected bits are authenticated. K08 exact author-final words remain unquoted; six established slots still PASS, combined REC8/1 INCOMPLETE.

## Different question

Earlier source-fitted p951 MT19937 analyses established that even the exact **highest twelve or lowest twelve tempered output bits** of all 435 unprinted nonselected printer-stream stages would leave the withheld selected fourword coupon entirely unrestricted. Another study found native, **untempered** low/high bitplane oracles could reduce uncertainty. These are different observation types: MT19937 tempering is a nontrivial invertible binary matrix, and in an original source actual public output words are tempered.

This experiment asks whether a hypothetical independent carrier exposing the **middle sixteen tempered bits**, bits 8..23 (LSB is bit 0), for an unprinted printer-native output stage could transmit selected K04 information that neither separate 12bit edge window can. A halfword in the *middle* of a tempered output is a particular conditional data-serialization model; **no preserved carrier is authenticated as such an output**.

## Exact source construction

The unchanged original spool \`resources/evidence/print/spool-reconstruction.log\`, SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`, has 133 sixteenbyte packet rows. Omit selected ESC-N ACK2 row129 **before fitting**. The same published speculative \`p951\` 133-row starts and 624-word symbolic native MT19937 source generator as [Agent49's basis](../agents/agent49/k04_p951_symbolic_basis.py) fit all 132 undamaged original packet rows with exact rank **15,365** (16,896 copied source bits, 1,531 redundant linear combinations). No selected copied ACK2 bytes, mask, acceptance digest, or K08 source enters the fit.

Under this hypothetical source model the omitted selected event emits four native stages **951..954**, all **128** tempered output bits initially independent modulo intact original data. Among native stages 0..966, exclude the 528 observed payload output stages and four selected output stages, leaving exactly **435** hypothetical unprinted *nonselected* stages.

Each hypothetical carrier equation is the binary expression for a specific bit of MT temper(native-stage-word). To measure actual information content independently of *what values* an oracle might report, append these equations to the source row space. For selected target row space T and oracle/source row space O, the missing target dimension is \`rank(O + T) - rank(O)\`, with a complete GF(2) basis reduction that preserves cross-bit linear relationships.

## Actual conditional ranks

| Additional ideal exact observations, all 435 hidden stages unless specified | New total source rank | Remaining selected coupon dimensions |
| --- | ---: | ---: |
| No oracle | 15,365 | **128** |
| Tempered output bits 0..11 (lowest 12) | 18,203 | **128** |
| Tempered output bits 20..31 (highest 12) | 18,203 | **128** |
| **Tempered output bits 8..23 (middle 16)** | **18,820** | **115** |
| Only critical four stages 328..331, middle16 | 15,429 | **128** |
| Only critical four stages 724..727, middle16 | 15,429 | **128** |
| Both critical quartets, eight stages, middle16 | **15,493** | **116** |
| Both critical quartets, lowest 16 tempered bits | 15,493 | **127** |
| Both critical quartets, highest 16 tempered bits | 15,493 | **127** |

Thus the full hypothetical **middle16** leak would constrain **13 linear dimensions** of the unknown native selected coupon. The narrow **eight-stage** leak supplies **12** dimensions, but either critical quartet alone supplies **zero**. This is an exact synergy in the MT state recurrence, not 12 individually recovered physical bits.

The eight critical states are exactly the original p951 causal stages previously derived by Agent15: \`328,329,330,331,724,725,726,727\`. The other 427 source positions collectively supply the thirteenth dimension; **no single other stage** added on top of the critical eight supplies it, and no single 32stage block does either (tested exact rank on the same original symbolic data). There is no independent historical evidence that these eight stage values were written in an off-printer 16bit format.

## Provenance, controls and reproduction

The source-pinned [portable standalone target-quotient SFT](../agents/agent23/k04_middle_tempered_oracle_sft.py) imports the repository's established Agent49 symbolic source module, calculates all oracle equations and asserts the rank table. An independent local source-equivalent implementation executed against the original 46member uploaded ZIP and reproduced these counts. A planted positive adds the first actual eight tempered target-output bits from each of the four missing stages as *synthetic* observations and verifies precisely 32/128 target dimensions are removed, leaving 96. It does not use the disputed copied packet or mutate any original source. These positive checks establish the quotient measurement's ability to register genuine target information.

This is an algebraic counterfactual, **not a discovered external leak**. No K04 candidate bytes or commitment match were produced, and the assumed p951 chronology/MT firmware is not historically authenticated. The measured relation would apply only if the source producer, exact stage indices, public-output tempering and a whole independent middle-halfword carrier were all established. Prior arbitrary K02/K07 halfword-to-native concatenation tests and whole 16byte donor-pair tests did not match the original acceptance. The current experiment neither overrides those negatives nor demonstrates a new physical reconstruction.

## Consequence

The former edge-bitplane information ceiling must **not** be extrapolated to all possible 16bit public-output projections: the *position* of the observed bits can change selected target information. For an actual attempt to recover K04, seek a source-selected and independently held-out 16bit emitter with time/stage provenance at or around the two causal quartets. Critically, a source only identifying or reporting guessed printer categories is insufficient, and unindexed K02/K07 substitutions cannot establish the proposed carrier. Without a real original carrier, the 13bit information bound has **no direct effect on the original K04 solution**.

All official files, original selected copied ACK, K04/K08 commitments and canonical six accepted candidate components remain unchanged.


## Stronger decomposition and explicit original-data parity witness (20:42 UTC)

The 12/13 counts above should be separated into **pure native-MT recurrence identities** and genuine constraints supplied by intact original printer records. A second exact rank run **removed all 132 original source packet equations**, retaining only the symbolic 624×32 generator and the hypothetical same middle16 oracle:

| Perfect hypothetical middle16 oracle | Independent selected coupon equations with no original spool data | Independent selected coupon equations after all 132 intact originals |
| --- | ---: | ---: |
| Only eight causal stages | **11** | **12** |
| All 435 hidden stages | **11** | **13** |

Thus the authentic intact source contributes **one extra** target relation to the eight-stage oracle and **two extra** to the full hidden-word oracle. Without the independent partial-output measurements, the original spool alone contributes **zero** target relations. This decomposition identifies a particularly narrow hypothetical *source-coupling opportunity*, rather than mistaking bare MT recurrence identities for data newly recovered from archive records. The portable SFT now asserts no-original-source ranks **128** (eight-oracle only) and **6,889** (435-stage oracle only), both with selected residual **117**.

An independent, right-hand-side-tracking GF(2) elimination using the source's actual 132 accepted intact packet bytes further produces **12 exact parity certificates** relating the selected tempered coupon bits, the eight hypothetical middle-halfwords, and the observed source. Removing the source equations leaves **11** of these independent; only the first source-inclusive relation adds a genuinely archive-dependent linear constraint. With bit0 as the LSB of the first 32bit emitted target word, oracle bits ordered by stage \`328,329,330,331,724,725,726,727\` and by bits8..23 ascending within each stage, that one additional relation has:

- selected 128bit mask: \`00000000000000000000000000009200\` (three selected bits);
- concatenated oracle 128bit mask: \`00000000000000920000000000000004\` (four hypothetical outside bits);
- original-source parity constant: **0**.

The equation is \`parity(selected & 0x9200) XOR parity(oracle & 0x00000000000000920000000000000004) = 0\`. This **does not reveal** the three selected bits, since the four oracle bits are unobserved in the original material. Its value is an explicit falsifiable source-derived equality: any proposed genuine independent halfword carrier at the eight exact stage positions must satisfy it, whereas the pure MT recurrence does not itself entail this particular equation. A complete source-consistent 19,968bit state was constructed by backsubstitution, all 132 intact original packets regenerated exactly and every one of the 12 eight-stage parity identities verified against this independent state completion.

The full 435-stage gain of two source-assisted equations likewise depends on hypothetical values for far more hidden outputs; it cannot be read as recovered physical coupon data. All computations avoid the disputed original selected copied ACK and K04 commitment.


## Full-oracle compression: only thirteen exact hidden stages suffice (20:48 UTC)

A further exact source-plus-oracle rank computation materially sharpens the otherwise unrealistic 435-stage idealized observation. Under the same unchanged p951 source, the **entire 13-dimensional source-and-MT target information** of the middle16 observation of all 435 hidden stages is already obtained from **13 specific unprinted stages**:

\`104, 105, 328, 329, 330, 331, 332, 500, 501, 724, 725, 726, 727\`

The hypothetical 13×16bit middle-halfword carrier adds **204** independent equations to original rank15365, giving total rank **15,569**. Adding all 128 missing selected coupon equations increases rank by **115**, exactly the same selected quotient as observing middle16 at all 435 stages. The corresponding test with no original spool records has oracle rank **206**, target residual **117**. Hence the compact 13stage view attains all **13** conditional target parity relationships, of which **two** exploit the real intact spool constraints beyond the 11 bare MT recurrence relationships. This 13stage construction is a **sufficient witness**, with no assertion of global minimum or of a physical historical source for those stages.

An alternative **five-stage** carrier \`100, 101, 328, 496, 497\` alone adds 78 independent source equations (rank15443) and reduces the missing target dimension to **125**, three new target parity relations. These five positions appeared when symbolic right-hand-side elimination tracked which exact unprinted stage oracles participated in the original-source-conditioned target certificates. A different 6stage certificate involving stages \`104,105,331,332,500,501\` supplies the independent target parity direction that the original eight critical stages alone do not. Combining those positions with the eight critical stages yields the thirteen-stage sufficient set above.

This sharpens the next potential archive-carrier search from 435 indiscriminate unprinted words to a specific **26-byte hypothetical middle-halfword source spanning 13 stages**. All 13 physical observation values are absent from the surviving export under the stated producer model, so the actual authenticated K04 information gain remains **zero**. The repository SFT now asserts the source-assisted and source-free compact ranks separately, avoiding any inference that this is a found coupon or a validated printer algorithm.
