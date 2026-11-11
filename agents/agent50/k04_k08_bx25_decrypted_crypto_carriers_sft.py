"""H-17 experimental complete-component recovery from the decrypted BX25 crypt carrier.

Requires pypdf>=5. Original ZIP evidence, route, verifier, and commitments are read-only.
This does not assert a historical connection between a 2025 office folio and 2026 keys.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from io import BytesIO
import json
import zipfile
from pathlib import Path

from pypdf import PdfReader

ZIP_SHA256 = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
PDF_PATH = "evidence/h17-supplemental-office-files/BX25-08.pdf"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def views(word: bytes):
    assert len(word) == 16
    yield "natural", word
    yield "reverse-all", word[::-1]
    yield "reverse-per32", b"".join(word[i:i + 4][::-1] for i in range(0, 16, 4))
    yield "reverse-words", b"".join(word[i:i + 4] for i in range(12, -1, -4))


def carrier_streams(document):
    e = document.trailer["/Encrypt"].get_object()
    sources = {"file-aes-key": document._encryption._key}
    for field in ("/O", "/U", "/OE", "/UE", "/Perms"):
        value = e[field]
        sources[field] = value.original_bytes if hasattr(value, "original_bytes") else bytes(value)
    for i, value in enumerate(document.trailer["/ID"]):
        sources[f"id-{i}"] = (value.original_bytes if hasattr(value, "original_bytes")
                              else str(value).encode("latin1"))
    for i, page in enumerate(document.pages):
        sources[f"page-{i}-text"] = page.extract_text().encode("utf-8")
        sources[f"page-{i}-decoded-content"] = page.get_contents().get_data()
    return sources


def evaluate(streams, mask, copied, k04_hash, k08_hash):
    counts = Counter()
    hits = []
    for name, data in streams.items():
        for i in range(len(data) - 15):
            for orientation, candidate in views(data[i:i + 16]):
                counts["source16-views"] += 1
                stage_candidates = {
                    "coupon-xor-mask": bytes(a ^ b for a, b in zip(candidate, mask)),
                    "replacement-mask-xor-copy": bytes(a ^ b for a, b in zip(candidate, copied)),
                    "direct-reduced-k04": candidate,
                    "direct-hmac16-k08": candidate,
                }
                for stage, value in stage_candidates.items():
                    counts["complete-original-tests"] += 1
                    expected = k08_hash if stage == "direct-hmac16-k08" else k04_hash
                    if sha256(value).digest() == expected:
                        hits.append((name, i, orientation, stage, value.hex().upper()))
    return counts, hits


def run(original_zip: Path):
    data = original_zip.read_bytes()
    assert sha256(data).hexdigest() == ZIP_SHA256
    with zipfile.ZipFile(BytesIO(data)) as z:
        assert sha256(z.read("evidence/print/spool-reconstruction.log")).hexdigest() == SPOOL_SHA256
        route = json.loads(z.read("evidence/recovery-routing.json"))
        acceptance = json.loads(z.read("acceptance.json"))
        pdf_bytes = z.read(PDF_PATH)
        doc = PdfReader(BytesIO(pdf_bytes))
    assert doc.is_encrypted and doc.decrypt("8131")
    assert len(doc.pages) == 1
    sources = carrier_streams(doc)
    assert len(sources["file-aes-key"]) == 32
    assert b"2025" in sources["page-0-text"]
    assert b"2026" not in sources["page-0-text"]
    mask = bytes.fromhex(route["K04"]["masked_component"])
    copied = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
    k04_hash = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    k08_hash = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    counts, hits = evaluate(sources, mask, copied, k04_hash, k08_hash)
    assert not hits
    # In-memory planted authentic whole-coupon positive, separate SHA256 target.
    planted = bytes.fromhex("102132435465768798A9BACBDCEDFE0F")
    planted_streams = {"synthetic-document": b"genuine control:" + planted + b"-end"}
    planted_target = sha256(bytes(a ^ b for a, b in zip(planted, mask))).digest()
    positives, planted_hits = evaluate(planted_streams, mask, copied, planted_target, b"\0" * 32)
    assert any((name == "synthetic-document" and orientation == "natural" and
                stage == "coupon-xor-mask" and value ==
                bytes(a ^ b for a, b in zip(planted, mask)).hex().upper())
               for name, _, orientation, stage, value in planted_hits)
    print(json.dumps({
        "original_zip_sha256": sha256(data).hexdigest(),
        "pdf_sha256": sha256(pdf_bytes).hexdigest(),
        "carrier_sizes": {k: len(v) for k, v in sources.items()},
        "source_views": counts["source16-views"],
        "complete_original_tests": counts["complete-original-tests"],
        "original_hits": hits,
        "planted_control_hits": len(planted_hits),
        "planted_control_tests": positives["complete-original-tests"],
        "conclusion": "NO_MATCH",
    }, sort_keys=True))


if __name__ == "__main__":
    import sys
    run(Path(sys.argv[1] if len(sys.argv) > 1 else "h17-archive-dump.zip"))
