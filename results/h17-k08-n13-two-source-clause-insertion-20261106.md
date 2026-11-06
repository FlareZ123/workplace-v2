# K08 two independent source-literal insertions into the full Emily N13 desk scene

**Agent 49 | 6 November 2026 | original K08 commitment NO_MATCH on 21,395,178 complete caption assignments.** Six individually accepted REC8/1 components remain PASS; K04/K08 missing, combined INCOMPLETE.

## New exact editor model

Emily's N13 writes the entire 22-word retrospective scene, beginning \`at the end of the night\` and closing at the lamp. Her N20 says the eventual line needed the sea, end of night and voices at the table. N13 itself supplies the night, mugs, window and lamp but lacks explicit sea/water and voices/table passages. This suggests a concrete *additive editor*: preserve every N13 original word, then splice in two source-derived multiword expressions, one describing sea/water/outside and one describing company/voices/table.

This is distinct from the 3,086,541,640-candidate N13 subset-and-**one-word** insertion experiment, its all-length pure-deletion complement, and Agent49's earlier two-role **replacement** editors. Here **all 22 N13 words remain in their original order**, with *two* added length-2..8 spans. The historical final edit has no direct surviving witness; this is a speculative complete-candidate construction and not a claim about the original keeper's actual drafting process.

Read the original source \`resources/evidence/crew/noticeboard-and-desk-notes.txt\` (SHA256 \`13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb\`) and MAIL11/12 without modifying them. Extract lowercased normalized contiguous 2..8-word spans from N01, N08, N14, N20 and MAIL11 if they contain one of \`sea/water/outside/horizon\`; these form **171 distinct environmental spans**. Extract the equivalent 2..8-word spans from N02, N03, N09, N11, N19, N20, MAIL11 and MAIL12 if they contain one of \`voices/table/people/room/somebody/mugs/cup/hands\`; these form **331 distinct social spans**. Spans may carry the original note/paragraph framing; the test is over source-literal normalized tokens, not manually rewritten topical prose.

For each of seven N13 scene-boundary offsets **6, 8, 12, 14, 16, 21, 22** (after the time opener, mugs, window, somebody, remembered, lamp or full caption), insert the sea span at one boundary and the social span at a *different* one. Each insertion has one of three literal prefixes: empty, \`and\`, or \`with\`. Source word order in the full original N13 base is preserved. Do not add punctuation or extra trailing whitespace. The fully determined grammar has exactly

\`171 × 331 × 7 × 6 × 3 × 3 = 21,395,178\` complete **assignments**. Duplicates across assignments are possible, and no global unique-normalized-string count is claimed.

For every complete candidate, compute the original K08 rule: HMAC-SHA256 with the unchanged 16-byte desk nonce \`5F933DA6A1BD03C32DA5CBC25344F497\`, truncate to 16 bytes, SHA256 those exact 16 bytes, compare all 32 digest bytes with the unchanged original K08 commitment \`285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747\`.

## Executed complete original result

Executed source-pinned portable C++17/OpenSSL [single-file SFT](../agents/agent49/k08_n13_two_source_clause_insertion_sft.cpp) locally over an exact extraction from the attached original ZIP. One sea-insertion-position shard per offset, each covering exactly \`171 × 331 × 6 × 9 = 3,056,454\` complete assignments. The seven tested offsets were **6, 8, 12, 14, 16, 21, 22**. All seven completed and independently reported **\`original_hits=0\`**, yielding **21,395,178 full original K08 negatives**, and no run timed out after sharding. Each shard took 5.1..6.3 seconds locally.

Controls: original crew source SHA256 asserted; 24 original N records and exact N13 opener/22-word count asserted; independently known original N02 HMAC16 \`BF889359B0303F2B2B2FD96AE841210B\` reproduced; **seven distinct precomputed synthetic full-caption commitment positives** tested (one per shard) and recovered exactly once. The seven planted digests were computed separately with Python's native \`hmac\` and \`hashlib\`, before reexecuting the C++ shards. The final code corrects an intermediate trailing-space issue for end-boundary inserts; all final counts and negatives are from the corrected code.

This is **not a proof that the terminal caption was unmodified N13, nor a recovery of exact keeper words**. The final may delete or reorder N13, choose newly written words, insert a third passage, use another desk draft, or have a wholly different authored form. This test makes a real finite negative claim only for the specified two-addition version mechanism.

**Unchanged project status:** K01/K02/K03/K05/K06/K07 individually PASS; K04's selected physical coupon and K08's author-final caption remain unresolved, combined REC8/1 INCOMPLETE. No original source, acceptance file, original verifier or canonical candidate was changed. No automatic CI was created.
