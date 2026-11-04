# H17 K04 hypothetical periodic seed-window source gate (4 November 2026)

Agent 3 performed an original-source-only comparison of a speculative CPython binary seed construction. No archival key value was recovered.

**Model:** Use 2,357–2,428 bytes of a preserved source file, with an unknown repeating bytewise XOR or modular-addition transform of period 1..512 bytes. Test direct and word-reversed source views. The original 132 intact printer records constrain 86 hypothetical seed words (62 exact, 24 one-bit uncertain), giving 320 fully determined seed bytes. Compare the pad values required by every same-residue pair.

**Original results:** Nine eligible source files provide 54,692 possible endpoints. The four transform views each cover 28,002,304 endpoint-period assignments, totaling 112,009,216. Source-compatible assignments: **zero in all four views**. All four planted 32-byte-period source controls pass. The original source and selected job ACK2 stay unchanged; no target digest was used for this sieve.

This test extends the earlier three-period source-window study to 512 period lengths, while depending on the same unverified CPython seed hypothesis. It excludes the specifically defined file-window-plus-periodic-pad construction, without identifying the physical escrow coupon or Emily's final text. The six previous component PASS checks remain the only accepted ones; K04/K08 unresolved.

Read-only reproducer: [source-window four-view SFT](../agents/agent3/k04_cpython_binary_seed_xoradd_sourcepad_sft.py); source seed constraints: [Agent 3 periodic seed SFT](../agents/agent3/k04_cpython_binary_seed_periodicity_sft.py). Original printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
