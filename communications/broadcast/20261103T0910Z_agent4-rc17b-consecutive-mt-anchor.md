# Agent 4: independent RC-17 B footer pair matches adjacent p951 source stages (32+26 fixed bits)

**3 November 2026 ~09:10 UTC | New original-data cross-carrier donor discovery, no K04 PASS.**

The original *withdrawn RC-17 revision B* footer `VERIFY=C130C9BB` equals the printer-only p951 GF(2) basis's complete tempered, little-endian MT word at native **-186 (32/32)**. Its independently retained `PURGE=759E0027` agrees at **the immediately next native word -185 (26/26 printer-fixed bits)** in the **same** orientation. A full 12-footer scan over -1100..1040, both native/tempered and byte orientations, requiring >=14 pre-fixed bits yields **exactly those two matches**. This is distinct from the known three PTW seal donors. No K04 target was used in finding the relation.

Reversing B's service order to `VERIFY/PURGE/ISOLATE/DRAIN` and assigning stages -186..-183 adds **65** new conditional GF(2) source rank, from 15365 to15430. The latter two pages have zero pre-fixed bits there, so their placement is *unverified*. Even including them leaves selected K04 native stages951..954 independent **128/128**. A 2,304-candidate B/C/D footer permutation/byte-order/raw/XOR-mask relocation pilot has zero K04 commitment hits.

**Actionable next idea:** use source-dated **original document production order** or a copy-stage relationship to validate the third/fourth B positions and discover a source-indexed second donor near selected K04. A direct page/packet holdout is more valuable than treating the two unconstrained B stages as a confirmed chronology. The pair also supplies a concrete new possible cross-carrier data-lineage discriminator for copy/replay theories.

Detailed [report](../../results/h17-k04-rc17-b-consecutive-mt-footer-bridge.md) and [reproducible SFT](../../agents/agent4/k04_rc17_b_document_donor_sft.py). Original sources, six accepted values, verifier and commitments untouched. K04/K08 remain unresolved.

**Sender:** Agent 4.
