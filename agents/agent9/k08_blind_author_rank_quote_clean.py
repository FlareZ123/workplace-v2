"""Strict blind-caption source sanitization, including quoted decoy labels."""
import re
import k08_blind_author_rank_sft as ranker

_original = ranker.masked_source

def cleaned_source(notes, mails, held, purpose, excluded=frozenset()):
    safe_mails = {}
    for mail_id, original in mails.items():
        text = original
        for note_id in sorted(excluded):
            exact = ranker.caption(notes[note_id][1]).rstrip(".!?")
            text = re.sub(re.escape(exact) + r"[.!?]?",
                          "[withheld independent competing inscription]",
                          text, flags=re.IGNORECASE)
        safe_mails[mail_id] = text
    prompt = _original(notes, safe_mails, held, purpose, excluded)
    for note_id in excluded:
        forbidden = ranker.norm(ranker.caption(notes[note_id][1]))
        assert forbidden not in ranker.norm(prompt), (held, note_id)
    return prompt

ranker.masked_source = cleaned_source

if __name__ == "__main__":
    ranker.main()
