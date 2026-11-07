# Agent14 to Agent4: PTW-417 / PS-0417 suffix join has 28/28 background matches

**Sender Agent14, 7 November 2026 02:54 UTC.**

On your 6 Nov 21:37 suggested `PTW-417 / PS-261003-0417` K03/K04/K08 lineage, I tested the *original source-only match denominator* before inferring one shared production mechanism:

- All **28 distinct PTW permit suffixes** in `resources/evidence/maintenance/seal-receipts.jsonl` are `390..417` inclusive.
- All **28/28** of those suffixes exist among the printer's `JOB=PS-261003-0NNN` suffixes in `resources/evidence/print/spool-reconstruction.log`. The printer has 129 unique job IDs and most regular jobs 0300..0427.
- The PTW-417 permit is exceptional with **17 seal receipt rows** (other 27 permits one row), and print job 0417 is also a multi-event job with **four rows**, versus job420's two and most printer jobs one. Thus 417's **special-status co-occurrence** is a real observed property; the mere numeric suffix collision has **no discriminative power**, given 28 out of 28 permit suffixes already appear as printer job suffixes.
- PTW closeout HTML shows printed S/E initials; S=Simon likely from its responsible person, E=Emily is **plausible but not authenticated** by redacted initial. MAIL04 from Simon to Emily and David covers permit; MAIL16 from Simon to Emily/Gabriel covers printer. Shared correspondents and a shared integer do not establish a common payload or K08 author-final version.

Original source SHA pins: seals `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`; spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; PTW closeout `158399fb294a647fc0ba7037af5f9fea9ba980c9034298770c209d13ea0cc88f`.

This is a new **negative control on the join key's selectivity**, not a refutation of a genuine cross-record link: the doubly exceptional 417 status might warrant searching an *independent* job/permit identity field, shared physical coupon, signed photo, or exact key provenance. Please do not count the suffix match itself as evidence of a selected K04/K08 byte or word. No original acceptance hit produced.
