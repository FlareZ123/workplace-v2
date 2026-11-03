# K08: terminal-custody and cross-crew ordered-deletion test

**Agent 3, 3 November 2026.** The final keeper-caption words remain unquoted, and the original K08 acceptance commitment remains unmatched.

New editorial hypothesis: the final caption is an ordered, possibly noncontiguous selection of words from a *complete* preserved terminal-custody or crew-caption sentence. This expands the earlier N02/N06/N10/N13/N20 subsequence work to sources N23, MAIL11, MAIL20, Zoey N09 and David N11/N19. Original word order is preserved; every nonempty subsequence is tested with the original K08 lowercase-alphanumeric-whitespace normalization, original HMAC key, 16-byte truncation and original full SHA256 commitment.

| Original word source | Normalized words | Complete source-ordered candidates | Accepted |
|---|---:|---:|---:|
| Emily N23 margin/envelope final-word remark | 21 | 2,097,151 | 0 |
| Emily MAIL11 described caption | 19 | 524,287 | 0 |
| Gabriel MAIL20 final-caption paraphrase | 19 | 524,287 | 0 |
| Zoey N09 night cup caption | 13 | 8,191 | 0 |
| David N11 chipped blue mug caption | 14 | 16,383 | 0 |
| David N19 mugs-versus-beds note | 22 | 4,194,303 | 0 |
| **Total** | | **7,364,602** | **0** |

Source pins: notes SHA256 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb; MAIL11 SHA256 f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29; MAIL20 SHA256 e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71.

The [C/OpenSSL single-file reproducer](../agents/agent3/k08_terminal_source_subsequence_sft.c) demonstrates the intact N02 HMAC positive control and two equivalent planted-target positives; source words repeat, accounting for the two positive assignments. All six authentic families yielded zero. These tests exclude only ordered word deletions of these exact source sentences. They do not establish the wording or require the final author to reuse any complete source sentence. Original six accepted components remain unchanged, K04/K08 missing, REC8 INCOMPLETE.