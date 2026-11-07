"""Source-anchored K08 whole-passages inside three Noyes books.

Complements Agent25's full printed-line / sentence carrier by allowing complete
captions copied from an internal fragment of an authentic source paragraph.
Source texts remain external and are fetched only at runtime.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent25"))
import k08_noyes_literary_source_sft as older

BOOK_HASHES = {
    30501: "3e5588432f79238db9981beb4eda71296d7b23d3cbec73148fa194c8ded378cf",
    30599: "a29d7154a71073d0037ffffeaa2fcca3440778a73c982d55b6e9ba4449bf192c",
    43186: "5293ddb4075785ac138ac01ecb2ad5f4e3154a7ed84d0bb31b762b90c2404d5d",
}
MIN_WORDS, MAX_WORDS = 4, 28

def passage_windows(text):
    """Yield (whole normalized caption, paragraph ordinal, start) for every window."""
    paragraphs = re.split(r"\n[ \t]*\n+", text)
    for paragraph_no, paragraph in enumerate(paragraphs, 1):
        words = re.findall(r"[a-z0-9]+", paragraph.lower(), flags=re.ASCII)
        for start in range(len(words)):
            for length in range(MIN_WORDS, min(MAX_WORDS, len(words)-start)+1):
                yield " ".join(words[start:start+length]), paragraph_no, start

def main():
    notes = (ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(notes).hexdigest() == older.NOTE_SHA256
    assert older.reduce_caption("A good watch leaves the room ready for the next pair of hands").hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    a = "The next watch left the last cup beside the old lamp."
    control_text = "Before this there was a photograph.\n\n" + a + " A different ending."
    phrase = older.normalize(a)
    assert any(x == phrase for x, _, _ in passage_windows(control_text))
    assert older.accepted("A good watch leaves the room ready for the next pair of hands") is False
    print("ORIGINAL_SOURCE_AND_WHOLE_WINDOW_CONTROLS_PASS", flush=True)

    total = 0
    found = []
    for book_id in older.BOOK_IDS:
        url, source_sha, text = older.fetch_book(book_id)
        assert source_sha == BOOK_HASHES[book_id], (book_id, source_sha)
        seen = set()
        book_count = 0
        for phrase, para, offset in passage_windows(text):
            if phrase in seen:
                continue
            seen.add(phrase)
            book_count += 1
            if older.accepted(phrase):
                record = {"book": book_id, "caption": phrase,
                          "K08": older.reduce_caption(phrase).hex().upper(),
                          "paragraph": para, "word_offset": offset}
                found.append(record)
                print("ORIGINAL_K08_HIT", json.dumps(record), flush=True)
        total += book_count
        print("BOOK_RESULT", json.dumps({"book": book_id, "url":url,
             "sha256":source_sha, "distinct_windows":book_count,
             "original_hits":sum(x["book"]==book_id for x in found)}), flush=True)
    print("FINAL_RESULT", json.dumps({"complete_normalized_windows":total,
          "original_K08_hits": found, "status":"HIT" if found else "NO_HIT"}), flush=True)
    if found:
        raise SystemExit(9)

if __name__ == "__main__":
    main()
