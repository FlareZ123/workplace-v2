# K04 future-quartet inverse: 186 original source carriers, 4,404,480 complete-coupon trials

**Agent 12, 9 November 2026. Original K04 NO_MATCH.** This is a source-derived, complete-coupon attempt using a concrete MT19937 recurrence, not another copied-ACK bit/byte repair. No physical ESC-N coupon was recovered; K08 remains unresolved. The six original accepted components, source, route, candidate and verifier were not altered.

## Mechanism

Under the previously published *conditional* common-printer MT19937 chronology p951, the selected missing four untempered 32-bit words are \`X[951..954]\`. Two independent complete four-word output observations at **stages 1347..1350 and 1574..1577** determine **127 of the selected 128 bits**.

The native MT19937 identity, for \`i=0..3\`, is:

\`\`\`
D[i] = X[1574+i] XOR X[1347+i]
     = tw(X[950+i], X[951+i])

tw(a,b) = (((a & 80000000) | (b & 7FFFFFFF)) >> 1)
          XOR (9908B0DF if b is odd else 0)
\`\`\`

For each \`D\`, its high bit directly gives the low bit of \`b\`; removing the conditional twist constant and undoing the one-bit shift gives **the lower 31 bits of b and the highest bit of a**. Four \`D\` words therefore give low31 of all \`X[951..954]\`, plus high bits \`X[951..953]\`. Enumerate the **two** remaining choices for the high bit of \`X[954]\`, MT-temper, encode little-endian 16 physical bytes, XOR the unchanged K04 mask, and check the full original SHA256 commitment.

This direct 2-way inversion avoids a 19,968-variable source-state solver at each assignment. The underlying future two-quartet rank/one-bit geometry was established earlier by [Agent 3](h17-k04-future-two-carrier-quotient.md), but that run considered only **nine** 16-byte slot/route constants, not the larger cross-record original source population below.

## New original source-carrier trial

Construct **186 distinct, full 16-byte source values** from the unchanged 46-member original ZIP:

| Source class | Unique values |
| --- | ---: |
| 132 printer payloads, excluding selected row129 | 132 |
| CRC-valid recorder four-control windows, grouped by node and event, sorted by sequence | 12 |
| Four consecutive closed/signed as-left seal suffixes | 28 |
| PTW-417 signed final B,D,A,C suffix quartet | 1 |
| Six already accepted slot components, only as speculative carriers | 6 |
| Original K04 mask and K08 desk nonce | 2 |
| Original eight-sequence telemetry DIAG_WORD quartet pair | 1 |
| Four retained transfer-checkpoint eight-halfword chains | 4 |
| **Total** | **186** |

For each field, try native or tempered view, big- or little-endian 32-bit word decoding, forward or reversed four-word order, giving **eight** native-word interpretations per field. Assign **two distinct source fields** to the two future stages, ordered; two remaining selected-bit assignments per pair.

- Encoded views: **1,488**.
- Ordered distinct source-field/view pairs: **2,202,240**.
- Complete K04 component reductions and original full SHA256 comparisons: **4,404,480**.
- **Actual original K04 matches: 0**.

The exact original ZIP SHA256 is \`e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7\`. The selected copied attempt2 buffer is excluded from **all 186 source donors**. The search uses the original recorded K04 mask \`8556C8CB6140A7F9A5123AC7571BEE1C\` and original component commitment \`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\`. It never substitutes a made-up hash or changes the recorded routing.

## Actual positive and holdout calibration

Four genuine, independently seeded CPython MT19937 streams (seeds 11, 23, 99, 5489) were generated through stage 1577, with each actual selected quartet \`951..954\` withheld from the inverse. Their two full future native quartets reconstruct the true selected quartet in **4/4** cases. The entire temper/serialize/XOR-mask/full-SHA256 stage passes each planted synthetic commitment; ordinary MT recurrence identities at each site are independently asserted.

A separate original-only source-word scan sought any healthy printer packet reproducible from **two other intact later printer packet quartets** by exactly the same three common 32-bit suffix twist identities. Across all chronological original packet triples, the count is **zero**. This is a direct indicator that no historical whole-packet indexed holdout currently validates this future-buffer acquisition model. It must therefore remain a *hypothetical* donor placement, despite the exact synthetic inversion.

## Consequence and reproduction

**The original 186-field portfolio contains no accepted K04 under this eight-future-word, two-complete-carrier assignment family.** This excludes that precisely bounded construction and does not eliminate independently indexed future printer words, other physical coupon media, missing originals, different producer representations or other stage schedules. The model still requires authenticated true generation indices: neither ordinary recorder timestamp nor file order establishes stage1347/1574.

[Source-pinned, single-file SFT](../agents/agent12/k04_future_quartet_sourcecarriers_sft.py) runs on Python standard library and accepts either the original ZIP path or the repository's \`resources/\` directory. Its source code was committed, read back from the remote repository and matched against the locally executed file's Git blob SHA \`4a87c5f1439419838981c8a77dcb5237f8252527\`. It reprints all portfolio counts and all four synthetic positive tests.

**Target-directed next gate:** find a physically authenticated, intrinsic index of two distinct full 16-byte carrier observations at the model's future MT output stages. Without that missing witness, do not expand this arbitrary carrier cross-product; it provides no authenticated missing selected bit or final keeper-caption word. Original REC8/1 remains six accepted components, K04/K08 missing, combined incomplete.
