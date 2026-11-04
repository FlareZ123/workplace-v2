"""Original H-17 K08 note/mail literal-transmission test; never queries K08 hash."""
import hashlib
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MAIL11_SHA = "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
MAIL20_SHA = "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71"

def words(s: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9]+", s.lower()))

def ngrams(docs: dict[str, tuple[str, ...]], size: int):
    occurrences = defaultdict(set)
    for name, tokens in docs.items():
        for i in range(len(tokens) - size + 1):
            occurrences[tokens[i:i+size]].add(name)
    return {span: places for span, places in occurrences.items() if len(places) > 1}

def run(root: Path = ROOT) -> None:
    notes_path = root / "evidence/crew/noticeboard-and-desk-notes.txt"
    mail_dir = root / "evidence/mail"
    for path, sha in ((notes_path, NOTES_SHA),
                      (mail_dir / "11.eml", MAIL11_SHA),
                      (mail_dir / "20.eml", MAIL20_SHA)):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == sha, path
    docs = {}
    for path in sorted(mail_dir.glob("[0-9][0-9].eml")):
        body = path.read_text(encoding="utf-8").split("\n\n", 1)[1]
        docs["MAIL" + path.stem] = words(body)
    raw = notes_path.read_text(encoding="utf-8")
    for num, body in re.findall(r"(?m)^N(\d\d) / .+\n([^\n]+)$", raw):
        docs["N" + num] = words(body)
    assert len(docs) == 44
    five = ngrams(docs, 5)
    eight = ngrams(docs, 8)
    assert len(five) == 6 and len(eight) == 1, (len(five), len(eight))
    assert eight[("leave", "the", "light", "on", "for", "the", "next", "watch")] == {"MAIL11", "N17"}
    assert five[("back", "before", "the", "first", "boat")] == {"MAIL11", "N18"}
    assert five[("the", "end", "of", "the", "night")] == {"N13", "N20"}
    for key in ("N02", "N06", "N13", "N23"):
        tokens = docs[key]
        assert all(tokens != docs[n][i:i+len(tokens)]
                   for n in docs if n.startswith("MAIL")
                   for i in range(len(docs[n])-len(tokens)+1)), key
    for key in ("N17", "N18"):
        tokens = docs[key][docs[key].index("label")+1:]
        assert any(tokens == docs["MAIL11"][i:i+len(tokens)]
                   for i in range(len(docs["MAIL11"])-len(tokens)+1)), key
    print("24 notes + 20 mail bodies: exact cross-doc 5grams = 6, 8grams = 1")
    for span, places in sorted(five.items()):
        print(" ", " ".join(span), ":", ",".join(sorted(places)))
    print("Older N17/N18 complete quoted labels: PASS, 2/2")
    print("Complete N02/N06/N13/N23 note-body mail copies: 0")
    print("K08 final text: not found. K08 target hash never read.")

if __name__ == "__main__":
    run()
