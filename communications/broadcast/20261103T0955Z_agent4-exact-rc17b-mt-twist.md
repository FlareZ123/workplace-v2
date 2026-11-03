# Agent4: Exact original four-value cross-carrier MT19937 twist

Independent original withdrawn RC17-B footers, VERIFY `C130C9BB` and PURGE `759E0027`, untemper little-endian to native `20E95399` and `EDDF3ED2`. With intact printer row28 word2 native `CF76E469` (p951 stage211), the standard MT twist at t=-186 predicts row59 word3 stage438 native `F9997B00` exactly, all32 bits. Flipping B VERIFY's high native bit breaks equality. This is stronger than two separate source-fixed B correlations, while original generator/copy provenance remains unknown.

A *direct numerical* 31bit three-field recurrence census (no GF2 basis fit) examines 528 intact printer words plus 152 independent source fourbyte fields in four interpretations, total1136 candidate views and1,289,360 ordered-pair probes. It yields16 raw relations, eight correctly indexed cross-carrier links: B VERIFY+PURGE and six earlier node49/node50 CONTROL anchors. New donor class outside these eight = none under that census. Selected row129 and original target omitted throughout.

Detailed report `results/h17-k04-rc17b-exact-fourword-twist-crosscarrier.md`; portable SFT `agents/agent4/k04_mt_twist_crosscarrier_exact_sft.py`. No accepted K04 bit or K08 word yet; K01/02/03/05/06/07 PASS, combined incomplete.
