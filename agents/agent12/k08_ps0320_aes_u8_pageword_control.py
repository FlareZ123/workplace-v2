#!/usr/bin/env python3
"""N20/PS-0320 earlier-version control for the bounded AES/u8 page-word test."""
import argparse, hashlib, hmac, json, re
from pathlib import Path
import fitz, pytesseract
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PDF_SHA = "0f237b073f5768b77b5badc78836a76e35fc84cd67e5c3542175831b87564d3b"
K08_SHA = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
NONCE_HEX = "5F933DA6A1BD03C32DA5CBC25344F497"
CIPHER_HEX = "9B9D8D85D48AF325FF55556CE0AE7BF3"
PLAINTEXT_HEX = "9266952F91A151BA399876EB5A0E83E2"
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
MANUAL_FOLIOS = {14: 27, 81: 96, 161: 178}
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
    phrase = re.sub(r"[^a-z0-9\s]", " ", phrase)
    return re.sub(r"\s+", " ", phrase).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=None,
                        help="repository root, or extracted Bundle06 root for local reproduction")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve() if args.root else Path(__file__).resolve().parents[2]

    pdf_bytes = args.pdf.resolve().read_bytes()
    if sha256(pdf_bytes) != PDF_SHA:
        raise SystemExit("PDF SHA-256 differs from the pinned Falcon scan")
    acceptance = json.loads(source_path(root, "acceptance.json").read_text())
    routing = json.loads(source_path(root, "evidence/recovery-routing.json").read_text())
    target = acceptance["slot_sha256"]["K08"]
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    if target != K08_SHA or nonce.hex().upper() != NONCE_HEX:
        raise SystemExit("K08 commitment or desk nonce differs from pinned source")

    spool = source_path(root, "evidence/print/spool-reconstruction.log").read_text()
    rows = [line for line in spool.splitlines() if "JOB=PS-261003-0320 " in line]
    if len(rows) != 1:
        raise SystemExit(f"expected one PS-0320 row, found {len(rows)}")
    row = rows[0]
    if not all(token in row for token in ("ATTEMPT=1", "STATE=ACK", "CLASS=RECOVER", "DEST=bench")):
        raise SystemExit("PS-0320 retained row no longer has its pinned role")
    match = re.search(r"\bPAYLOAD=([0-9A-Fa-f]{32})\b", row)
    if not match or match.group(1).upper() != CIPHER_HEX:
        raise SystemExit("PS-0320 payload differs from pinned value")
    decryptor = Cipher(algorithms.AES(nonce), modes.ECB()).decryptor()
    plaintext = decryptor.update(bytes.fromhex(match.group(1))) + decryptor.finalize()
    if plaintext.hex().upper() != PLAINTEXT_HEX:
        raise SystemExit("PS-0320 AES plaintext differs from pinned value")

    b = list(plaintext)
    coordinate_sets = {
        "high_page_low_word": [(b[i], b[i + 1]) for i in range(0, 16, 2)],
        "low_page_high_word": [(b[i + 1], b[i]) for i in range(0, 16, 2)],
    }
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    if document.page_count != 350:
        raise SystemExit(f"unexpected PDF page count: {document.page_count}")
    folios = sorted({folio for coordinates in coordinate_sets.values() for folio, _ in coordinates})
    page_map = {}
    for folio in folios:
        if folio in MANUAL_FOLIOS:
            page_map[folio] = MANUAL_FOLIOS[folio]
            continue
        hits = []
        for index, page in enumerate(document):
            lines = [line.strip() for line in page.get_text("text").splitlines() if line.strip()]
            if str(folio) in lines:
                hits.append(index)
        if len(hits) != 1:
            raise RuntimeError(f"folio {folio}: expected one standalone hit, found {hits}")
        page_map[folio] = hits[0]

    page_tokens = {}
    for folio, index in page_map.items():
        page = document.load_page(index)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        ocr = pytesseract.image_to_string(image, lang="eng", config="--psm 4")
        page_tokens[folio] = {
            "pdf_text_layer": WORD_RE.findall(clean_body_lines(page.get_text("text"))),
            "tesseract_2x_psm4": WORD_RE.findall(clean_body_lines(ocr)),
        }
    document.close()

    candidates = {}
    for orientation, coordinates in coordinate_sets.items():
        for base in (0, 1):
            for source in ("pdf_text_layer", "tesseract_2x_psm4"):
                words, contexts, error = [], [], None
                for folio, position in coordinates:
                    tokens = page_tokens[folio][source]
                    index = position - base
                    if not 0 <= index < len(tokens):
                        error = f"folio {folio} has {len(tokens)} tokens; position {position}, base {base}"
                        break
                    words.append(tokens[index])
                    contexts.append({"folio": folio, "position": position, "word": tokens[index],
                                     "context": tokens[max(0, index - 3):index + 4]})
                label = f"{orientation}_base{base}_{source}"
                if error:
                    candidates[label] = {"status": "INCOMPLETE", "error": error}
                    continue
                phrase = normalize(words)
                component = hmac.new(nonce, phrase.encode(), hashlib.sha256).digest()[:16]
                candidates[label] = {
                    "status": "COMPLETE", "words": words, "normalized_phrase": phrase,
                    "hmac16": component.hex().upper(), "sha256": sha256(component),
                    "match": sha256(component) == target, "contexts": contexts,
                }

    n02_phrase = normalize("A good watch leaves the room ready for the next pair of hands".split())
    n02_component = hmac.new(nonce, n02_phrase.encode(), hashlib.sha256).digest()[:16]
    if n02_component.hex().upper() != N02_HMAC16 or sha256(n02_component) == target:
        raise SystemExit("N02 HMAC known-answer control failed")

    result = {
        "status": "NO_K08_MATCH_ON_COMPLETE_CONTROL_VIEWS",
        "payload_hex": CIPHER_HEX, "plaintext_hex": PLAINTEXT_HEX,
        "coordinate_sets": coordinate_sets, "page_map_zero_based": page_map,
        "manual_folio_map": MANUAL_FOLIOS, "candidates": candidates,
        "complete": sum(item["status"] == "COMPLETE" for item in candidates.values()),
        "incomplete": sum(item["status"] == "INCOMPLETE" for item in candidates.values()),
        "matches": sum(item.get("match", False) for item in candidates.values()),
        "n02_control_hmac16": n02_component.hex().upper(),
        "pdf_sha256": PDF_SHA, "k08_target_sha256": target,
        "tesseract_version": str(pytesseract.get_tesseract_version()),
        "scope": "N20/PS-0320 earlier-version negative control only; same four u8 page-word views and word bases 0/1. High-page orientation is incomplete because folio 81 has 154/155 body tokens but position 186 is requested.",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
