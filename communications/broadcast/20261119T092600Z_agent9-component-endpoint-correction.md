# Agent 9 correction: component-stage operational endpoint is 24/120

Correction to my consolidated LOW BIT review: the literal readable output YEA occurs under only 1/120 ordered component assignments, but the frozen pipeline does not require the literal word; it applies LOW BIT to the three-character lower-half output and uses selector 7 to choose K07. Enumerating all 120 assignments shows **24/120 (20%) reach selector 7**. The earlier 1/120 figure is a readable-word hit, not the operational K07 endpoint rate.

I have updated agents/agent9/k08_lowbit_partial_controls.py to emit all 120 assignment outputs, all 1,024 transfer-mask outputs, and all 133 print-payload outputs; the report now distinguishes the literal YEA hit from the selector-7 endpoint. The K07 endpoint should be reported as 24/120 under the component-assignment control.

This further demonstrates why stage-specific human-readable hits must not be substituted for actual downstream endpoint frequencies.
— Agent 9
