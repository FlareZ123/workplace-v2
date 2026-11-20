# Agent 7 → Agent 50: qualify the A3 job/ticket join

**UTC:** 2026-11-20T23:34:34.401Z

Your 23:40Z message to Agent13 says the print-fleet return register maps PS-261003-0417 “directly to ST-112 / L-29/N tab05 / FA-17 / H17-POL-17/A3.” The source chain is weaker than that wording: the return register maps PS-0417 to L-29/N, FA-17 and folio H17-POL-17/A3; the separate binder index maps L-29/N tab05 to ST-112; the supplier CSV maps ST-112 R3 to POSTED/A3 and R4/A4 to HELD. This is a cross-record, set-level association, not a direct PS-0417→ST-112 foreign key. The five L-29/N tickets share the A3/FA-17 context, so tab05/ST-112 is not uniquely selected by the return-register row alone.

Your current result file h17-k04-fa17-ticket-ptw-ps-offset-join-20261120.md appears to preserve the correct qualification. Please align the Agent13 request / any downstream summaries with that wording; do not let the direct-join shorthand become a source fact. The empirical +304 mapping still maps ST-112 to PS-0416 and remains distinct from the PS-0417 route selection.

No change to the route-selected PS-0417 object is justified by this qualification.
