"""Write the verified public-domain Falcon word stream once into the shared repo.

Called by a manual authenticated GitHub Actions run after the source-pinned K08
AES test has verified the exact original source and 81,392-word corpus.
GitHub's create-file Contents API makes one atomic repository commit.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

PIN = "36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66"
TARGET = "work/h17_falcon_1889_normalized_words.txt"
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work/agent43-falcon-aes/falcon-normalized-wordstream.txt"


def main() -> None:
    raw = SOURCE.read_bytes()
    assert raw.endswith(b"\n")
    assert hashlib.sha256(raw[:-1]).hexdigest() == PIN
    assert len(raw[:-1].decode("ascii").split()) == 81392

    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{repo}/contents/{TARGET}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "h17-archival-source-preserver",
    }
    payload = json.dumps({
        "message": "Agent 43: preserve SHA-pinned Falcon 1889 public-domain words",
        "branch": "main",
        "content": base64.b64encode(raw).decode("ascii"),
    }).encode("utf-8")
    try:
        request = Request(
            url, headers={**headers, "Content-Type": "application/json"},
            data=payload, method="PUT",
        )
        with urlopen(request, timeout=90) as response:
            assert response.status == 201
            committed = json.load(response)
            print("PINNED_WORDSTREAM_COMMITTED", TARGET, committed["commit"]["sha"])
    except HTTPError as error:
        if error.code not in (409, 422):
            raise
        # Another agent may have added the identical file concurrently.
        with urlopen(Request(url, headers=headers, method="GET"), timeout=30) as response:
            existing = json.load(response)
        content = base64.b64decode(existing["content"].replace("\n", ""))
        if content != raw:
            raise RuntimeError(f"Conflicting existing public source at {TARGET}") from error
        print("PINNED_WORDSTREAM_ALREADY_PRESENT_IDENTICAL", TARGET)


if __name__ == "__main__":
    main()
