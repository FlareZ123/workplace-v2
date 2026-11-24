# Agent 5: K08 workbook intake security and M10 scope update

I found that `work/h17_k08_mug_stock_cell_selector.py` printed the PS-0323 ciphertext/plaintext, desk nonce, K08 target digest, selected cell values, candidate phrases, HMACs and comment-author identity. That is not safe for a public repository or CI logs.

The default `inspect_workbook(...)`, CLI stdout and `--json-out` are now redacted. Raw results require an explicit in-process `reveal=True` for authorized local analysis; never log or publish that result. The literal PS-0323 ciphertext/plaintext were removed from the public source; the computed plaintext is checked against a SHA-256 fingerprint.

The bounded comment path now checks only exact `M10<comment>` streams on all listed worksheets when no sheet is selected. Cell-value candidates on multi-sheet workbooks still require an explicit `--sheet`; no worksheet order or broad comment search is inferred. Comment-author identity is redacted in public output.

The focused regression now includes all-sheet M10 and redaction tests. Workflow run 45456449793 completed successfully. This is a security/intake correction only; no K08 phrase or component was recovered.