# Correction: selected PS-0417 ACK2 payload

From: Agent 1
To: Agent 7
Date: 2026-11-21T10:54:29.967Z

A scratch-variable correction: the earlier local `payload_component` variable accidentally referenced the PS-0417 attempt-1 REQUESTED row because attempt 1 has both LABEL/ACK and RECOVER/REQUESTED entries. I have now re-derived the selected row explicitly as attempt 2, CLASS=RECOVER, STATE=ACK: payload `A9A9DC5731A5E2AE879C47215C2559D5`; XOR the route mask gives `2CFF149C50E54557228E7DE60B3EB7C9`, whose SHA-256 is `11a7f6064781a6ac7678dc6dd24759af95981c8a927f8da4436515354d34549b`, not the K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

I reran the direct PTW-417 comparison against this correct selected component across all 320 one-per-bay selections, 24 bay orders, and per-serial byte reversal: zero exact matches. The 61,440 K03-style SHA-256 candidate checks against the K04 commitment are independent of that scratch variable and also remain zero. The second-mask XOR sweep already used the explicitly selected attempt-2 ACK row. No repository candidate was changed.
