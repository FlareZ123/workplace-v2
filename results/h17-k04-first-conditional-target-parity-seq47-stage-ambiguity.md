# First target-facing K04 parity from a 56-recorder history: one conditional bit, not authenticated

**Agent 2 | 3 November 2026 | exact original-source GF(2) analysis**

**Status:** Original six REC8/1 slots K01/K02/K03/K05/K06/K07 PASS; original selected K04 and exact K08 remain MISSING; original combined checksum INCOMPLETE. The equation below is a **conditional model consequence** with a concrete competing history that lacks it. It is therefore **not** an authenticated seventh component or a justified permanent alteration of the official candidate.

## New mechanism reaching the selected K04 quotient

The original 132 intact printer payloads, with the disputed selected ACK row129 excluded, generate the same source-pinned p951/MT19937 GF(2) basis rank **15,365**. Previously source-selected recorder CONTROL anchors and the [new seq39 AUX13 witness](h17-k04-node50-seq39-aux13-conditional-permutation-bridge.md) motivate testing a common MT source for many additional original node50 records. Full **32-bit native CONTROL parity syndromes**, ordering bounds **4..11 MT outputs per original sequence interval**, and joint exact binary consistency across records admit a frozen chronology with **56 of the 64 original node50 records seq7..70**. It omits original seq **28,31,34,35,53,62,66,67**. This is a data-selected *compatible history*, and omitted records are genuine original CRC-valid observations, not established acquisition faults.

All 56 inserted 32-bit CONTROL observations are jointly compatible with original intact spool records. Their joint basis rank rises to **16,663**. The four **selected** native MT output words, 951..954, now add rank **127** rather than 128. The incremental one-parity relation is extracted *without* reading the original K04 acceptance digest or using the damaged selected ACK bytes.

In the model's original printer output byte order (each tempered 32-bit word emitted little-endian), for the **unknown true 16-byte selected printer payload** \`P\`:

\[
\boxed{\operatorname{bit}_7(P[1])\ \oplus\ \operatorname{bit}_6(P[3])=1.}
\]

The equivalent 16-byte parity selection mask is **\`00800040000000000000000000000000\`**. The route's original K04 XOR mask is \`8556C8CB6140A7F9A5123AC7571BEE1C\`. Therefore, for the unknown true **K04 component** \`C=P XOR route_mask\`, the same two-bit XOR must be **0**.

The retained selected reconstruction \`A9A9DC5731A5E2AE879C47215C2559D5\` has payload parity **0** under this mask, so it **disagrees** with the one admissible model history. It already fails the original cryptographic K04 acceptance independently; the parity disagreement does not by itself identify which physical byte was damaged.

Two independently seeded, explicit complete GF(2) state assignments satisfy **all** original printer and 56 recorder equations and produce different 16-byte coupons. Both satisfy the parity above. Consequently the conditional rank-127 constraint leaves **127 selected unknown bits**, and no K04 coupon is recovered by this mechanism.

## Critical ambiguity: seq47 is not source-index authenticated

The one-parity gain depends on placing original node50 **seq47 CONTROL at native index −523**. Withholding seq47 from the otherwise fixed 55-row chronology raises the selected target quotient back to **128/128**. More importantly, indices **−522, −521 and −520** are *also individually and jointly consistent* with the exact same 55 other original records and the 4..11-output chronology. Each alternative yields **full 128/128 K04 uncertainty**, rather than the parity above:

| Original seq47 native placement | Joint source rank | Remaining target bits |
|---|---:|---:|
| −523 | 16,663 | **127** |
| −522 | 16,664 | 128 |
| −521 | 16,664 | 128 |
| −520 | 16,664 | 128 |

The authentic seq47 latch, event, AUX and timestamp offer **no independent original source-fixed high-width discriminator** among these stage choices under the tested nearby field offsets. The previously studied homogeneous recorder sampler already has contradictions in this interval. The model can thus be used to **prioritize an independently indexed seq47 witness**, while it cannot assert that the true coupon obeys the displayed bit equation.

## Scope and reproducibility

The [read-only exact SFT](../agents/agent2/k04_conditional_onebit_parity_sft.py) uses the unchanged original spool SHA-256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`, recorder SHA-256 \`5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba\`, all recorder CRCs, original p951 source and explicitly printed 56 seq/stage assignments. It verifies joint source equations, derives the sparse 128-bit coupon parity and its K04 route-mask translation, checks two distinct full linear-state completions, and reruns the three competing seq47 placements. **No selected printer row, original K04 commitment or phrase is admitted to the symbolic source basis.**

This is a *conditional inference and falsifiable target-reaching mechanism*, not recovered archive bits proven against the original acceptance. Next useful experiment: an external/source-preserved **seq47 exact native stage discriminator** or a complete physically authenticated coupon. Additional original-source facts alone do not establish which currently admissible chronology generated the incident records.
