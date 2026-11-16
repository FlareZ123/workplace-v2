"""Read-only recovery search of exact 16-byte and caption literals in prior artifacts.

Scope: agents/, results/, work/, communications/. Original evidence, private
files, acceptance, routing, verifier and candidate are never modified.
"""
import base64
import hashlib
import hmac
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEX = re.compile(r"(?<![0-9a-fA-F])([0-9a-fA-F]{32}|[0-9a-fA-F]{64})(?![0-9a-fA-F])")
BASE64 = re.compile(r"(?<![A-Za-z0-9+/])([A-Za-z0-9+/]{22}==)(?![A-Za-z0-9+/=])")
BYTES = re.compile(r"(?:0[xX][0-9A-Fa-f]{2}(?:\s*,\s*|\s+)){15,}0[xX][0-9A-Fa-f]{2}")
QUOTES = re.compile(r"""(["'])([^"'\r\n]{6,260})\1""")
TEXT = {".md", ".py", ".json", ".jsonl", ".txt", ".csv", ".c", ".cpp", ".h", ".html", ".yaml", ".yml"}


def normalize(s):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())


def main():
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    k04_digest = acceptance["slot_sha256"]["K04"]
    k08_digest = acceptance["slot_sha256"]["K08"]
    assert hashlib.sha256(bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A")).hexdigest() == acceptance["slot_sha256"]["K01"]
    control = "a good watch leaves the room ready for the next pair of hands"
    assert hmac.new(nonce, control.encode(), hashlib.sha256).digest()[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    print("ORIGINAL_K01_AND_K08_HMAC_CONTROLS=PASS", flush=True)

    seen_bytes, seen_phrases = set(), set()
    counts, hits = Counter(), []

    def binary(raw, path, number, kind):
        if len(raw) != 16 or raw in seen_bytes:
            return
        seen_bytes.add(raw)
        counts["distinct_binary_values"] += 1
        for view in (raw, raw[::-1]):
            for form, component in (("literal_component", view),
                                    ("literal_physical_coupon", bytes(a ^ b for a, b in zip(view, mask)))):
                if hashlib.sha256(component).hexdigest() == k04_digest:
                    hits.append(dict(slot="K04", path=str(path.relative_to(ROOT)), line=number,
                                     kind=kind, form=form, component=component.hex().upper()))

    def phrase(raw, path, number, kind):
        value = normalize(raw)
        if not 3 <= len(value.split()) <= 40 or len(value) > 260 or value in seen_phrases:
            return
        seen_phrases.add(value)
        counts["distinct_phrases"] += 1
        component = hmac.new(nonce, value.encode(), hashlib.sha256).digest()[:16]
        if hashlib.sha256(component).hexdigest() == k08_digest:
            hits.append(dict(slot="K08", path=str(path.relative_to(ROOT)), line=number,
                             kind=kind, phrase=value, component=component.hex().upper()))

    for dirname in ("agents", "results", "work", "communications"):
        for path in sorted((ROOT / dirname).rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT or path.stat().st_size > 2000000:
                continue
            counts["files"] += 1
            for number, line in enumerate(path.read_text(encoding="utf8", errors="replace").splitlines(), 1):
                counts["lines"] += 1
                for match in HEX.finditer(line):
                    raw = bytes.fromhex(match.group(1))
                    if len(raw) == 16:
                        binary(raw, path, number, "hex16")
                    else:
                        binary(raw[:16], path, number, "hex32_first")
                        binary(raw[16:], path, number, "hex32_last")
                for match in BASE64.finditer(line):
                    binary(base64.b64decode(match.group(1)), path, number, "base64")
                for match in BYTES.finditer(line):
                    words = re.findall(r"0[xX]([0-9A-Fa-f]{2})", match.group(0))
                    for i in range(len(words) - 15):
                        binary(bytes.fromhex("".join(words[i:i+16])), path, number, "byte_array")
                for match in QUOTES.finditer(line):
                    phrase(match.group(2), path, number, "quoted")
                if (path.suffix.lower() in (".md", ".txt") and len(line) < 260
                        and not line.lstrip().startswith(("|", "#", "[", "<!--", "http"))):
                    phrase(re.sub(r"^\s*(?:[>*-]\s+|\d+\.\s+)", "", line), path, number, "line")
    print(json.dumps({"input_scope": "agents/results/work/communications; private excluded",
                      "counts": dict(counts), "original_commitment_hits": hits}, indent=2))
    if hits:
        raise SystemExit(10)


if __name__ == "__main__":
    main()
