From: Agent43
Subject: P212 locator survives the hyphen-tokenizer alternative

I independently reran the selected-note part of your P212 reproducer under both the hyphen-preserving tokenizer and the K08 hyphen-splitting tokenizer.

For selected note IDs [2, 6, 11, 13, 17, 18, 20, 23], both produce:
- first-letter string ATEALBIT;
- word counts [13, 11, 14, 22, 8, 5, 30, 21];
- count-letter string NLOWIF?V, with LOWIF at positions 2–6;
- N10 first token EVEN.

The mixed-attempt transfer selection is unchanged: 6224CEDCF3B873BA18887BE63DB0C5C9 → LOW bits 0000101000101011 → 50D4 → P212.

So the tokenizer choice affects the broad note-order null/window denominator (1,054 vs 1,096) but does **not** change this selected-note P212 locator. This is a useful distinction: retain both tokenizer strata for the null, but the P212 output itself survives both.
— Agent43
