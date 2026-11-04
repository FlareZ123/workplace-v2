# H-17 ZIP DEFLATE payload channel: exact standard-encoder equality

**Agent 35 | 4 November 2026 | Original-source structural hypothesis, negative.** This addresses a specific channel left open by [the attached-ZIP integrity analysis](h17-attached-zip-integrity.md): could the archive's 46 DEFLATE byte streams contain additional encoded information, despite matching the repository's decompressed original-source blobs?

## Hypothesis and frozen input

A steganographic exporter can choose alternative valid DEFLATE encodings for an identical plaintext, leaving extracted files and their Git object IDs unchanged. An alternate compression stream could, in principle, carry hidden K04 coupon bytes or K08 final wording. This is an exploratory **wrapper-channel** hypothesis, not source evidence that such encoding actually occurred.

The original 50,526-byte uploaded `h17-archive-dump.zip` has SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`. The existing ZIP report already audited comments, headers, extra fields, prefix and suffix. This experiment instead independently reads **raw compressed member streams** at each local-file-header offset and reconstructs the deterministic, standard Python/zlib compression of every original decoded member.

## Method and controls

The portable [read-only SFT](../agents/agent35/zip_deflate_original_channel_sft.py) first checks the complete original ZIP fingerprint, local header path and compression type, uncompressed bytes and ZIP CRC32. It reconstructs each non-directory file using `zlib.compressobj(level=6, method=DEFLATED, wbits=-15)`, then compares all compressed bytes exactly against the original local-header stream. Both filenames and compressed lengths are taken from the ZIP metadata, rather than guessed offsets.

As a positive detector control, recompress the original large `spool-reconstruction.log` using raw DEFLATE at **level 1**. The resulting stream remains decompressible to the exact original plaintext yet differs from its stored stream. The SFT must detect this different valid representation and does.

## Measured result

- **46 of 46** non-directory compressed members match the current local zlib **1.3.1** raw DEFLATE level-6 output **byte-for-byte**.
- **10 of 10** directory entries are empty `STORED` records.
- **Zero** member streams deviate from that deterministic encoder. The alternate valid-encoding control is distinguishable.

This rules out additional information encoded by a *deviation from this precise canonical compression representation* within the original ZIP's DEFLATE streams. Since every actual compressed stream matches recompression deterministically, no such deviation remains to decode in the tested wrapper.

**Limits:** the result is conditional on the current zlib 1.3.1 implementation's deterministic level-6 output; equal bytes do not prove the historical packager was zlib or that the extracted source text itself is complete. Ordinary ZIP metadata and prior file-content audits are separate. This analysis does not recover the absent physical K04 coupon or Emily's exact K08 author-final words. The original verifier, archive evidence, commitments and six accepted components remain untouched; **six PASS, K04/K08 MISSING, combined INCOMPLETE**.

**Next-value decision:** this closes a narrowly specified previously untested side channel, rather than supporting further wrapper speculation. Shift compute back to source-derived complete selected-event/revision reconstruction.
