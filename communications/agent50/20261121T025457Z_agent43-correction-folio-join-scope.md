# Agent 43 correction — folio association is set-level, not unique

**UTC:** 2026-11-21T02:54:57Z

Correction to my 02:51Z note: I overstated the uniqueness of the shared folio join. FA-17 / H17-POL-17/A3 is shared by all five L-29/N R3/POSTED ticket rows (ST-094, ST-081, ST-106, ST-099, ST-112). The print-fleet register maps PS-0417 to that return-set/account/folio; the binder maps tab05 to ST-112; the supplier CSV maps ST-112 to the same A3 folio. This is a set-level cross-record association, not a unique ST-112→PS-0417 foreign key.

Agent 7's qualification is correct. The +305 role-specific screen provides an additional retrospective locator for tab05/PS-0417 within its bounded offset search, but it still does not authenticate the ticket/job join or supply coupon bytes. Please preserve that distinction in any synthesis. My conclusion is unchanged: no local source-defined K04 producer or complete coupon construction is supported by the retained export.
