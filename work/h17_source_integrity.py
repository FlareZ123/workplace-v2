"""Read-only H-17 export integrity and source-difference check (Python 3 stdlib).

Invoke compare_archive(archive_zip, checkout_resources) from an ordinary Python session.
The JSON summary distinguishes byte-identical records from source additions/changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


EXPECTED_EVIDENCE_GIT_TREE = "0196e2bc6b207b8065f50698273db9581ca3f286"


def git_blob_id(data: bytes) -> bytes:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).digest()


def git_tree_id(root: Path) -> bytes:
    entries = bytearray()
    children = sorted(root.iterdir(), key=lambda p: (p.name + ("/" if p.is_dir() else "")).encode("utf-8"))
    for child in children:
        if child.is_dir():
            mode = b"40000"
            object_id = git_tree_id(child)
        else:
            mode = b"100644"
            object_id = git_blob_id(child.read_bytes())
        entries.extend(mode + b" " + child.name.encode("utf-8") + b"\0" + object_id)
    return hashlib.sha1(b"tree " + str(len(entries)).encode("ascii") + b"\0" + entries).digest()


def compare_archive(archive_zip: Path, checkout_resources: Path) -> dict[str, object]:
    with ZipFile(archive_zip) as zip_file:
        source_names = [entry.filename for entry in zip_file.infolist() if not entry.is_dir()]
        if len(source_names) != len(set(source_names)):
            raise ValueError("Archive contains duplicate file names")
        same, changed, new = [], [], []
        for name in sorted(source_names):
            repository_file = checkout_resources.joinpath(*Path(name).parts)
            if not repository_file.is_file():
                new.append(name)
            elif zip_file.read(name) == repository_file.read_bytes():
                same.append(name)
            else:
                changed.append(name)
    excluded = {"candidate.json"}
    repo_files = {p.relative_to(checkout_resources).as_posix()
                  for p in checkout_resources.rglob("*") if p.is_file()
                  and not p.relative_to(checkout_resources).parts[0] == "work"
                  and p.relative_to(checkout_resources).as_posix() not in excluded}
    missing = sorted(repo_files.difference(source_names))
    return {
        "zip_sha256": hashlib.sha256(archive_zip.read_bytes()).hexdigest(),
        "unchanged_count": len(same),
        "changed": changed,
        "new": new,
        "missing_relative_to_repository_source": missing,
        "repository_evidence_git_tree": git_tree_id(checkout_resources / "evidence").hex(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive_zip", type=Path)
    parser.add_argument("checkout_resources", type=Path)
    args = parser.parse_args()
    print(json.dumps(compare_archive(args.archive_zip, args.checkout_resources), indent=2))
