"""H-17 archival public-site acquisition through Common Crawl's public index.

Queries index metadata only. Never visits the company site, and never probes
/admin, /api, credentials or partner resources. No repository or source writes.
Independent of the earlier Internet Archive Wayback/CDX negative.
"""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

HOST = "noyes-energy-group.pages.dev"
INDEXES = (
    "CC-MAIN-2026-43",  # October 2026, post-incident
    "CC-MAIN-2026-39",  # September 2026, pre-incident
    "CC-MAIN-2026-34",  # August 2026
    "CC-MAIN-2026-30",  # July 2026
    "CC-MAIN-2026-25",  # June 2026
    "CC-MAIN-2025-51",  # December 2025
    "CC-MAIN-2025-47",  # November 2025 folio era
)
DENY_PATHS = ("/admin", "/api")


def query(index: str, exact_root: bool = False) -> tuple[str, list[dict]]:
    qs = urlencode({"url": HOST + ("/" if exact_root else "/*"), "output": "json", "filter": "status:200"})
    url = f"https://index.commoncrawl.org/{index}-index?{qs}"
    request = Request(url, headers={
        "User-Agent": "H17-archive-preservation-research/1.0 (public-index-only)"
    })
    try:
        with urlopen(request, timeout=45) as response:
            body = response.read(1500000).decode("utf-8", errors="replace")
            if len(body) >= 1500000:
                return "TRUNCATED", []
            return str(response.status), [json.loads(line) for line in body.splitlines() if line.strip()]
    except HTTPError as e:
        if e.code == 404:
            return "NO_CAPTURES", []
        return f"HTTP_{e.code}", []
    except (URLError, TimeoutError, json.JSONDecodeError) as e:
        return f"ERROR_{type(e).__name__}: {str(e)[:140]}", []


def permitted_public(entry: dict) -> bool:
    address = entry.get("url", "")
    parts = urlsplit(address)
    path = parts.path.lower()
    return (parts.hostname == HOST and
            not any(path == restricted or path.startswith(restricted + "/")
                    for restricted in DENY_PATHS) and
            entry.get("status") == "200")


def run() -> None:
    print("SCOPE: publicly indexed URL metadata for documented folio hostname only")
    print("NO site HTTP requests, credentials, login or restricted paths")
    summary = []
    for n, index in enumerate(INDEXES):
        if n:
            time.sleep(1)
        status, entries = query(index)
        if status == "HTTP_504":
            time.sleep(1)
            fallback_status, fallback_entries = query(index, exact_root=True)
            print(f"EXACT_ROOT_FALLBACK {index}: {fallback_status}, rows={len(fallback_entries)}")
            status = status + ";ROOT=" + fallback_status
            entries = fallback_entries
        public = [entry for entry in entries if permitted_public(entry)]
        other = len(entries) - len(public)
        print(f"INDEX {index}: status={status} result_rows={len(entries)} permitted_public={len(public)} excluded={other}")
        for entry in public[:40]:
            print("PUBLIC_ARCHIVED_URL", json.dumps({
                "index": index,
                "url": entry.get("url"),
                "timestamp": entry.get("timestamp"),
                "mime": entry.get("mime"),
                "digest": entry.get("digest"),
                "warc_filename": entry.get("filename"),
                "warc_offset": entry.get("offset"),
                "warc_length": entry.get("length")
            }, sort_keys=True))
        summary.append((index, status, len(entries), len(public)))
    print("INDEX_SUMMARY", json.dumps(summary))
    print("FINISHED_PUBLIC_INDEX_ONLY")


if __name__ == "__main__":
    assert permitted_public({"url": "https://" + HOST + "/projects/", "status": "200"})
    assert not permitted_public({"url": "https://" + HOST + "/admin", "status": "200"})
    assert not permitted_public({"url": "https://" + HOST + "/api/login", "status": "200"})
    assert not permitted_public({"url": "https://unrelated.example/", "status": "200"})
    run()
