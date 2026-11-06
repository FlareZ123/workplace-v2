# H-17 K04: original archive Base64-decoded coupon/mask carriers

**Agent10 | 6 November 2026. Source-only encoded physical-carrier test. K04 remains missing.**

## Why this is distinct

Previous source-wide K04 scans exhausted **verbatim raw 16-byte windows and literal 32-character hex windows** as candidate coupons or alternative masks. Agent8 separately searched conventional Base64 as a transport for *printable K08 captions* and found none, but a 16-byte binary printer coupon or mask would decode into mostly arbitrary, nonprintable bytes and escape its K08 text extraction. We test that missing binary transport class.

The original archive source ZIP SHA256 is `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`. No generated files were added to the ZIP. Source-selected K04 uses the unchanged mask `8556C8CB6140A7F9A5123AC7571BEE1C`, copied disputed ACK2 `A9A9DC5731A5E2AE879C47215C2559D5`, and original target `SHA256(K04)=930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Complete transport hypothesis and executed result

For each of all 46 original ZIP members, locate every maximal ASCII Base64-looking run of at least 22 symbols, with standard Base64 alphabet and up to two trailing padding characters. Attempt all four starting-symbol phases, enforcing valid Base64 decoding after padding normalization. For each resulting decoded binary stream, extract *every contiguous complete 16-byte window*. Dedupe full decoded carrier bytes across all original files.

Test three complete K04 component interpretations for each decoded 16byte source carrier `C`:
`C XOR original_mask` (paper coupon);
`copied_ACK2 XOR C` (alternative mask);
`C` (already reduced component).
Compare full SHA256 in every case to the untouched original acceptance commitment.

| Original-data count | Exact result |
| --- | ---: |
| ZIP members inspected | 46 |
| Base64-shaped source runs | 183 |
| Invalid shifted-decoding phases | 173 |
| Distinct decoded binary 16byte carriers | **5,753** |
| Complete K04 assignments checked | **17,259** |
| Original K04 commitment matches | **0** |

One independently planted 16byte coupon was Base64-encoded into a synthetic in-memory source line, recovered by the same run scanner, XOR-masked, and found uniquely by a synthetic target commitment. This validates the complete transport and target arithmetic without changing the official hash.

[Reproducible source-pinned Python SFT](../agents/agent10/k04_original_base64_carriers_sft.py) takes the exact original ZIP path as its optional argument. Executed against the supplied 46-member ZIP and produced the counts above.

## Evidence boundary

The decoded source binary does not contain the true K04 coupon or an alternative route mask *under this standard, contiguous Base64 carrier hypothesis*. The source does not attest Base64 as the actual printer transport, and the result does not eliminate custom encodings, fragmented copies, off-export physical records, or an unrelated actual printer producer. No original physical coupon bit or final Emily K08 word was recovered. The six accepted original components are unchanged; combined REC8/1 remains INCOMPLETE.