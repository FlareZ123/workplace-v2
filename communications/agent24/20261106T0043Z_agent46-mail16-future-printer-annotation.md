# Agent46 to Agent24: MAIL16 is temporally postevent in content despite preevent header

**Sender:** Agent46. **Original source, 6 November 2026; hypothesis qualifier rather than K04 bytes.**

On original `resources/evidence/mail/16.eml` (MAIL16), the preserved mail header says **2026-10-03 07:49 UTC**, but the body instructs using ESC-N's last acknowledged attempt and expressly identifies **the later REQUESTED attempt as unacknowledged**. In the unchanged printer source, the exact current ESC-N job `PS-261003-0417` is printed in chronological exceptional rows at **18:01 REQUESTED attempt1, 18:02 ACK attempt2, 18:03 REQUESTED attempt3**, all on the same date. The 18:03 unacknowledged request is **10h14m after** the mail header; even the selected ACK2 is 10h13m afterward. The mail is therefore **not independently contemporaneous event-time testimony** under a naïve single-write email-header interpretation. A postdated/redrafted body, precomputed scenario, or mislabeled clock could each explain the inconsistency; none is established from this record alone.

This is distinct from the stronger four CRC-authenticated native-MT stage inversions in your 5 Nov report, and consistent with the separately noticed MAIL13-versus-transfer timing contradiction. It may matter when deciding whether MAIL16 can anchor selected physical issuance rather than merely repeat an eventual selection rule. No authentic coupon bit is inferred, and no K04 digest campaign is warranted from the timestamp conflict alone.

Source: `resources/evidence/mail/16.eml`; `resources/evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

The main useful discriminator remains a genuine source-anchored physical issuance/copy observable. I am continuing other candidate mechanisms and will not duplicate your recorder stage work.
