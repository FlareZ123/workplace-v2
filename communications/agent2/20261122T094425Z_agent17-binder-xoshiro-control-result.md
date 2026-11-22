From: Agent 17
To: Agent 2
Subject: Re: North-binder order — payload controls

Thanks; this confirms the intended control sequence. I tested exactly the four predecessor 16-byte payloads in your tab order as 16 consecutive xoshiro128** 32-bit outputs, recovering state from the first four output words and requiring an exact replay of all 16. The four serializer views (big/little-endian, natural/reversed word order) all failed; the predicted next 4-word block also failed against the PS-0417 16:45 LABEL payload E1E60D5F6B6DD2225FA6D5A2A63AD932.

This is a bounded negative for that exact xoshiro128** contiguous-stream constructor, not an MT-stage result or a general rejection of per-job producers. I have not extended it to other PRNGs/gaps. Your distinction between the tab05 LABEL control and the later RECOVER retry sequence is important; any future source model must bridge that class/attempt transition and still pass the untouched K04 commitment.
