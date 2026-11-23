# Agent 25 — K08 Word revision/copy-path mechanism

Responding to the K08 direction to pursue an editor/version/copy mechanism rather than another wordlist or adjacent parser: the OOXML intake now reconstructs Word's retained revision semantics.

The K08 intake emits:
- visible final paragraph text (ordinary runs + `w:ins`/`w:moveTo`; excludes `w:del`/`w:moveFrom`);
- the distinct original paragraph view;
- each insert/delete/move event as its own stream, labelled with Word revision id, author and date;
- comment text labelled with comment id, author and date.

This provides an explicit copy/version record. A match in a deleted/original stream is not promoted as final wording. The synthetic DOCX test assembles a complete phrase across ordinary text and an inserted run, rejects the deleted version, and confirms the exact synthetic K08 HMAC only on the final view. The full K08 suite and profile self-test passed on [run 45093401174](https://github.com/FlareZ123/workplace-v2/actions/runs/45093401174).

No Word document is present in the supplied ZIP, so this is not a phrase recovery. It is a source-specific mechanism for an already-authorized profile-refresh DOCX if one exists. The report records exact behavior and limits: [Word revision/copy-path result](../../results/h17-k08-word-tracked-revision-copy-path-20261123.md).

I also closed the separate thumbnail-cache intake gap, but its cache hits remain explicitly source-unlinked; see [profile-cache result](../../results/h17-k08-profile-thumbcache-integrated-scan-20261123.md).
