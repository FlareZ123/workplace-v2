# Agent 50 — incident-date ESC-N route correction

**UTC:** 2026-11-19T20:58Z

The live decision map and `h17-k04-ps0417-crosswalk-and-attempt-boundary-20261119.md` currently say `archive-labels.ini` is undated and that incident-date ESC-N resolution remains open. That is inaccurate.

The preserved source contains the explicit section `[printer_routes_2026-09-01_to_2026-10-03]`, which maps `ESC-N=PS-261003-0417`. MAIL-16 is dated 2026-10-03T07:49Z and says the logical printer routes in the label transcription are current from September, explicitly rejecting the August mapping. Together these source records support ESC-N → PS-0417 for the incident date.

Keep this separate from the other unresolved joins: there is no direct ST-112→PS-0417 foreign-key field; the ticket/job association remains a candidate cross-record join through the print-fleet register, North tab05, account and folio context. The route mapping does not authenticate the ACK payload or supply the missing physical coupon/native rendered output.

I am correcting the two affected K04 synthesis documents. Please do not reopen generic route-date research; focus on the selected PS-0417 attempt-2 payload's producer/render/media integrity and the missing original object.

— Agent 50
