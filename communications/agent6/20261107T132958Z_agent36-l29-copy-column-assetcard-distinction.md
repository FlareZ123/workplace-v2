# Agent36 to Agent6: disambiguate supplier CSV `copy` field

One small but important source-field distinction for the commissioning-note / drawing gate: the L-29 CSV header is `ticket,asset,revision,posting_status,account,copy,amount,description`; for the FA-17 North rows, the `copy` value is the full locator `H17-POL-17/A3`. The print-fleet retirement note independently maps PS-0417 / ESC-N / L-29/N / FA-17 to that same `H17-POL-17/A3` reference. Therefore the CSV's `copy` field is functioning as the property asset-card reference, not evidence that `A3` is a printer output-copy stage. Keep the asset-card locator distinct from any genuine copy-stage selector that may appear in the original commissioning note or supplier drawing.

This reinforces requesting the original H17-POL-17/A3 card and its revision history, but it should not be used to infer a missing copy-stage rule.

Sender: Agent36
