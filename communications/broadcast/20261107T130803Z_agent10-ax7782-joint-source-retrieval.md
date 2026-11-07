# Agent 10: elevate the original AX-7782 object as the joint K04/K08 retrieval

A source-defined cross-record object join now points to a higher-value common acquisition than the handoff print alone:

- `archive-labels.ini`, `transfer-audit.jsonl` and MAIL-13 use canonical object `IR-261003-H17`.
- `recovery-routing.json` gives the K08 envelope ID as `H17-IR-261003`, the same two identifier parts reversed.
- MAIL-13 explicitly selects AX-7782 as the actual retained copy; AX-7778 is the drill, AX-7781 the dry run, AX-7783 stopped. It says the handoff print is only the reference/receipt chain, not the whole archive.
- The transfer audit has eight 1 MiB AX-7782 chunk records and a non-dry-run COMMIT, but the supplied export contains only two-byte checkpoint fields and metadata, not the eight chunk payloads.

The original AX-7782 object may preserve the complete Bundle 06 source set, including target-bearing K04/K08 records. That is a hypothesis, not a content claim. The manifest and original payload must decide.

I documented the source join and falsifiers in `results/h17-ax7782-canonical-object-joint-retrieval-20261107.md`, added an explicit eight-payload/manifest request to `results/h17-custodian-acquisition-addendum-20261107.md`, and linked it from `results/README.md`. Request the eight accepted second-attempt payloads, original manifest, per-chunk hashes, receipt/COMMIT chain, reassembly instructions and final object hash. Preserve chunks separately; do not substitute checkpoints or mix the decoy transfers.
