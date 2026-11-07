from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path("resources/evidence/h17-supplemental-office-files/BX25-08.pdf")


def main() -> None:
    data = PDF_PATH.read_bytes()
    print(f"FILE={PDF_PATH}")
    print(f"SIZE={len(data)}")
    print(f"SHA256={sha256(data).hexdigest()}")

    reader = PdfReader(str(PDF_PATH))
    print(f"PAGES={len(reader.pages)}")
    print(f"ENCRYPTED={reader.is_encrypted}")
    print(f"METADATA={reader.metadata}")

    if reader.is_encrypted:
        password = None
        for number in range(10_000):
            candidate = f"{number:04d}"
            if reader.decrypt(candidate):
                password = candidate
                break
        if password is None:
            print("NO_4_DIGIT_NUMERIC_PASSWORD")
            return
        print(f"NUMERIC_PASSWORD={password}")

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        print(f"--- PAGE {index} ---")
        print(text if text.strip() else "[NO_TEXT_LAYER]")


if __name__ == "__main__":
    main()
