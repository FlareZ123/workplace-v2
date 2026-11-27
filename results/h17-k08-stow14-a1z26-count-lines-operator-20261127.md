# H-17 K08: STOW14 A1Z26 emits COUNT / LINE / BETWEEN / MARGIN and reconstructs LOW IF EVEN

**Agent 18 | 27 November 2026 | New source-local operator extension; K08 still unrecovered**

## Decision question

The existing K05–K07 sender-union mask reproducibly decodes **STOW14** from the 24 crew-note author tags. Prior work has treated that value mainly as a locator to MAIL-14/WN-14. Does the literal four-letter output itself define another source-local operation before we assume it is only a namespace?

## New extension

Use ordinary A1Z26 on the already-derived letters **S T O W**:

- S = 19 -> N19
- T = 20 -> N20
- O = 15 -> N15
- W = 23 -> N23

In that exact STOW order, the four selected note bodies contain the conspicuous directive words:

- N19: **count**
- N20: **line**
- N15: **between**
- N23: **margin**

Thus the literal selector has a second readable interpretation:

**COUNT LINE BETWEEN MARGIN**

This was not found in the existing repository search for the STOW14 results or earlier LOW-BIT synthesis.

## Exact source-format continuation

In the untouched `noticeboard-and-desk-notes.txt` byte sequence (SHA-256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`):

- the N19 body containing **count** is physical text line 59;
- the N23 body containing **margin** is physical text line 71;
- there are exactly **11 physical lines strictly between them** (lines 60 through 70).

N11's post-label body begins **Even**. Independently, the numeric suffix **14** points to N14, whose post-label body begins **If**. Read together, the STOW14 extension yields:

**IF EVEN**

The earlier CREW4 path had already selected David; David's post-label body word counts for N04, N11 and N19 are 11, 14 and 22, which under the established A=0 convention spell **LOW**. The combined source-local directive is therefore:

**LOW IF EVEN**

This does **not** recover Emily's final K08 words. Its value is that it reconstructs an already-observed operator through a different STOW14/A1Z26 route rather than through the previous K05 retry-stratum interpretation.

## Stronger target-blind continuation to N09

The same A1Z26-selected STOW note set also gives a cleaner continuation that does **not** depend on physical blank/header-line serialization.

Take the established post-label word-count convention on the four STOW note IDs:

- N19 = 22 words
- N20 = 30 words
- N15 = 10 words
- N23 = 21 words

Their low bits are `0,0,0,1`. Under the same first-bit-as-LSB convention used by the existing LOW BIT chain, those four bits pack to decimal **8**, selecting **N08**. N08 is Jason's **Window photograph** line.

Now apply the independently reconstructed **LOW IF EVEN** row transition: 8 is even, so move one note lower, **N08 -> N09**. N09 is Zoey's **galley-board caption**:

`Nobody should have to make their first cup alone after a bad night.`

This is a target-blind source-only convergence onto a caption-class record. It still does not prove N09 is Emily's final wording; indeed verbatim N09 has already failed K08. Its value is selector specificity: STOW14 is no longer only a WN-14 namespace locator under this interpretation, but also deterministically reaches a surviving caption antecedent using the already calibrated LOW BIT / LOW IF EVEN operations.

## Why this is useful but not yet authentication

The four cue words are source literals reached by a fixed A1Z26 reading of an independently existing readable selector. The line-count arithmetic is exact for the preserved source bytes and produces an existing note number whose body starts with the required word.

However, the source nowhere explicitly says “interpret STOW as A1Z26 note IDs” or “count physical text lines including blank lines and note headers.” The 11-line result therefore depends on the preserved text serialization. It is a **source-local mechanism hypothesis with a concrete fixed output**, not proof of the historical encoder.

A secondary, unused observation is that taking character 14 of the four A1Z26-selected **post-label bodies** in STOW order gives `" len"`, i.e. `LEN` after the leading separator. Because that depends on the same label-stripping convention and has no independently fixed next operation, it is retained only as an exploratory clue and is not used to claim a decoder.

## Reproducer

`agents/agent18/k08_stow14_a1z26_operator_sft.py` pins the original crew-note SHA, reproduces STOW14 from the Simon/Emily/Gabriel author mask, checks the A1Z26 note IDs and cue words, asserts the exact physical line positions, reconstructs N11/EVEN and N14/IF, and independently recomputes David's LOW.

No source record, acceptance commitment, route, verifier, or canonical candidate was modified. K01/K02/K03/K05/K06/K07 remain the six accepted components; K04 and K08 remain unresolved.
