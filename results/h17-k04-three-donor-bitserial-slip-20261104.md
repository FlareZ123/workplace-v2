# H-17 K04: bit-serial slip across three preserved original 0417 coupons

**Agent 3, 4 November 2026 | original K04 commitment NO_MATCH.** This is a source-only, complete-coupon model with an altered serializer architecture. It differs from the earlier [same-bit-position affine donor model](h17-k04-0417-bitplane-affine-whole-coupon-20261104.md) because it allows one-bit position shifts within each source byte. The original note N22's comparison of a label printer to a fax machine motivates investigating serial bit alignment; the note is **not a source-verified fault diagnosis**.

## Exact event sources and model

Retained packets for the selected 0417 job, all **excluding the unauthenticated 18:02 ACK2 copied payload**, are original 16:45 LABEL ACK `E1E60D5F6B6DD2225FA6D5A2A63AD932`, 18:01 RECOVER REQUESTED1 `CD3E4F216ADB2FB180DA2AA90B33F7A4`, and 18:03 RECOVER REQUESTED3 `44D53DFC29D7943A95D89371DA58EC64`.

For each output byte bit position 0..7, independently select **one of three** source packets and **one of three** within-byte source bit offsets (−1, 0, +1 modulo eight). The chosen bit source is fixed across the 16 byte positions of the complete packet; assemble eight bitplanes to obtain the 16byte hypothetical printer coupon. Each plane has exactly nine distinct 16bit original-source choices, asserted by the SFT. XOR the unchanged K04 source route mask and check complete SHA256 against the original target. Exact corpus size is `9^8 = 43,046,721` 16byte candidate components. This can introduce bit positions absent from any corresponding-bit donor, which the previous 16^8 affine XOR-selected-same-bit class cannot represent.

The source-pinned [single C/OpenSSL reproducer](../agents/agent3/k04_bitplane_serdes_slip_sft.c) includes the sibling source-gated [affine packet library](../agents/agent3/k04_bitplane_affine_sft.c). It asserts original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, route and acceptance original checksums, exact three intact source buffers, and SHA256 compression equivalence. A separately planted full 16byte bit-shifted coupon code 20261104 is recovered **exactly once**, confirming complete coverage and digest checking. Read-only compiled original export execution:

```
SOURCE_PINNED bitplane_3donor_three_bitshifts candidates=43046721 original_hits=0 planted_positive=1
```

No original K04 SHA256 match was detected. No genuine physical coupon bit was authenticated, and K08 wording is untouched. This excludes only this specified independent per-bitplane donor and circular −1/0/+1 bit-slip model. Larger shifts, per-byte independent selection, correlated wire faults, or a different generator remain outside scope. Archive state: K01,K02,K03,K05,K06,K07 individually accepted, K04/K08 missing, combined incomplete. No official source, verifier, acceptance or candidate edited.
