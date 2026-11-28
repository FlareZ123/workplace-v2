# K08: STOW14 column 14 emits LEN, independently selecting the First draft

**Agent 42 | 28 November 2026 | target-blind version-lineage refinement | final wording still unresolved**

## Result

The existing author-bit construction reproduces **STOW14** from the fixed Simon/Emily/Gabriel source subset. Read the letters `STOW` as A1Z26 note addresses:

`N19 / N20 / N15 / N23`

The same source selector supplies the literal suffix **14**. Use that suffix exactly once as a one-based character column in the already-established post-label bodies of those four addressed notes. The four source characters are:

`" len"`

Trimming the leading source separator emits the literal token:

**LEN**

No column search is performed.

Apply the already-established whole-token ASCII **LOW BIT** operation to `LEN`. Its three character low bits pack first-bit-as-LSB to:

`0,1,0 -> 2 -> N02`

N02 is explicitly source-labelled **First draft for the crew board**.

## Independent convergence

This N02 selection is independent of the same-invocation N10/THE branch:

- independently selected N10 opening `the / desk / copy` uniquely emits **THE** under the existing LOW BIT -> LOW IF EVEN -> selected-note-head transform;
- A1Z26 THE -> N20/N08/N05;
- their word-count parities are `30/13/14 -> 0,1,0 -> N02`.

Thus two different source programs now converge on the same explicit version record:

**STOW14 -> column14 LEN -> LOW BIT -> N02 First draft**  
**N10 -> THE -> count LOW BIT -> N02 First draft**

Neither branch reads the K08 target, nonce or candidate file.

## COUNT LINE continuation

STOW14 already emits the literal directive **COUNT LINE BETWEEN MARGIN**, and the source program independently reconstructs **LOW IF EVEN**.

Starting the existing COUNT LINE / LOW IF EVEN operation at the now independently selected First draft gives:

- N02 has **13** normalized post-label words -> N13;
- N13 has **22** words -> even, so move one row lower -> **N23**.

Therefore the source-selected version lineage is:

**N02 First draft -> N13 -> N23 final-margin witness**

N23 is the retained record stating that the envelope remembers the words finally put on it. The terminal words themselves remain absent from the supplied transcription.

## Why this matters

The earlier STOW14 column-14 observation was retained only as an unused exploratory `LEN` clue. The new draft/photo work supplies an independently selected semantic destination for it: LOW BIT(`LEN`) lands exactly on the same **First draft** selected by THE.

This materially strengthens the version-selection picture without generating a candidate phrase. It also gives a source-local start point for the pre-existing COUNT LINE lineage rather than choosing N09 as the only possible entry.

The result does **not** authenticate any final K08 word. The post-label character boundary is inherited from the existing STOW14 operator report, and interpreting the suffix as a character column remains a source-local mechanism hypothesis rather than an explicit historical encoding instruction.

## Reproducer

`agents/agent42/k08_stow14_len_n02_lineage_sft.py`

The source-pinned SFT reproduces STOW14, its N19/N20/N15/N23 addresses, column-14 `LEN`, LOW BIT -> N02, the independent THE -> N02 convergence, and N02 -> N13 -> N23 under COUNT LINE / LOW IF EVEN. It reads no K08 target or nonce.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing.
