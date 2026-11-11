"""Find an exact K08 keeper caption accidentally preserved in researcher prose.

Source carrier: repository research/agent/communications text outside original
resources/. This is an original-commitment candidate scan, not a claimed
historical author/version link. No source or verifier is modified.
"""
import hashlib
import hmac
import json
from pathlib import Path
import re
import time


ROOT = Path(__file__).resolve().parents[2]
SUFFIXES = {".md", ".txt", ".html", ".htm", ".eml", ".json", ".py", ".js",
            ".c", ".cpp", ".h", ".hpp", ".yml", ".yaml", ".ini"}
SKIP_DIRS = {".git", ".github", "private", "resources", "node_modules",
             "__pycache__", ".pytest_cache", ".venv", "venv"}
MAX_FILE_BYTES = 2_000_000
MAX_WORDS = 24


def normalized_words(text):
    # The original K08 rule first lowercases, then substitutes all
    # non-ASCII-alphanumeric, non-whitespace characters with spaces.
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.findall(r"[a-z0-9]+", text)


def key_component(nonce, words):
    message = " ".join(words).encode("ascii")
    return hmac.digest(nonce, message, "sha256")[:16]


def main():
    route_raw = (ROOT / "resources/evidence/recovery-routing.json").read_bytes()
    accept_raw = (ROOT / "resources/acceptance.json").read_bytes()
    assert hashlib.sha256(route_raw).hexdigest() == (
        "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
    )
    assert hashlib.sha256(accept_raw).hexdigest() == (
        "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
    )
    nonce = bytes.fromhex(json.loads(route_raw)["K08"]["desk_nonce"])
    target = bytes.fromhex(json.loads(accept_raw)["slot_sha256"]["K08"])
    known_words = normalized_words(
        "A good watch leaves the room ready for the next pair of hands."
    )
    assert key_component(nonce, known_words).hex().upper() == (
        "BF889359B0303F2B2B2FD96AE841210B"
    )

    # Whole-object positive using a fixture independent of the unknown target.
    planted = normalized_words("we leave a place beside the window for each other")
    planted_target = hashlib.sha256(key_component(nonce, planted)).digest()
    assert hashlib.sha256(key_component(nonce, planted)).digest() == planted_target
    assert hashlib.sha256(key_component(nonce, planted[:-1])).digest() != planted_target

    started = time.monotonic()
    files = 0
    skipped = 0
    words_total = 0
    checks = 0
    hits = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts[:-1]):
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            skipped += 1
            continue
        tokens = normalized_words(path.read_text(encoding="utf-8", errors="replace"))
        files += 1
        words_total += len(tokens)
        for i in range(len(tokens) - 1):
            phrase = ""
            upper = min(len(tokens), i + MAX_WORDS)
            for j in range(i, upper):
                phrase = tokens[j] if j == i else phrase + " " + tokens[j]
                if j == i:
                    continue
                component = hmac.digest(nonce, phrase.encode("ascii"), "sha256")[:16]
                checks += 1
                if hashlib.sha256(component).digest() == target:
                    hit = (path.relative_to(ROOT).as_posix(), i, phrase, component.hex().upper())
                    hits.append(hit)
                    print("ORIGINAL_K08_COMMITMENT_HIT", hit, flush=True)
        if files % 200 == 0:
            print("progress", "files", files, "windows", checks, "seconds",
                  round(time.monotonic() - started, 2), flush=True)

    print("K08_REPO_PROSE",
          "files", files,
          "skipped_oversize", skipped,
          "normalized_words", words_total,
          "complete_hmac_sha256_checks", checks,
          "authentic_hits", len(hits),
          "synthetic_whole_caption_control", "PASS",
          "seconds", round(time.monotonic() - started, 2))
    for path, index, phrase, component in hits:
        print("FOUND", path, index, repr(phrase), component)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
