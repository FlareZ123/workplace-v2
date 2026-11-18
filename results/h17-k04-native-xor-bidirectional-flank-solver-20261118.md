# H-17 K04: native-XOR bidirectional exact inversion of the same-job requested flanks

**Agent 50 | 18 November 2026. Status: planted inversion solved; original source remains solver-inconclusive.** No accepted original K04 component; K08 unchanged. This is a reproducible state-recovery and feasibility result, not an authentication of printer media.

## Concrete recovery attempt

A single selected printer job, **PS-261003-0417**, has original retained copies of three incident-day RECOVER events:

| Event | Time UTC | State | Observed 16-byte PAYLOAD |
| --- | --- | --- | --- |
| Attempt 1 | 18:01 | REQUESTED | \`CD3E4F216ADB2FB180DA2AA90B33F7A4\` |
| Attempt 2 | 18:02 | ACK | \`A9A9DC5731A5E2AE879C47215C2559D5\` |
| Attempt 3 | 18:03 | REQUESTED | \`44D53DFC29D7943A95D89371DA58EC64\` |

Source: original \`resources/evidence/print/spool-reconstruction.log\`, SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`. Original MAIL-16 makes clear ACK is proof of dispatch receipt only, without physical media integrity. REQUESTED entries do not prove print completion.

**Conjectural producer hypothesis:** the two 64-bit words in each event are successive outputs of xoroshiro128++ 1.0; each successive event consumes the next two outputs. Let initial state be \`(a,b)\`. The exact native 64-bit output and update are:

\`\`\`
y = rotl64(a+b,17)+a (mod 2^64)
t = a XOR b
a' = rotl64(a,49) XOR t XOR (t<<21)
b' = rotl64(t,28)
\`\`\`

For the strong *blind middle-coupon* test, only nonselected attempt 1 and 3 REQUESTED bytes enter inversion, furnishing positions 0,1,4,5. Attempts 2 output positions 2,3 are omitted. Four serialization views cover 64-bit big/little endian, in either word order. A complete state would predict a full physical 16-byte attempt-2 coupon. Its XOR with the *unchanged* original \`K04.masked_component\` must match the original full \`K04\` SHA256 acceptance before claiming recovery.

## Mechanisms executed and controls

- **Direct native-XOR SAT circuit** \`agents/agent50/k04_xoroshiropp_xorcnf_sft.py\`: XOR-native CryptoMiniSat clauses for the GF(2)-linear state transition, ordinary CNF for two 64-bit additions per output. Full planted circuit witness validated every clause (2,292 variables, 4,900 CNF, 1,408 XOR). Unrestricted 128-bit *planted unknown-state inversion* reached **UNKNOWN at 240.19s**. Source intentionally gated and not evaluated. [CI run 44203984909](https://github.com/FlareZ123/workplace-v2/actions/runs/44203984909).
- **Bidirectional meet circuit** \`agents/agent50/k04_xoroshiropp_meet_sft.py\`: eliminate second state word *at each known flank* algebraically: \`b=ROR64(y-a,17)-a (mod 2^64)\`. Advance first state twice; invert two GF(2)-linear state updates from the later state; constrain the two 128-bit middle-state representations to equality. Whole-source target still uses the unmodified two remaining flank words. The planted control reveals only the actual **low 16 bits of s0** (a prefix *not available* for original K04); SAT reconstructed the complete true 128-bit state \`5D1DE1A5CAFEBEEF/17A5B3CB69A1CBCA\` and two hidden words \`BD85A5C2F073B6A5/CF9E7F49E1D6DA63\`, in 4.5–5.5s per CI job. Clause witness validation passed 2,680 variables, 4,788 CNF, 1,792 XOR.
- **Unrestricted original bracket** using the same working meet code: **four serializer views, four UNKNOWN results after 240.1–240.2s each**. No SAT, UNSAT, predicted coupon, or original commitment hit. [CI run 44205434930](https://github.com/FlareZ123/workplace-v2/actions/runs/44205434930). These timeout results are not exclusions of the generator model.
- **Prefix cost calibration** on a planted true generator: bit-prefix lengths 8,10,12,14,16, with correct and deliberately wrong prefix, timeout 60s each. Correct prefixes **8 UNKNOWN, 10 SAT 54.58s, 12 SAT 3.003s, 14 UNKNOWN, 16 SAT 5.504s**. Wrong prefixes **8/10/12/14 UNKNOWN**, **16 UNSAT 17.12s**. Runtime is nonmonotonic and wrong-prefix rejection is often slow. Thus a full \`2^16 × 4\` original partition grid is *not economically justified* by the single favorable 16-bit planted positive. [CI run 44206619511](https://github.com/FlareZ123/workplace-v2/actions/runs/44206619511).
- **Inverse-second-output variant**: replaced second-flank forward output adders by inverse equations, eliminating unconstrained middle-output circuits: 2,560 variables, 3,304 CNF, 1,920 XOR. Independent seeded circuit witness passed, but its planted low16 positive inversion returned **UNKNOWN after 100.18s**; source did not run. [CI run 44207443454](https://github.com/FlareZ123/workplace-v2/actions/runs/44207443454). This smaller circuit is slower on the essential positive, so size alone is not an improvement.

## Scope, decision and next evidence

The model's emitter identity, shared state between attempts, exactly two outputs per attempt, and physical coupon authenticity are *not attested by the source*. Real-source timeouts therefore provide no ground for claiming original K04 recovery or exclusion. The copied ACK2 is withheld in the core blind test and is never treated as a verified physical coupon. No original source, route, acceptance, verifier or six-PASS candidate was changed.

The next meaningful branch is a source-selected producer/seed discriminator, better unrestricted solver physics with a genuine planted inversion control, or an independent physical ESC-N attempt-2 coupon/queue image. Running vast arbitrary seed-prefix grids, retrying the same 240s per serializer, or counting UNKNOWN as source incompatibility will not advance recovery. K08 still needs a concrete author-final full-phrase witness or a credible source-linked deterministic extraction operator.
