#!/usr/bin/env python3
"""Convert an authorized legacy Word .doc member to a searchable .docx copy.

The conversion is performed by headless LibreOffice in a fresh profile with
macro security Very High. Only a temporary copy is written; the input bytes
are hashed and checked unchanged. The returned .docx is a search aid, not a
replacement for the original OLE object. Word comments/marginal notes are
retained by the tested conversion path and can then be read by the existing
DOCX ZIP/XML intake.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

MAX_DOC_BYTES = 64 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _profile_config(profile: Path) -> None:
    user = profile / "user"
    user.mkdir(parents=True, exist_ok=True)
    xcu = '''<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry"
           xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <item oor:path="/org.openoffice.Office.Common/Security/Scripting">
    <prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop>
  </item>
</oor:items>
'''
    (user / "registrymodifications.xcu").write_text(xcu, encoding="utf-8")


def convert_doc_bytes(data: bytes, source_name: str = "note.doc", timeout: int = 60) -> bytes:
    if not isinstance(data, bytes) or not data:
        raise ValueError("Word source must be a non-empty bytes object")
    if Path(source_name).suffix.casefold() != ".doc":
        raise ValueError("expected a legacy .doc member")
    if len(data) > MAX_DOC_BYTES:
        raise ValueError(f"Word source exceeds {MAX_DOC_BYTES} bytes")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    soffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not soffice:
        raise RuntimeError("LibreOffice/soffice is not installed")

    original_hash = sha256(data)
    with tempfile.TemporaryDirectory(prefix="h17-doc-intake-") as temp_name:
        root = Path(temp_name)
        incoming = root / "incoming"
        outgoing = root / "converted"
        profile = root / "lo-profile"
        incoming.mkdir(mode=0o700)
        outgoing.mkdir(mode=0o700)
        profile.mkdir(mode=0o700)
        _profile_config(profile)
        working_copy = incoming / "source.doc"
        working_copy.write_bytes(data)
        os.chmod(working_copy, 0o600)
        if sha256(working_copy.read_bytes()) != original_hash:
            raise RuntimeError("temporary Word copy does not match source SHA-256")

        command = [
            soffice, "--headless", "--nologo", "--nodefault", "--nolockcheck",
            "--norestore", "--nofirststartwizard",
            f"-env:UserInstallation={profile.as_uri()}",
            "--convert-to", "docx:Office Open XML Text",
            "--outdir", str(outgoing), str(working_copy),
        ]
        proc = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, check=False,
        )
        converted = outgoing / "source.docx"
        if proc.returncode != 0 or not converted.is_file():
            raise RuntimeError(
                "LibreOffice Word conversion failed: "
                + (proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}")
            )
        if sha256(working_copy.read_bytes()) != original_hash:
            raise RuntimeError("temporary Word copy changed during conversion")
        result = converted.read_bytes()
        if not result:
            raise RuntimeError("LibreOffice produced an empty DOCX")
        return result
