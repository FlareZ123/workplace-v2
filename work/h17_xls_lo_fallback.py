#!/usr/bin/env python3
"""Read-only text extraction for an authorized legacy .xls workbook.

This is a format adapter for the H-17 K08 intake path, not a source scanner.
It hashes the original, converts a temporary copy with headless LibreOffice in
an isolated profile, and emits workbook text streams with cell coordinates,
row/sheet order, comments, hyperlinks, hidden-sheet contents, formulas, cached
values, defined names and embedded-image metadata. Image bytes are emitted only
when the caller explicitly allowlists cell anchors. The original file is never modified.

LibreOffice conversion can recalculate formulas and may not preserve every
legacy object. Treat extracted text as a search aid; retain and authenticate
the original workbook independently.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

MAX_WORKBOOK_BYTES = 64 * 1024 * 1024
MAX_CELLS = 250_000
MAX_EMBEDDED_IMAGES = 32
MAX_EMBEDDED_IMAGE_BYTES = 8 * 1024 * 1024
MAX_EMBEDDED_IMAGE_TOTAL_BYTES = 32 * 1024 * 1024
STYLE_COORDS = ("M10", "C3", "EX4", "AT171", "HN28", "DZ122", "DT205", "AI96", "C67", "Z201")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _profile_config(profile: Path) -> None:
    user = profile / "user"
    user.mkdir(parents=True, exist_ok=True)
    # LibreOffice's fresh profile keeps user extensions/settings isolated.
    # MacroSecurityLevel=3 is the Very High setting; no macros are invoked.
    xcu = '''<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry"
           xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <item oor:path="/org.openoffice.Office.Common/Security/Scripting">
    <prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop>
  </item>
  <item oor:path="/org.openoffice.Office.Common/Load">
    <prop oor:name="UpdateDocMode" oor:op="fuse"><value>0</value></prop>
  </item>
</oor:items>
'''
    (user / "registrymodifications.xcu").write_text(xcu, encoding="utf-8")


def _plain(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _color_metadata(color: Any) -> dict[str, Any] | None:
    if color is None:
        return None
    return {
        "type": getattr(color, "type", None),
        "rgb": _plain(getattr(color, "rgb", None)),
        "indexed": getattr(color, "indexed", None),
        "theme": getattr(color, "theme", None),
        "tint": getattr(color, "tint", None),
    }


def _column_is_hidden(sheet: Any, column_index: int, column_letter: str) -> bool:
    for dimension in sheet.column_dimensions.values():
        minimum = getattr(dimension, "min", None)
        maximum = getattr(dimension, "max", None)
        if (minimum is not None and maximum is not None
                and minimum <= column_index <= maximum and dimension.hidden):
            return True
    dimension = sheet.column_dimensions.get(column_letter)
    return bool(dimension.hidden) if dimension is not None else False



def _image_anchor_cell(image: Any, get_column_letter: Any) -> str | None:
    """Return a stable A1 cell anchor for an openpyxl drawing image."""
    anchor = getattr(image, "anchor", None)
    if isinstance(anchor, str):
        return anchor.upper()
    marker = getattr(anchor, "_from", None)
    row = getattr(marker, "row", None)
    column = getattr(marker, "col", None)
    if isinstance(row, int) and isinstance(column, int) and row >= 0 and column >= 0:
        return f"{get_column_letter(column + 1)}{row + 1}"
    return None


def _extract_embedded_images(
    workbook: Any,
    include_image_data: bool = False,
    allowed_anchors: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Inventory converted-workbook images; emit bytes only for explicit anchors.

    Limits apply to the converted workbook's extracted image payloads. This is
    a bounded intake aid, not proof of an image's historical identity.
    """
    allowed = {str(anchor).strip().upper() for anchor in (allowed_anchors or set())
               if str(anchor).strip()}
    if include_image_data and not allowed:
        raise ValueError("image-byte emission requires at least one explicit allowed cell anchor")

    try:
        from openpyxl.utils import get_column_letter
    except ImportError as exc:  # pragma: no cover - openpyxl is already required by extract()
        raise RuntimeError("openpyxl utilities are required for image anchors") from exc

    records: list[dict[str, Any]] = []
    total_bytes = 0
    image_count = 0
    for sheet in workbook.worksheets:
        for image_index, image in enumerate(getattr(sheet, "_images", []), start=1):
            image_count += 1
            if image_count > MAX_EMBEDDED_IMAGES:
                raise RuntimeError(f"embedded image count exceeds {MAX_EMBEDDED_IMAGES}")
            anchor = _image_anchor_cell(image, get_column_letter)
            record: dict[str, Any] = {
                "sheet": sheet.title,
                "sheet_state": sheet.sheet_state,
                "image_index": image_index,
                "anchor": anchor,
                "format": getattr(image, "format", None),
                "width": getattr(image, "width", None),
                "height": getattr(image, "height", None),
                "data_included": False,
            }
            try:
                data = image._data()
            except Exception as exc:
                record["error"] = f"image-data:{type(exc).__name__}:{exc}"
                records.append(record)
                continue
            if not isinstance(data, bytes) or not data:
                record["error"] = "image-data-empty-or-not-bytes"
                records.append(record)
                continue

            record["size_bytes"] = len(data)
            record["sha256"] = hashlib.sha256(data).hexdigest()
            if len(data) > MAX_EMBEDDED_IMAGE_BYTES:
                record["reason"] = "per_image_size_limit"
            elif total_bytes + len(data) > MAX_EMBEDDED_IMAGE_TOTAL_BYTES:
                record["reason"] = "total_image_size_limit"
            else:
                total_bytes += len(data)
                if include_image_data and anchor in allowed:
                    record["data_base64"] = base64.b64encode(data).decode("ascii")
                    record["data_included"] = True
                elif include_image_data:
                    record["reason"] = "anchor_not_allowlisted"
                else:
                    record["reason"] = "metadata_only"
            records.append(record)
    return records

