"""Corrected K08 A/B entry point.

Uses the paired experiment in k08_independent_lexical_ab_3b_sft.py, with
purpose labels restricted to independently known document roles and the
separate galley-and-stores log retained as its own source record.
"""
import hashlib

import k08_independent_lexical_ab_3b_sft as base

base.ROLE = {
    2: "First draft for the crew board.",
    6: "Second desk draft.",
    17: "Standby-envelope label.",
    18: "Commissioning-envelope label.",
}
base.WRONG_ROLE = {
    2: base.ROLE[6],
    6: base.ROLE[2],
    17: base.ROLE[18],
    18: base.ROLE[17],
}

notes, mails, nonce, target = base.load_sources()
log_path = base.ROOT / "resources/evidence/crew/galley-and-stores.log"
galley_log = log_path.read_text("utf-8").strip()
galley_sha = hashlib.sha256(log_path.read_bytes()).hexdigest()
assert galley_sha == "23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46"

for case, role in base.ROLE.items():
    content_vocab = set(base.tokens(notes[case]["caption"])) - base.STOPWORDS
    assert not (set(base.tokens(role)) & content_vocab), (
        case, "purpose label contains held-out content vocabulary"
    )
for case, role in base.WRONG_ROLE.items():
    content_vocab = set(base.tokens(notes[case]["caption"])) - base.STOPWORDS
    assert not (set(base.tokens(role)) & content_vocab), (
        case, "swapped purpose label contains held-out content vocabulary"
    )

original_source_records = base.source_records


def source_records_with_galley_log(notes, mails, held, excluded, phrases):
    records = original_source_records(notes, mails, held, excluded, phrases)
    clean, manifest = base.sanitize_record(
        "GALLEY_LOG", "GALLEY_LOG | " + galley_log, phrases
    )
    records.append(("GALLEY_LOG", clean, manifest))
    return records


base.source_records = source_records_with_galley_log

original_final_prompt = base.final_prompt


def final_prompt_with_galley_log(notes, mails):
    prompt = original_final_prompt(notes, mails)
    phrases = [("N17", notes[17]["caption"]), ("N18", notes[18]["caption"])]
    clean, _ = base.sanitize_record(
        "GALLEY_LOG", "GALLEY_LOG | " + galley_log, phrases
    )
    marker = "\nFinal keeper-envelope inscription:"
    assert prompt.count(marker) == 1
    return prompt.replace(marker, "\n" + clean + marker)


base.final_prompt = final_prompt_with_galley_log
print("GALLEY_LOG_SOURCE", {
    "sha256": galley_sha,
    "chars": len(galley_log),
    "lines": len(galley_log.splitlines()),
    "purpose_labels_target_vocab_overlap": 0,
}, flush=True)
base.main()
