"""Construct source-backed raw eight-byte fragments from the H-17 original evidence."""
from pathlib import Path
import re
import hashlib

root = Path("resources/evidence")
fragments = set()
sources = []
for p in sorted(root.rglob("*")):
    if not p.is_file() or p.suffix.lower() == ".pdf":
        continue
    raw = p.read_bytes()
    fragments.update(raw[i:i + 8] for i in range(len(raw) - 7))
    for match in re.finditer(rb"(?i)(?<![0-9a-f])[0-9a-f]{16,}(?![0-9a-f])", raw):
        token = match.group()
        if len(token) % 2:
            continue
        decoded = bytes.fromhex(token.decode())
        fragments.update(decoded[i:i + 8] for i in range(len(decoded) - 7))
    sources.append(p.relative_to(root))
out = Path("agents/agent6/k04_k08_raw8_fragments.bin")
out.write_bytes(b"".join(sorted(fragments)))
digest = hashlib.sha256(out.read_bytes()).hexdigest()
assert len(sources) == 41, sources
assert len(fragments) == 42698, len(fragments)
assert digest == "a14b1ee50ae0110b9d8b07cb246d8681697dddfe86cd89ee87e7b91c2329f6ff", digest
print(f"sources={len(sources)} fragments={len(fragments)} pairs={len(fragments)**2} sha256={digest}")
