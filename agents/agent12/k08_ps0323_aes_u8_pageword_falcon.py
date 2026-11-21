#!/usr/bin/env python3
"""Bounded PS-0323 AES-ECB -> u8 page/word test against the retained Falcon scan."""
from __future__ import annotations
import argparse, hashlib, hmac, json, re
from pathlib import Path
from typing import Any
import fitz
import pytesseract
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
PDF_SHA = "0f237b073f5768b77b5badc78836a76e35fc84cd67e5c3542175831b87564d3b"
K08_SHA = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
PLAINTEXT_HEX = "E5407654D33238607DFA324B94656E1D"
PS0323_HEX = "1E51EFD2E5CA8F4E1FC8B49297B3D74F"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[.'’/-][A-Za-z0-9]+)*")


def source_path(root: Path, relative: str) -> Path:
    candidate = root / "resources" / relative
    return candidate if candidate.exists() else root / relative


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_body_lines(text: str) -> str:
    kept = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        upper = line.upper().strip(" .:-—'\"")
        if re.fullmatch(r"\d{1,3}", upper):
            continue
        if upper in {"THE FALCON ON THE BALTIC", 'THE "FALCON" ON THE BALTIC',
                     "THE 'FALCON' ON THE BALTIC", "E. F. KNIGHT"}:
            continue
        if re.fullmatch(r"(?:CHAPTER\s+)?[IVXLCDM]+", upper):
            continue
        if len(line) <= 72 and line == line.upper() and re.search(r"[A-Z]", line):
            continue
        kept.append(line)
    return re.sub(r"(?<=[A-Za-z0-9])-\s*\n\s*(?=[A-Za-z0-9])", "", "\n".join(kept))


def normalize(words: list[str]) -> str:
    phrase = " ".join(words).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", phrase)).strip()


def folio_index(doc: fitz.Document, folio: int) -> int:
    hits = []
    for index, page in enumerate(doc):
        lines = [x.strip() for x in page.get_text("text").splitlines() if x.strip()]
        if str(folio) in lines:
            hits.append(index)
    if len(hits) != 1:
        raise RuntimeError(f"folio {folio}: expected one standalone hit, found {hits}")
    return hits[0]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", required=True, type=Path)
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                    help="repository root, or extracted Bundle06 root for local reproduction")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    root = args.root.resolve()

    pdf_bytes = args.pdf.resolve().read_bytes()
    if sha256(pdf_bytes) != PDF_SHA:
        raise SystemExit("PDF SHA-256 does not match the pinned Falcon scan")
    acceptance = json.loads(source_path(root, "acceptance.json").read_text())
    routing = json.loads(source_path(root, "evidence/recovery-routing.json").read_text())
    target = acceptance["slot_sha256"]["K08"]
    if target != K08_SHA:
        raise SystemExit("K08 commitment differs from pinned value")
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])

    spool = source_path(root, "evidence/print/spool-reconstruction.log").read_text()
    rows = [x for x in spool.splitlines() if "JOB=PS-261003-0323 " in x]
    if len(rows) != 1 or not all(x in rows[0] for x in
                                  ("ATTEMPT=1", "STATE=ACK", "CLASS=RECOVER", "DEST=store")):
        raise SystemExit("PS-0323 retained row no longer has the expected role")
    m = re.search(r"\bPAYLOAD=([0-9A-Fa-f]{32})\b", rows[0])
    if not m or m.group(1).upper() != PS0323_HEX:
        raise SystemExit("PS-0323 payload differs from pinned value")
    ciphertext = bytes.fromhex(m.group(1))
    decryptor = Cipher(algorithms.AES(nonce), modes.ECB()).decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    if plaintext.hex().upper() != PLAINTEXT_HEX:
        raise SystemExit("AES plaintext differs from pinned value")

    coordinate_sets = {
        "high_page_low_word": [(plaintext[i], plaintext[i + 1]) for i in range(0, 16, 2)],
        "low_page_high_word": [(plaintext[i + 1], plaintext[i]) for i in range(0, 16, 2)],
    }
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if doc.page_count != 350:
        raise SystemExit(f"unexpected page count: {doc.page_count}")
    folios = sorted({p for coords in coordinate_sets.values() for p, _ in coords})
    page_map = {p: folio_index(doc, p) for p in folios}

    page_tokens: dict[int, dict[str, list[str]]] = {}
    for folio, index in page_map.items():
        page = doc.load_page(index)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        ocr = pytesseract.image_to_string(img, lang="eng", config="--psm 4")
        page_tokens[folio] = {
            "pdf_text_layer": WORD_RE.findall(clean_body_lines(page.get_text("text"))),
            "tesseract_2x_psm4": WORD_RE.findall(clean_body_lines(ocr)),
        }
    doc.close()

    candidates: dict[str, Any] = {}
    for orientation, coords in coordinate_sets.items():
        for base in (0, 1):
            for extraction in ("pdf_text_layer", "tesseract_2x_psm4"):
                words, contexts = [], []
                for folio, position in coords:
                    tokens = page_tokens[folio][extraction]
                    index = position - base
                    if not 0 <= index < len(tokens):
                        raise RuntimeError(f"{orientation} base {base}: folio {folio}, {len(tokens)} tokens")
                    words.append(tokens[index])
                    contexts.append({"folio": folio, "position": position,
                                     "word": tokens[index], "context": tokens[max(0,index-3):index+4]})
                phrase = normalize(words)
                component = hmac.new(nonce, phrase.encode(), hashlib.sha256).digest()[:16]
                candidates[f"{orientation}_base{base}_{extraction}"] = {
                    "words": words, "normalized_phrase": phrase,
                    "hmac16": component.hex().upper(),
                    "sha256": sha256(component), "match": sha256(component) == target,
                    "contexts": contexts,
                }

    n02 = normalize("A good watch leaves the room ready for the next pair of hands".split())
    n02_component = hmac.new(nonce, n02.encode(), hashlib.sha256).digest()[:16]
    if n02_component.hex().upper() != N02_HMAC16 or sha256(n02_component) == target:
        raise SystemExit("N02 known-answer control failed")

    result = {
        "status": "NO_K08_MATCH" if not any(x["match"] for x in candidates.values()) else "MATCH_REVIEW",
        "ps0323_payload": ciphertext.hex().upper(), "desk_nonce": nonce.hex().upper(),
        "aes_plaintext": plaintext.hex().upper(), "coordinate_sets": coordinate_sets,
        "pdf_sha256": PDF_SHA, "pdf_page_count": 350, "folio_to_pdf_index_zero_based": page_map,
        "k08_target_sha256": target, "candidates": candidates,
        "n02_control": {"phrase": n02, "hmac16": n02_component.hex().upper(),
                        "sha256": sha256(n02_component), "expected_hmac16": N02_HMAC16},
        "tesseract_version": str(pytesseract.get_tesseract_version()),
        "scope": "Four u8 page-word views x two word bases x two text sources only; PS-0323-to-envelope and physical-book joins are unauthenticated.",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