def extract(path: Path, timeout: int = 60, max_cells: int = MAX_CELLS,
            source_name: str | None = None, include_image_data: bool = False,
            allowed_image_anchors: set[str] | None = None) -> dict[str, Any]:
    path = path.expanduser().absolute()
    info = path.lstat()
    if path.is_symlink() or not path.is_file():
        raise ValueError("source must be a regular, non-symlink file")
    if path.suffix.casefold() != ".xls":
        raise ValueError("expected a legacy .xls workbook")
    if info.st_size <= 0 or info.st_size > MAX_WORKBOOK_BYTES:
        raise ValueError(f"workbook size must be 1..{MAX_WORKBOOK_BYTES} bytes")

    before_hash = sha256_file(path)
    soffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not soffice:
        raise RuntimeError("LibreOffice/soffice is not installed")

    try:
        import openpyxl
    except ImportError as exc:
        raise RuntimeError("openpyxl is required to inspect the converted workbook") from exc

    with tempfile.TemporaryDirectory(prefix="h17-xls-intake-") as temp_name:
        root = Path(temp_name)
        incoming = root / "incoming"
        outgoing = root / "converted"
        profile = root / "lo-profile"
        incoming.mkdir(mode=0o700)
        outgoing.mkdir(mode=0o700)
        profile.mkdir(mode=0o700)
        _profile_config(profile)
        working_copy = incoming / "source.xls"
        shutil.copyfile(path, working_copy)
        os.chmod(working_copy, 0o600)
        if sha256_file(working_copy) != before_hash:
            raise RuntimeError("temporary working copy does not match original SHA-256")

        command = [
            soffice, "--headless", "--nologo", "--nodefault", "--nolockcheck",
            "--norestore", "--nofirststartwizard",
            f"-env:UserInstallation={profile.as_uri()}",
            "--convert-to", "xlsx:Calc MS Excel 2007 XML",
            "--outdir", str(outgoing), str(working_copy),
        ]
        proc = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout,
            check=False,
        )
        converted = outgoing / "source.xlsx"
        if proc.returncode != 0 or not converted.is_file():
            raise RuntimeError(
                "LibreOffice conversion failed: "
                + (proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}")
            )

        formula_book = openpyxl.load_workbook(
            converted, data_only=False, read_only=False, keep_links=False
        )
        value_book = openpyxl.load_workbook(
            converted, data_only=True, read_only=False, keep_links=False
        )
        streams: list[dict[str, Any]] = []
        sheet_meta: list[dict[str, Any]] = []
        style_metadata: list[dict[str, Any]] = []
        count = 0

        def add(source: str, kind: str, value: str | None, **extra: Any) -> None:
            if value is not None and value != "":
                streams.append({"source": source, "kind": kind, "text": value, **extra})

        for sheet in formula_book.worksheets:
            value_sheet = value_book[sheet.title]
            sheet_meta.append({
                "name": sheet.title,
                "state": sheet.sheet_state,
                "max_row": sheet.max_row,
                "max_column": sheet.max_column,
            })
            for coordinate in STYLE_COORDS:
                cell = sheet[coordinate]
                style_metadata.append({
                    "sheet": sheet.title,
                    "sheet_state": sheet.sheet_state,
                    "coordinate": coordinate,
                    "style_id": cell.style_id,
                    "wrap_text": cell.alignment.wrap_text,
                    "horizontal_alignment": cell.alignment.horizontal,
                    "vertical_alignment": cell.alignment.vertical,
                    "fill_type": cell.fill.fill_type,
                    "fill_foreground": _color_metadata(cell.fill.fgColor),
                    "fill_background": _color_metadata(cell.fill.bgColor),
                    "font_color": _color_metadata(cell.font.color),
                    "number_format": cell.number_format,
                    "row_hidden": bool(sheet.row_dimensions[cell.row].hidden),
                    "column_hidden": _column_is_hidden(sheet, cell.column, cell.column_letter),
                    "style_source": "LibreOffice-converted XLSX; style_id is converted-workbook-local",
                })
            row_texts: list[str] = []
            cached_row_texts: list[str] = []
            for row in sheet.iter_rows():
                cells: list[str] = []
                cached_cells: list[str] = []
                for cell in row:
                    count += 1
                    if count > max_cells:
                        raise RuntimeError(f"cell limit exceeded ({max_cells})")
                    value = _plain(cell.value)
                    cached = _plain(value_sheet[cell.coordinate].value)
                    comment = cell.comment.text if cell.comment else None
                    link = cell.hyperlink.target if cell.hyperlink else None
                    coord = f"{sheet.title}!{cell.coordinate}"
                    add(coord, "cell", value, data_type=cell.data_type,
                        converted_cached_value=cached)
                    if cached is not None and cached != value:
                        add(coord + "<cached>", "cached_value", cached)
                    if comment:
                        add(coord + "<comment>", "comment", comment)
                    if link:
                        add(coord + "<hyperlink>", "hyperlink", link)
                    if value:
                        cells.append(value)
                    if cached is not None:
                        cached_cells.append(cached)
                if cells:
                    row_text = " ".join(cells)
                    row_texts.append(row_text)
                    add(f"{sheet.title}!<row:{row[0].row}>", "row", row_text)
                if cached_cells:
                    cached_row_text = " ".join(cached_cells)
                    cached_row_texts.append(cached_row_text)
                    add(f"{sheet.title}!<cached-row:{row[0].row}>", "cached_row", cached_row_text)
            if row_texts:
                add(f"{sheet.title}!<sheet>", "sheet", "\n".join(row_texts))
            if cached_row_texts:
                add(f"{sheet.title}!<cached-sheet>", "cached_sheet", "\n".join(cached_row_texts))

        defined_names = []
        for name, definition in formula_book.defined_names.items():
            record = {"name": str(name), "attr_text": getattr(definition, "attr_text", None)}
            defined_names.append(record)
            add(f"<defined-name:{name}>", "defined_name", record["attr_text"])

        embedded_images = _extract_embedded_images(
            formula_book, include_image_data=include_image_data,
            allowed_anchors=allowed_image_anchors,
        )

        props = formula_book.properties
        properties = {
            key: _plain(getattr(props, key, None))
            for key in ("title", "subject", "creator", "keywords", "description",
                        "lastModifiedBy", "category", "identifier")
        }
        converted_hash = sha256_file(converted)
        formula_book.close()
        value_book.close()

        after_hash = sha256_file(path)
        if before_hash != after_hash:
            raise RuntimeError("original workbook changed during intake")

        return {
            "source_name": source_name or path.name,
            "source_bytes": info.st_size,
            "source_sha256_before": before_hash,
            "source_sha256_after": after_hash,
            "source_unchanged": True,
            "converted_sha256": converted_hash,
            "converter": Path(soffice).name,
            "converter_exit_code": proc.returncode,
            "converter_stdout": proc.stdout.strip(),
            "converter_stderr": proc.stderr.strip(),
            "formula_values_note": "Cached values are from the LibreOffice-converted copy and may have been recalculated.",
            "sheets": sheet_meta,
            "style_metadata": style_metadata,
            "style_metadata_scope": list(STYLE_COORDS),
            "embedded_images": embedded_images,
            "defined_names": defined_names,
            "properties": properties,
            "cell_count": count,
            "text_streams": streams,
        }


