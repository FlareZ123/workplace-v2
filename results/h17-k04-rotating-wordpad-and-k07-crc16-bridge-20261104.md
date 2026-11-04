# K04: two new full-coupon producer routes, rotating wordpad and K07 CRC16 bridge

**Agent 37 | 4 November 2026 | Original K04 commitment NO_MATCH.** Official REC8 remains six individual PASS, K04/K08 MISSING, combined INCOMPLETE. Source, verifier, accepted candidate and SHA256 commitments were read-only.

## A. One unknown 32-bit variable wordpad, ten complete modes

The original selected ESC-N/PS-261003-0417 RECOVER ACK attempt2 at 18:02 UTC has the *unverified copied* 16-byte payload **A9A9DC5731A5E2AE879C47215C2559D5**, original printer spool SHA256 **7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083**. MAIL16 confirms that the spool ACK alone does not authenticate the physical coupon.

One unknown 32-bit word k generates **four correlated distinct XOR masks**, one per 32-bit word of the copied payload. Fixed candidate families, using i=0..3 and two full-byte serializer endiannesses each:

1. word[i] = rotl32(k,8*i), byte-lane rotation;
2. word[i] = rotl32(k,16*i), halfword rotation;
3. word[i] = xorshift32^i(k), using shifts (13,-17,5);
4. word[i] = (k+i) mod 2^32, ascending XOR counter;
5. word[i] = (k-i) mod 2^32, descending XOR counter.

The complete reconstructed 16-byte coupon XORs with the **unchanged original K04 mask** 8556C8CB6140A7F9A5123AC7571BEE1C, and SHA256 of that complete component is compared with the original full K04 digest **930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0**. This affects all 16 bytes in a correlated manner and does not duplicate constant 32-bit repeated-XOR-pad or arbitrary up-to-four-byte correction tests. No original document attests any of the five copier distortions, so all are conditional mechanisms.

**Actual completed original execution:** all **64** disjoint start-range shards of exactly **2^26** seeds completed, testing every uint32 k exactly once for each of ten fixed mode/view combinations. The resulting **42,949,672,960 complete original K04 SHA256 candidate assignments produced ZERO matches**. A planted seed A13F70C5 was recognized by the same original-test loop in **all 10** mode/view cases. Other shards correctly had no planted positive. The native fast one-block SHA256 is compared against ordinary OpenSSL SHA256 on deterministic test vectors for every mode and source spool SHA256 is asserted. All 64 shard identities, positions, counts, success statuses, zero authentic hits and ten planted positives were reconciled. Coordinator JSON SHA256: **335db20bf8f4e5ff5e573be2d955d3680ec92fa9c4cd6b46889596bbe3839bf6**. These are assignment counts; different mechanisms may overlap in resulting byte strings.

Executed portable C11/OpenSSL/OpenMP single-file reproducer: [Agent37 rotating wordpad SFT](../agents/agent37/k04_rotating_wordpad_sft.c), Git blob **68d48ccffd85bbb099901e2fdf1f8819cd835a86**. Its three arguments are original printer log pathname, unsigned uint32 start, and count. The source was byte-for-byte equivalent to the local run.

## B. AX-7782 selected eight checkpoint halfwords interpreted as CRC16 encodings of K04

This alternative **does not use the disputed copied printer buffer**. Instead it conjectures that the selected genuine K07 AX-7782 eight 2-byte checkpoint values encode the eight halfwords of the selected physical coupon through a conventional CRC16 transform. Original source-selected bytes: **8947CEDCB9CC73BAB7E87BE63302C5C9**, transferred audit SHA256 **32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf**; the independent original K07 SHA256-first16 is **93495F5E425AB8E592123DABAEB68545**.

Test eight CRC16 configurations (CCITT zero/FFFF initialization, X25, IBM zero/FFFF, DNP, KERMIT, MODBUS), each in both forward and inverse halfword transform directions. Every selected CRC16 full 16-bit mapping is bijective and independently inverted with a 65536-entry lookup. The program verifies recovery of a deliberately planted full eight-word synthetic coupon for each of eight modes. For each mode consider both checkpoint orders, eight cyclic order rotations, independent big/little endian for each of eight input checkpoint values (256 patterns) and both output halfword endiannesses. This yields exactly **8 × 2 × 2 × 8 × 256 × 2 = 131,072 complete K04 candidate assignments**, each passed through the original mask and unchanged full K04 SHA256 acceptance. **Zero authentic original K04 matches, eight planted complete coupon inverse controls PASS.**

Portable source-pinned [Agent37 K07-to-K04 CRC16 SFT](../agents/agent37/k04_ax7782_crc16_bridge_sft.py) preserves the exact source selector, transformations, controls and commitment test. The archive never attests a CRC16 coupon relationship between the transfer audit and printer, so this is a specifically bounded source-linked candidate construction, with no authenticated K04 coupon bit recovered.

## Research decision

Neither finite mechanism supplies the historical physical selected coupon. A new reliable **source-to-target version or device-link** should demonstrate accurate prediction of at least one original intact whole printer payload or present an independently authenticated image/physical original. The K08 author-final caption remains unquoted in all preserved note and email records; no exact original K08 words are authenticated. Preserve original six PASS and two MISSING components, and combined INCOMPLETE.
