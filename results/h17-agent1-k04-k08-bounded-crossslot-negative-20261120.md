# Bounded K04/K08 cross-slot tests (Agent 1, 2026-11-20)

**Disposition: no recovery candidate found.** These tests close only the specific derivation families below; they do not prove that the archive is unsolvable. K04 and K08 remain unverified.

## K04: spool retry and cross-record candidates

Source: the local export's print spool reconstruction log, route mask, acceptance commitments, and the six accepted components in the repository's candidate record.

The relevant spool values were:

- PS-0417 attempt 1 / REQUESTED: `CD3E4F216ADB2FB180DA2AA90B33F7A4`
- PS-0417 attempt 2 / ACK: `A9A9DC5731A5E2AE879C47215C2559D5`
- PS-0417 attempt 3 / REQUESTED: `44D53DFC29D7943A95D89371DA58EC64`
- PS-0420 attempt 1 / ACK: `31C9714DD36DB2677BB9006670A9DFFD`
- PS-0420 attempt 2 / ACK: `432475F72A62DB39F3D5693E2C937FA4`
- PS-0323 / RECOVER: `1E51EFD2E5CA8F4E1FC8B49297B3D74F`
- route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`

Tested:
- Each named attempt payload directly and XORed with the route mask.
- PS-0417 pairwise and three-way XOR combinations, with and without the mask; bitwise majority, AND, and OR; all 256 possible 3-input bitwise Boolean functions with and without the mask.
- All 134 payload rows in the spool log, including direct, masked, reversed, and reversed-plus-masked values.
- Natural XOR aggregates grouped by class, state, destination, and combinations of those fields.
- PS-0323 payload XOR every subset of K01, K02, K03, K05, K06, K07, the route mask, and the desk nonce (256 subsets).

**Result:** none of the resulting 16-byte values matched the K04 acceptance commitment. The tested operations do not recover the coupon. The native SPL/SHD and rendered job output remain absent; do not claim that the spool payload is the coupon merely because PS-0417 attempt 2 is acknowledged.

## K04: BX25-08 PDF encryption internals

The local BX25-08 PDF opens with password `8131` and uses AES-256 PDF encryption (revision 6). Tested the trailer IDs, the 16-byte encrypted /Perms block and its AES-256-decrypted plaintext, the 32-byte file-key halves and their XOR, and simple 16-byte hashes of the PDF key, IDs, and permission block.

**Result:** no tested 16-byte value matched K04. The PDF's valid /Perms plaintext is a PDF permissions structure, not a recovered coupon. Do not treat the PDF encryption key as the K04 component without new source evidence.

## K08: bounded cross-slot tests

- BIP39 mnemonics derived from the accepted K02, K03, K05, and K06 components did not match the K08 HMAC commitment. Existing work already covered K01/K07 and spool-payload entropy.
- The four RC-17 D-draft footer strips were tested in all 24 orders against K04 and K08; C/D vector permutations and D/C XOR combinations were also tested. No match. The all-D-draft low-bit output `BT` remains an exploratory two-character fragment, not an authenticated selector.
- First/terminal-letter streams from N20/N23 and the selected Emily note bodies did not match K08.
- A small source-motivated set of SEAT/SEATS/table, alone/next-watch, and sea/watch candidate phrases did not match K08. Stop semantic phrase guessing; the authoritative current path remains the missing N23 margin or the native/rendered PS-0323 output.

## L29 revision-pair check

The L29 docket has three visible revision pairs: ST-099 R2/R3, ST-121 R2/R3, and ST-112 R3/R4. Applying the K05-inspired “lower on even page suffix / higher on odd page suffix” rule selects R3 in all three cases. This is not an independent selector: it collapses to the already visible posted revision and does not establish that the K05 operator belongs to L29.

MD5 and SHA-256-truncated-16 checks of the R3-posted rows, plus little-/big-endian amount-cents vectors, did not match K04. No useful K04/K08 derivation emerged. Do not extend this into arbitrary CSV encodings.

## Research consequence

The bounded alternatives above are closed. The missing original profile-refresh package, mug-stock workbook, N23 margin, and native print-spool/rendered output were not found in the local export, repository branches/private placeholder, or the checked Actions artifacts. This does not authorize protected-system access or another custodian request.

Future work should prioritize a genuinely new, source-authenticated closed-export mechanism. Do not repeat the tested retry/XOR/Boolean families, PDF-key path, BIP39 component path, L29 parity selection, or semantic phrase guesses. Keep K04 and K08 marked unresolved until their exact acceptance commitments pass.
