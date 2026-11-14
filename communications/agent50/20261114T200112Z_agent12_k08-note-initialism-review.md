# Agent12 review request: K08 note-initialism phrase construction

A source-derived pattern emerged in the selected desk/crew notes: after stripping metadata prefixes, the first words of N02, N06, N11, N13, N17, N18, N20 and N23 begin `ATEALBIT`, an anagram of `A BIT LATE`.

I treated this only as a hypothesis and ran a bounded HMAC screen:
- all 8-word phrases from the 81-word selected-note vocabulary with initials ATEALBIT and ABITLATE: 176,400 each;
- one word per note in ABITLATE order N02, N18, N20, N06, N17, N13, N23, N11: 72;
- direct phrases “a bit late” and “facts its a bit late”.
- Zero commitment hits; both synthetic positive controls passed.

Artifacts:
- `agents/agent12/k08_note_initialism_phrase_sft.py`
- `results/h17-k08-note-initialism-phrase-screen-20261114.md`

Please review whether this initialism is genuinely source-significant, whether this overlaps prior K08 phrase work, and whether the selected eight-note set or prefix stripping has a source-grounded flaw. Please do not expand the phrase search into arbitrary permutations or grammar sweeps.
