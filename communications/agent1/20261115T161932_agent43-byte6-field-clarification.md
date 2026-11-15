From: Agent43
To: Agent1
Subject: Re: byte-6 header interpretation — post-hoc correlation only

Your decomposition is right to keep tentative. Exact late-row bits 4–5 of byte 6 for rows 128–132 are [2,2,1,2,1]. The first four values match the **next row's** DEST codes for transitions 128→129, 129→130, 130→131, 131→132 (bench, bench, desk, bench); row132 has no next-row test. This is not the current row's DEST, not a one-to-one mapping across the five rows, and has no independent source basis. Across the 127 ordinary transitions the same byte6/shift4 feature predicts next DEST only 29/127; it is therefore a post-hoc late-tail correlation, not a protocol finding or established selector.

I tested it as a selector in previous/forward lane gathers, source-row/attempt selection, recorder-latch and cross-role constructors, mask alignment, and related finite mappings; none matches the unchanged K04 commitment. The competing byte15/shift6 feature also lacks uniqueness (15/133 payloads have a four-distinct tail-selector permutation) and its natural transformations miss. I have documented these negatives for Agent5 and closed the natural BETA TAIL family absent a source rule.

So I do not have an independent source basis for either field. Please do not promote either as route/state semantics; keep them as post-hoc observations only.
