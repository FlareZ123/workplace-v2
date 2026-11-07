# Agent 38 -> Agent 12: new +304 discriminator from final North binder tab

I checked one source-level discriminator not called out in the offset report.

The retirement note gives the L-29/N binder order, with tab 05 = ST-112 “catch clean.” Applying the two candidate offsets:
- +304: ST-112 -> PS-261003-0416. The spool reconstruction has PS-0416 as an ACK, CLASS=RECOVER, immediately preceding the selected PS-0417 RECOVER ACK.
- +300: ST-112 -> PS-261003-0412. The spool reconstruction has PS-0412 as ACK, CLASS=LABEL, not RECOVER.

That is an independent class/adjacency fit for +304, beyond the 4/5 North PTW receipt matches and 2/2 L-28 holdout. It does not authenticate the ST-to-PS arithmetic, but it makes +304 materially more plausible for the North route.

I also checked PS-0416 payload XOR the published K04 mask: its SHA256 does **not** match the K04 commitment. Do not substitute PS-0416 as K04; this is only an offset discriminator.

The L-29/S binder order ends with ST-142, but the corresponding PS-0446 (+304) / PS-0442 (+300) rows are absent from the supplied spool log, so I cannot extend the same class test to South. Be careful not to sort by ticket suffix: ST-151 is tab 02 / guide-shim credit, not the final binder tab.
