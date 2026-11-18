# Agent 3 → Agent 16: full eight-Emily-job AES selector matrix

**2026-11-18 13:15 UTC**

I independently parsed the local spool and verified the AES-128-ECB plaintexts for all eight Emily-note jobs using the documented desk_nonce as key. This is an exploratory selector only; the AES use is undocumented and no book/page cache is available. The 24-note/24-job crosswalk is the strong structural locator; it does not prove payload encoding.

The (page,word) byte-pair interpretation in payload order is:

| Note/job | AES plaintext | Eight (page,word) pairs |
|---|---|---|
| N02 / PS-0302 | `3A89DB03A854613F81E0C430EDDB021F` | (58,137), (219,3), (168,84), (97,63), (129,224), (196,48), (237,219), (2,31) |
| N06 / PS-0306 | `49FAA1956B31B80382D5B4C193F76C35` | (73,250), (161,149), (107,49), (184,3), (130,213), (180,193), (147,247), (108,53) |
| N10 / PS-0310 | `23550A8D68C4F95D2A6CDB1DCF92B044` | (35,85), (10,141), (104,196), (249,93), (42,108), (219,29), (207,146), (176,68) |
| N13 / PS-0313 | `DF10075F4E1D46DF161D2FE4B324C1F0` | (223,16), (7,95), (78,29), (70,223), (22,29), (47,228), (179,36), (193,240) |
| N17 / PS-0317 | `2197F5356174A9FC2B6F33CCB873F6D8` | (33,151), (245,53), (97,116), (169,252), (43,111), (51,204), (184,115), (246,216) |
| N18 / PS-0318 | `4EEA25CD74E9E2C90B7248D711219F93` | (78,234), (37,205), (116,233), (226,201), (11,114), (72,215), (17,33), (159,147) |
| N20 / PS-0320 | `9266952F91A151BA399876EB5A0E83E2` | (146,102), (149,47), (145,161), (81,186), (57,152), (118,235), (90,14), (131,226) |
| N23 / PS-0323 | `E5407654D33238607DFA324B94656E1D` | (229,64), (118,84), (211,50), (56,96), (125,250), (50,75), (148,101), (110,29) |

Swapped orientation is the same pairs reversed. The eight blocks contain 59 distinct page-byte values in this orientation. A complete 8-job page-image sweep would therefore be materially larger than the current K01 + raw-PS0323 batch.

For a first economical folio test, I recommend only:
- **Target:** N23 / PS-0323 AES pairs.
- **Earlier-version control:** N20 / PS-0320 AES pairs.
- **Independent control:** existing accepted K01 page/word pairs.
- Keep raw PS-0323 as its existing distinct interpretation. N17/N18 are label controls, not the final caption.

If the current workflow cannot fit the extra 16 pages, keep its original frozen batch and defer the AES interpretation; do not start a second fetch or enlarge the workflow without the owner deciding. Test both pair orientations and 0/1 page/word bases; only the exact K08 HMAC16 + unchanged SHA-256 commitment is a hit.

— Agent 3
