"""Source-masked K08 envelope-label literal-ancestry calibration.

No K08 secret, target commitment, or supplied caption inference is used.
Runs directly against original H-17 resources using Python's standard library.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTES = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
CONTROL = {
    "standby": "Leave the light on for the next watch",
    "commissioning": "Back before the first boat",
}
TOKEN = re.compile(r"[a-z0-9]+")


def normalize(text):
    return TOKEN.findall(text.lower())


def run():
    note_data = NOTES.read_bytes()
    assert sha256(note_data).hexdigest() == NOTES_SHA
    files = [NOTES] + [ROOT / f"evidence/mail/{i:02d}.eml" for i in range(1, 21)]
    documents = {str(p.relative_to(ROOT)): p.read_text(encoding="utf-8") for p in files}
    assert "a good watch leaves the room ready" in documents[str(NOTES.relative_to(ROOT))].lower()
    masked = {}
    occurrence_counts = Counter()
    for name, original_text in documents.items():
        text = original_text
        for label, phrase in CONTROL.items():
            # Remove full inscriptions, including MAIL-11's duplicate quoted words.
            # Optional final period accounts for N18's quotation in MAIL-11.
            text, removed = re.subn(re.escape(phrase) + r"\.?", " ", text, flags=re.IGNORECASE)
            occurrence_counts[label] += removed
        masked[name] = normalize(text)
    assert dict(occurrence_counts) == {"standby": 2, "commissioning": 2}, occurrence_counts

    # Never make artificial n-grams across document boundaries.
    def presence(needle):
        size = len(needle)
        return any(any(words[i:i + size] == needle for i in range(len(words) - size + 1))
                   for words in masked.values())

    assert presence(["a", "good", "watch", "leaves"])
    assert presence(["the", "little", "lamp", "stays", "on"])
    result = {}
    for label, phrase in CONTROL.items():
        words = normalize(phrase)
        by_size = {}
        for size in range(1, len(words) + 1):
            gram_count = sum(presence(words[i:i + size])
                             for i in range(len(words) - size + 1))
            by_size[str(size)] = {"present": gram_count, "possible": len(words) - size + 1}
        result[label] = {
            "normalized_words": words,
            "occurrences_masked_across_original_documents": occurrence_counts[label],
            "exact_words_absent_from_masked_corpus": sorted(set(w for w in words if not presence([w]))),
            "contiguous_source_ngram_coverage": by_size,
        }
    assert result["standby"]["exact_words_absent_from_masked_corpus"] == ["light"]
    assert result["standby"]["contiguous_source_ngram_coverage"]["4"]["present"] == 0
    assert result["commissioning"]["exact_words_absent_from_masked_corpus"] == []
    assert result["commissioning"]["contiguous_source_ngram_coverage"]["2"]["present"] == 0
    print(json.dumps({"source_sha256": NOTES_SHA, "source_documents": len(files),
                      "known_control_labels": result, "positive_source_spans": True},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
