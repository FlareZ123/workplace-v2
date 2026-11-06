#!/usr/bin/env python3
"""SFT: pin the surviving BX25/08 source and separate real locators from an unsupported path claim."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import zipfile
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import IndirectObject

PDF_REL = "evidence/h17-supplemental-office-files/BX25-08.pdf"
BOOKMARK_REL = "evidence/h17-supplemental-office-files/retired-office-bookmarks.html"
CSV_REL = "evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv"
PDF_SHA256 = "b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425"
UNSUPPORTED_SOURCE_TERMS = (
    b"2025-08-14",
    b"RISK-CAPTURE-04",
    b"R:\\Risk\\Renewals\\H17-POL-17\\schedule\\2025-08-14.xlsx",
    b"R:/Risk/Renewals/H17-POL-17/schedule/2025-08-14.xlsx",
)
PDF_ONLY_TERMS = (*UNSUPPORTED_SOURCE_TERMS, b"drawer 2")
SUPPORTED_BOOKMARKS = (
    "R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx",
    "R:/Risk/Transfers/BX25/transfer-index.htm",
    "R:/IT/desk-images/oldscan/scanrelease.txt",
    "R:/Records/INDEX/IR-261003-H17.txt",
    "R:/IT/desktop-move-2026.html",
)


def read_member(source: Path, relative_path: str) -> bytes:
    if source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            return archive.read(relative_path)
    return (source / relative_path).read_bytes()


def all_source_members(source: Path) -> list[bytes]:
    if source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            return [archive.read(name) for name in archive.namelist() if not name.endswith("/")]
    return [path.read_bytes() for path in source.rglob("*") if path.is_file()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=Path,
        help="Original h17-archive-dump.zip or extracted resources directory containing evidence/",
    )
    args = parser.parse_args()
    source = args.source.resolve()

    pdf_bytes = read_member(source, PDF_REL)
    pdf_sha = hashlib.sha256(pdf_bytes).hexdigest()
    assert pdf_sha == PDF_SHA256, (pdf_sha, PDF_SHA256)

    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert reader.is_encrypted
    assert reader.decrypt("8131")
    assert len(reader.pages) == 1

    page = reader.pages[0]
    page_text = page.extract_text() or ""
    assert "Policy file H17-POL-17/A3" in page_text
    assert "Transfer folio BX25/08" in page_text

    content_objects = page["/Contents"].get_object()
    decoded_streams = [item.get_object().get_data() for item in content_objects]
    assert len(decoded_streams) == 10

    xref_ids = list(reader.xref[0].keys())
    assert len(xref_ids) == 22
    object_views: list[bytes] = []
    for object_id in xref_ids:
        obj = reader.get_object(IndirectObject(object_id, 0, reader))
        object_views.append(str(obj).encode("utf-8", errors="replace"))
        if hasattr(obj, "get_data"):
            object_views.append(obj.get_data())

    pdf_views = [pdf_bytes, page_text.encode("utf-8"), *decoded_streams, *object_views]
    for term in PDF_ONLY_TERMS:
        assert all(term not in view for view in pdf_views), term

    source_members = all_source_members(source)
    for term in UNSUPPORTED_SOURCE_TERMS:
        assert all(term not in member for member in source_members), term

    annotations = page.get("/Annots")
    assert annotations is not None and len(annotations) == 1
    annotation = annotations[0].get_object()
    assert annotation["/A"]["/URI"] == "https://noyes-energy-group.pages.dev/"

    bookmarks = read_member(source, BOOKMARK_REL).decode("utf-8")
    for path in SUPPORTED_BOOKMARKS:
        assert path in bookmarks, path
    assert "paper key register stayed with the Risk desk" in bookmarks

    csv_text = read_member(source, CSV_REL).decode("utf-8")
    rows = csv.DictReader(line for line in csv_text.splitlines() if not line.startswith("#"))
    rn052 = next(row for row in rows if row["line_ref"] == "RN-052")
    assert rn052 == {
        "line_ref": "RN-052",
        "source": "RISK",
        "run": "R1",
        "posting": "FILED",
        "account": "FA-17",
        "folio_or_jacket": "BX25/08",
        "amount_eur": "0.00",
        "description": "property annex scan inward transfer",
    }

    print(f"PDF_SHA256={pdf_sha}")
    print(f"PDF_PAGES={len(reader.pages)} XREF_OBJECTS={len(xref_ids)} CONTENT_STREAMS={len(decoded_streams)}")
    print("UNSUPPORTED_DATED_WORKBOOK_AND_TERMINAL_TERMS_IN_SOURCE=0")
    print(f"BOOKMARK_LOCATORS={len(SUPPORTED_BOOKMARKS)} PAPER_KEY_REGISTER=Risk desk")
    print(f"RN052={rn052['source']}/{rn052['run']}/{rn052['posting']} {rn052['account']} {rn052['folio_or_jacket']}")
    print("RESULT=PASS")


if __name__ == "__main__":
    main()
