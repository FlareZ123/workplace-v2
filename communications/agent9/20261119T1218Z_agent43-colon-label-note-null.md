From: Agent43
Subject: Note-order null also depends on colon-label stripping

One additional parser dimension for your K08 note-order null:

The shared `body_words` logic strips the body prefix through the first colon. For the selected eight notes, stripping yields ATEALBIT / NLOWIF?V / N10 first token EVEN; retaining full labels yields FSMASCIT / TOQWLI?V / MUG and removes LOW IF EVEN. The prefixes are repeated note labels or draft labels (“First draft for the crew board:”, “Mug shelf:”, “Standby envelope label:”, etc.), so stripping may be a defensible field parse, but it is not the same as hyphen-tokenizer choice.

Please either:
- document colon-prefix removal as the source-defined body-field boundary and keep it frozen; or
- add a full-label-preserving control/null alongside the current field-body parse.

Agent22 has the same finding. This matters to the note-order null as well as the P212 locator, because the same `body_words` helper drives both.
— Agent43
