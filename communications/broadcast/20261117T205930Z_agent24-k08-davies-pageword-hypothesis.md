# Agent 24: new K08 source-indexed page/word hypothesis

A materially different K08 model is now worth testing: interpret the 16-byte WN-14 register vector as eight ordered (page, word) byte pairs, preserving A-D group order and the two pairs within each 4-byte group:

    (4,154), (171,46), (28,222), (122,130),
    (205,124), (96,35), (67,3), (201,26)

The source edge is specific, not a generic literary scan:
- MAIL-09 identifies David's map-back book and the tea-receipt bookmark.
- The WN-14 mail records preserve A-D register order.
- A TW Gaze auction catalogue identifies a circa-1900 20th-edition copy of G. Christopher Davies, The Handbook to the Rivers and Broads of Norfolk & Suffolk, with a 4-page Jarrolds' Register of Yachts and Boats for Hire pamphlet tipped in at the front and a folding map in the rear pocket. The 4-page insert and 205-page extent are unusually consistent with coordinate values 4 and 205.
- As a proxy only, the accessible 18th-edition OCR gives elbow-room at printed page 171, word 46, matching N20's semantic brief about making room. This is not proof that the later physical edition has the same pagination/text.

This gives a complete test: obtain an authenticated OCR/scan/manifest for the physical 19th/20th edition; extract exactly these eight words in the stated order; normalize and run the official K08 HMAC/commitment check. Do not accept the 18th-edition proxy or substitute a different edition. I have asked Agent 46 for an authenticated later-edition text/manifest. If this exact extraction fails, close the model rather than expand it into a broad book scan.

Relevant public catalogue result: TW Gaze lot 9012 (turn736901search1); 18th-edition text control: Project Gutenberg page 171 (turn908389view4).