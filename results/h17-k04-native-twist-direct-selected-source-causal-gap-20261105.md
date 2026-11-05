# K04: stage-free native-twist donors cannot reach the selected coupon

**Agent 9 | 5 November 2026 | Tested on the unchanged original H-17 ZIP.** New target-directed structural negative, not a recovered physical coupon. K04/K08 remain unresolved and combined REC8/1 remains INCOMPLETE.

## Target-directed mechanism

The usual p951 MT19937 chronology makes the selected native four-word output entirely unconstrained. This experiment drops that absolute chronology and asks whether *any* stage assignment consistent with all 42 original source-unindexed 31-bit twist witnesses and minimum monotone four-draw packet order could place **two intact original source packets** at the precise native intervals required to predict at least the *first* unknown K04 word. It thereby tests the source-to-selected structure, rather than merely refitting the same 132 ordinary packets.

The native twist is
\`x[t+624] = x[t+397] XOR mix(x[t],x[t+1])\`,
where \`mix(a,b) = (((a&0x80000000)|(b&0x7fffffff))>>1) XOR (0x9908b0df if b&1 else 0)\`.
If intact source packet a contains \`x[t]\` at lane j, intact source packet b contains \`x[t+397]\` at lane k, and the omitted physical packet row129 starts at \`x[t+624]\`, then their native packet starts MUST satisfy:
- \`start[b]-start[a] = 397+j-k\`;
- \`start[129]-start[a] = 624+j\`.

A further complete four-word coupon predictor requires a fifth consecutive source word \`x[t+4]\`. This hypothesis gets it from source packet a+1 at stage \`start[a]+4\`. With a full source packet b at stage \`start[a]+397\`, the four complete predicted coupon words are \`x[b,j] XOR mix(x[a,j], x[a,j+1])\` (j=0..3, using a+1 lane0 at j=3). Four ordinary endianness/word-reversal presentations are reduced with the recorded K04 mask and the untouched full K04 commitment.

## Original source-only feasibility certificate

The only source read to build chronology is the 132 intact printer packets (copied selected ACK2 row129 explicitly withheld). Original spool SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`.

Recomputing all **42** exact stage-free 31-bit relations independently reconstructs the already published minimum-chronology stage bounds **917..971** for row129. Instead of assuming any p951 event map, Floyd–Warshall closes every exact observed packet-difference equality and minimum four-output chronological inequality. For anchor packet starts \`v_i\` with proposed offsets \`q_i\`, feasibility is equivalent to **every** projected shortest-path bound \`q_j-q_i <= D[v_i,v_j]\`. All graph diagonal distances remain zero (no negative cycles).

**Result: all 99,072** ordered source-packet/lane target-direct donor placements (a<b<129, j=0..2, k=0..3) violate at least one original source/chronology bound. **Zero** even predict the first selected native word. All **8,128** geometries with a, a+1, b <129 required for a complete four-word packet also violate the source-only graph. The latter family consequently has no source-consistent full candidate, even before consulting a target hash.

As an independently bounded exploratory target test, nevertheless compute four serializations of all 8,128 hypothetical *source-inconsistent* three-packet coupons: **32,512 complete unchanged K04 SHA256 checks, zero matches**. The original route mask is \`8556C8CB6140A7F9A5123AC7571BEE1C\`; the immutable K04 component commitment is \`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\`.

## Controls and scope

A genuine \`random.Random(0x98513927)\` seeded MT stream predicts all four native outputs at t624..627 exactly from t0..4 and t397..400; the same complete original-style route-mask XOR and SHA256 reduction agrees with the independently retained seeded output. The original source SHA, 133-row count and omitted selected row identity are asserted. The source-relation count and independently recovered stage bounds provide two additional original-data controls.

This result excludes **direct single-twist four-output prediction from two whole intact print packets**, and its particular three-packet fifth-word completion, under a homogeneous native MT19937 four-consecutive-output packet model and the 42 relation plus monotonic chronology assumptions. It does *not* rule out multi-twist elimination, cross-record donors, other producer architectures, different capture-stage layouts, or the historical selected physical coupon. The original sender, actual stage allocation and physical-media integrity remain unverified. The result therefore cannot authenticate K04 bytes, and makes no K08 final-text claim.

Executable source-pinned SFT: [agents/agent9/k04_stagefree_coupon_geometry_sft.py](../agents/agent9/k04_stagefree_coupon_geometry_sft.py). No source, commitment, candidate or verifier was modified.