def extract_bytes(data: bytes, source_name: str, timeout: int = 60,
                  max_cells: int = MAX_CELLS, include_image_data: bool = False,
                  allowed_image_anchors: set[str] | None = None) -> dict[str, Any]:
    """Adapt an in-memory archive member through a short-lived temporary copy."""
    if not isinstance(data, bytes) or not data:
        raise ValueError("workbook bytes must be a non-empty bytes object")
    if Path(source_name).suffix.casefold() != ".xls":
        raise ValueError("expected a legacy .xls member")
    if len(data) > MAX_WORKBOOK_BYTES:
        raise ValueError(f"workbook size exceeds {MAX_WORKBOOK_BYTES} bytes")
    digest = hashlib.sha256(data).hexdigest()
    with tempfile.TemporaryDirectory(prefix="h17-xls-member-") as temp_name:
        member = Path(temp_name) / "source.xls"
        member.write_bytes(data)
        os.chmod(member, 0o600)
        if sha256_file(member) != digest:
            raise RuntimeError("temporary member copy does not match input SHA-256")
        result = extract(
            member, timeout=timeout, max_cells=max_cells, source_name=source_name,
            include_image_data=include_image_data,
            allowed_image_anchors=allowed_image_anchors,
        )
        if sha256_file(member) != digest:
            raise RuntimeError("temporary member changed during intake")
        result["source_bytes"] = len(data)
        result["source_sha256_before"] = digest
        result["source_sha256_after"] = digest
        result["source_unchanged"] = True
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--text-out", type=Path,
                        help="write ordered cell/row/sheet/comment text for existing phrase intake")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--max-cells", type=int, default=MAX_CELLS)
    parser.add_argument("--include-image-data", action="store_true",
                        help="include base64 bytes only for explicitly allowlisted image anchors")
    parser.add_argument("--image-anchor", action="append", default=[],
                        help="cell anchor eligible for image-byte emission; repeat as needed")
    args = parser.parse_args()
    source = args.workbook.expanduser().absolute()
    outputs = [p for p in (args.json_out, args.text_out) if p is not None]
    resolved_outputs = [p.expanduser().resolve(strict=False) for p in outputs]
    if source.resolve(strict=False) in resolved_outputs:
        raise ValueError("output path must not overwrite the source workbook")
    if len(set(resolved_outputs)) != len(resolved_outputs):
        raise ValueError("--json-out and --text-out must be different paths")
    if args.timeout <= 0 or args.max_cells <= 0:
        raise ValueError("timeout and max-cells must be positive")
    if args.image_anchor and not args.include_image_data:
        raise ValueError("--image-anchor requires --include-image-data")
    if args.include_image_data and not args.image_anchor:
        raise ValueError("--include-image-data requires at least one explicit --image-anchor")
    result = extract(
        source, timeout=args.timeout, max_cells=args.max_cells,
        include_image_data=args.include_image_data,
        allowed_image_anchors=set(args.image_anchor),
    )
    if args.json_out:
        args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.text_out:
        lines = []
        for stream in result["text_streams"]:
            lines.append(f"[{stream['kind']}] {stream['source']}")
            lines.append(stream["text"])
        args.text_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "source_name", "source_bytes", "source_sha256_before", "source_unchanged",
        "converted_sha256", "converter", "sheets", "style_metadata", "embedded_images",
        "defined_names", "cell_count",
    )}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
