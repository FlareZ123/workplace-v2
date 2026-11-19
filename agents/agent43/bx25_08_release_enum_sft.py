#!/usr/bin/env python3
"""Read-only local four-digit password recovery for the supplied BX25-08 PDF.

The default path is the repository's preserved encrypted source. This script
never writes a decrypted copy or accesses external services. It checks the
source SHA-256, enumerates 0000..9999 in ascending order (or validates an
explicit --password), then independently verifies the result with pypdf.
Requires PyMuPDF (fitz) and pypdf.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import fitz
from pypdf import PdfReader

EXPECTED_SHA256 = "b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425"
_REPO_ROOT = next(
    (parent for parent in Path(__file__).resolve().parents if (parent / "resources").is_dir()),
    Path.cwd(),
)
DEFAULT_PDF = (
    _REPO_ROOT
    / "resources"
    / "evidence"
    / "h17-supplemental-office-files"
    / "BX25-08.pdf"
)


def _dictionary(value):
    return value.get_object() if hasattr(value, "get_object") else value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="?", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--password", help="verify one known four-digit password instead of searching")
    args = parser.parse_args()

    raw = args.pdf.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"source SHA-256 mismatch: {digest} != {EXPECTED_SHA256}")

    reader = PdfReader(str(args.pdf), strict=False)
    encrypt = _dictionary(reader.trailer["/Encrypt"])
    cf = _dictionary(encrypt.get("/CF", {}))
    stdcf = _dictionary(cf.get("/StdCF", {})) if cf else {}
    encryption = {
        "filter": str(encrypt.get("/Filter")),
        "revision": int(encrypt.get("/R")),
        "version": int(encrypt.get("/V")),
        "length_bits": int(encrypt.get("/Length")),
        "crypt_filter": str(stdcf.get("/CFM")),
    }
    expected_encryption = {
        "filter": "/Standard",
        "revision": 6,
        "version": 5,
        "length_bits": 256,
        "crypt_filter": "/AESV3",
    }
    if encryption != expected_encryption:
        raise SystemExit(f"unexpected encryption profile: {encryption}")

    doc = fitz.open(str(args.pdf))
    if not doc.needs_pass:
        raise SystemExit("source is not password-protected")

    if args.password is not None:
        if len(args.password) != 4 or not args.password.isascii() or not args.password.isdigit():
            raise SystemExit("--password must be exactly four ASCII digits")
        candidates_tested = 1
        password = args.password
        fitz_auth = doc.authenticate(password)
        if not fitz_auth:
            raise SystemExit("provided password was rejected by PyMuPDF")
    else:
        password = None
        fitz_auth = 0
        candidates_tested = 0
        for value in range(10_000):
            candidate = f"{value:04d}"
            fitz_auth = doc.authenticate(candidate)
            candidates_tested += 1
            if fitz_auth:
                password = candidate
                break
        if password is None:
            raise SystemExit("no four-digit numeric password accepted")

    verify = PdfReader(str(args.pdf), strict=False)
    pypdf_auth = int(verify.decrypt(password))
    if pypdf_auth not in (1, 2):
        raise SystemExit("pypdf did not independently authenticate the password")

    pages = verify.pages
    text = "\n".join(page.extract_text() or "" for page in pages)
    annotations = []
    image_xobjects = 0
    for page in pages:
        for annotation_ref in page.get("/Annots", []):
            annotation = _dictionary(annotation_ref)
            action = _dictionary(annotation.get("/A")) if annotation.get("/A") else None
            annotations.append({
                "subtype": str(annotation.get("/Subtype")),
                "uri": str(action.get("/URI")) if action and action.get("/URI") else None,
            })
        resources = _dictionary(page.get("/Resources")) if page.get("/Resources") else {}
        xobjects = _dictionary(resources.get("/XObject")) if resources.get("/XObject") else {}
        for item in xobjects.values():
            if _dictionary(item).get("/Subtype") == "/Image":
                image_xobjects += 1

    catalog = _dictionary(verify.trailer["/Root"])
    names = _dictionary(catalog.get("/Names")) if catalog.get("/Names") else {}
    embedded_files = bool(names.get("/EmbeddedFiles")) if names else False

    metadata = verify.metadata or {}
    print(json.dumps({
        "source": str(args.pdf),
        "source_sha256": digest,
        "encryption": encryption,
        "password": password,
        "numeric_candidates_tested": candidates_tested,
        "pymupdf_auth_code": int(fitz_auth),
        "pypdf_auth_code": pypdf_auth,
        "page_count": len(pages),
        "image_xobject_count": image_xobjects,
        "embedded_files": embedded_files,
        "metadata": {
            "title": str(metadata.title) if metadata.title else None,
            "author": str(metadata.author) if metadata.author else None,
            "producer": str(metadata.producer) if metadata.producer else None,
        },
        "annotations": annotations,
        "text": text,
        "method_note": "local PDF password result only; not proof of paper-key-register provenance",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
