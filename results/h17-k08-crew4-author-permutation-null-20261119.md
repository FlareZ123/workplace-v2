# CREW4 → LOW author-permutation control (19 November 2026)

**Status:** exact conditional permutation analysis of the first K08 LOW BIT stage. This is a positive source-structure result, not a full end-to-end benchmark and not a recovered K08 phrase.

Reproducer: [agents/agent9/k08_crew4_author_null.py](../agents/agent9/k08_crew4_author_null.py)

## Source and observed pattern

The source is the hash-pinned 24-record note file:

- SHA-256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- Author counts: Jason 3, Emily 8, Zoey 4, David 3, Gabriel 3, Simon 3.
- First-appearance order: Jason, Emily, Zoey, David, Gabriel, Simon.

Using the same five-bit A=0, LSB-first one-hot author decoder as the existing LOW BIT work, the six outputs are:

| Author | Note positions | Decoded stream |
|---|---|---|
| Jason | 1, 8, 15 | BEQA0 |
| Emily | 2, 6, 10, 13, 17, 18, 20, 23 | **CREW4** |
| Zoey | 3, 9, 16, 21 | EIAB1 |
| David | 4, 11, 19 | IABI0 |
| Gabriel | 5, 14, 24 | QAIA8 |
| Simon | 7, 12, 22 | ACCA2 |

Across the four simple encoding variants A0/A1 × LSB/MSB, only A0_LSB yields exact CREW4 in the observed data.

The terminal 4 selects the fourth first-appearance author, David. David's three note-body word counts, using the existing tokenizer and excluding each note heading, are 11, 14, 22; A=0 maps these to **LOW**.

## Exact conditional permutation null

The null uniformly permutes author labels among the 24 note positions while preserving the six author counts and leaving note bodies fixed.

1. Emily has eight notes. For her one-hot stream to decode exactly CREW4 under the fixed A0_LSB encoding, her labels must occupy exactly the observed eight positions. There are (inom{24}{8}=735{,}471) possible eight-position subsets, so:
   [
   P(\text{exact CREW4})=1/735{,}471.
   ]
2. Conditional on those Emily positions, the remaining 16 positions receive Jason=3, Zoey=4, David=3, Gabriel=3, Simon=3. Of the (inom{16}{3}=560) possible David position sets, seven have chronological word counts 11,14,22.
3. For David to be the fourth first-appearance author, exactly two of the other four non-Emily authors must appear before David's earliest note. Exact combinatorial counting over the remaining label assignments gives:
   [
   P(\text{David fourth and LOW}\mid\text{Emily positions})=9/2080.
   ]
4. The joint event under this fixed-encoding permutation null is therefore:
   [
   P(\text{CREW4, fourth author David, LOW})=1/169{,}975{,}520.
   ]

The actual David positions (4,11,19) are one of the seven LOW triples. This calculation is exact under the stated permutation model; it is not a calibrated p-value.

## Emily's one-row lowering

Emily's original note-head string is ATTALBIT. The existing hypothesis lowers one selected note ID by exactly one row (+1), retaining sorted, unique note IDs. There are **seven valid edits**, not eight: lowering N17 to N18 is excluded because N18 is already selected.

| Lowered note | Resulting heads | Count-letter string | Splice |
|---|---|---|---|
| N02→N03 | STTALBIT | MLZWIF?V | SLZWBIT |
| N06→N07 | APTALBIT | NMZWIF?V | AMZWBIT |
| **N10→N11** | **ATEALBIT** | **NLOWIF?V** | **ALOWBIT** |
| N13→N14 | ATTILBIT | NLZOIF?V | ALZOBIT |
| N18→N19 | ATTALSIT | NLZWIW?V | ALZWSIT |
| N20→N21 | ATTALBPT | NLZWIFKV | ALZWBPT |
| N23→N24 | ATTALBIE | NLZWIF?L | ALZWBIE |

Only N10→N11 yields both ATEALBIT and ALOWBIT. Its ASCII character low bits are 1,0,1,1,0,0,1,0, which pack LSB-first to 0x4D = M. The selected count-letter string NLOWIF?V contains LOWIF, and the first word of N11 is “Even”, supplying the further literal cue LOW IF EVEN.

## Interpretation and limitations

This is substantially stronger than a generic “readable output” claim: the author assignment, first-appearance index, David's LOW count, and the unique valid N10→N11 edit converge under one fixed decoding convention. It should be included in the full K08 specificity assessment as positive evidence for the *early selector chain*.

The numerical null is conditional on the fixed A0_LSB decoder and the observed target word CREW4. It does not correct for searching other group sizes, bit offsets, codebooks, author subsets, word targets, or other post-hoc interpretations. Author positions may also be temporally or editorially clustered, so uniform label permutation is a sensitivity model rather than a claim that authorship is physically random.

This result does not validate the later component, transfer, bookmark, or N20/N23 operations; it does not authenticate the keeper wording; and it does not recover K08. The full source-preserving end-to-end benchmark remains necessary.
