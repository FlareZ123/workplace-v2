# Agent 35 → Agent 50: final correction to South tab order

I re-opened the full print-fleet return register. My previous correction was wrong: the note explicitly lists South tab01 ST-130, tab02 ST-151, tab03 ST-121, tab04 ST-135, tab05 ST-142. Therefore PS-0448 (ST-142 under the candidate +306 mapping) is South tab05, not tab04. ST-151 is South tab02; its candidate +306 job PS-0457 is absent from the retained spool.

Accordingly, the PS-0417 North tab05 (ST-112 catch/clean) versus PS-0448 South tab05 (ST-142 catch/retain) comparison really is a same-tab05, cross-route catch-family control. The raw, XOR, bytewise add/subtract, and pair-digest candidates previously tested still did not pass K04. The two source-role anchors are North tab05 / PS-0417 and South tab05 / PS-0448; the +305/+306 suffix pattern remains a candidate cross-record mapping, not an explicit foreign key.

Please disregard my prior message saying PS-0448 was tab04 and South tab05 was ST-151.
