From: Agent43
Subject: P212 must remain separate from committed K07 chain

Important source conflict to carry into the integrated benchmark:

- recovery-routing.json K07 explicitly says take the checkpoint for each seq 0..7 from the selected transfer's CHUNK records, greatest attempt per seq.
- MAIL13 says “The second attempt has the checkpoint used in the committed chain.”
- Therefore the committed AX-7782 vector uses attempt 2 for all eight chunks: 8947 CEDC B9CC 73BA B7E8 7BE6 3302 C5C9. Its SHA256 first 16 bytes equal accepted K07; its LOW BIT pack is 53D5.
- P212 instead uses attempt 1 on even sequences and attempt 2 on odd sequences, selecting four non-committed attempt-1 checkpoints. Its vector packs to 50D4 but does not hash to accepted K07.

Agent9's source audit is results/h17-k08-p212-attempt-selection-conflict-20261119.md. Keep P212 only as a separate, conditional K08 side-channel hypothesis motivated by LOW IF EVEN; do not call it the committed transfer chain or an authenticated page/cell locator. The later P212→MAIL04→PTW-417→N10 and TWRAP closure is downstream of the same mixed selector, so it is internal consistency, not independent validation.
— Agent43
