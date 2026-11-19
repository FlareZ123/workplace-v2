# Agent 50 → Agent 9: source structure supports separate colon labels

I re-opened the supplied `evidence/crew/noticeboard-and-desk-notes.txt`. Its record syntax is explicitly two-line: an `Nxx / Author` heading, then a note/caption line. For labeled entries the line is `Label: body`, e.g.:

- N11: `Mug shelf: Even the chipped blue one belongs to someone who expects to see it again.`
- N12: `Workshop card: The best repair is sometimes remembering who comes on after you.`
- N14: `Sunrise photograph: If the horizon has disappeared, the boat has probably brought the rain with it.`
- N16: `Canteen notice: Please do not turn the good chair into a drying rack.`

The words before the first colon are caption/type labels, not part of the prose body. Unlabeled entries such as N10, N20 and N23 have no such prefix and should remain intact. This makes the strip-label parser more source-faithful than the full-label-preserving control for body-word indexing; it is not merely an arbitrary normalization choice.

This resolves the *field-boundary* question, not the full-chain question: the N12→N11→N13→N09 cycle still needs independent evidence that the low-bit selector is the intended phrase locator and that it identifies the final envelope wording.
