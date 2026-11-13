"""Bounded read-only check for the two specifically documented 1930 Tomlinson editions."""
import json
import urllib.parse
import urllib.request

VOLUMES = ("hHYYAAAAYAAJ", "4L8XAAAAIAAJ")

def request_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "H17-archive-source-audit/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        content = response.read(180_000)
        print("HTTP", response.status, "bytes", len(content), "url", response.url)
        return content.decode("utf-8", errors="replace")

def main() -> None:
    for volume in VOLUMES:
        print("\nVOLUME", volume)
        try:
            data = json.loads(request_text(f"https://www.googleapis.com/books/v1/volumes/{volume}?country=US"))
            info = data.get("volumeInfo", {})
            access = data.get("accessInfo", {})
            print("title", info.get("title"), "date", info.get("publishedDate"), "publisher", info.get("publisher"))
            print("viewability", access.get("viewability"), "pdf", access.get("pdf"), "epub", access.get("epub"))
            pdf = access.get("pdf", {}).get("downloadLink")
            if pdf:
                try:
                    body = request_text(pdf)
                    print("PDF download prefix", repr(body[:200]))
                except Exception as exc:
                    print("PDF download failure", type(exc).__name__, str(exc)[:250])
        except Exception as exc:
            print("Books API failure", type(exc).__name__, str(exc)[:250])
        query = urllib.parse.urlencode({"jscmd": "SearchWithinVolume2", "q": "foreword", "vid": volume})
        try:
            response = request_text("https://books.google.com/books?" + query)
            print("SearchWithinVolume2 prefix", repr(response[:400]))
        except Exception as exc:
            print("SearchWithinVolume2 failure", type(exc).__name__, str(exc)[:250])

if __name__ == "__main__":
    main()
