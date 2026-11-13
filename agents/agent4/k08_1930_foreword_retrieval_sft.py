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
            for term in ("foreword", "full view", "download", "pdf", "pageimage", "pageurl", "jscmd"):
                location = response.lower().find(term)
                excerpt = response[max(0, location - 130):location + 320] if location >= 0 else ""
                print("HTML term", term, "position", location, "excerpt", repr(excerpt))
            print("HTML foreword occurrence count", response.lower().count("foreword"))
            import re
            snippets = [response[max(0, match.start() - 70):match.end() + 170]
                        for match in re.finditer("foreword", response, re.IGNORECASE)]
            for i, snippet in enumerate(snippets):
                print("VIEWER FOREWORD HIT", i, repr(snippet))
        except Exception as exc:
            print("SearchWithinVolume2 failure", type(exc).__name__, str(exc)[:250])
        accessible = urllib.parse.urlencode({"jscmd": "SearchWithinVolume2", "q": "foreword", "vid": volume, "hl": "en", "output": "html_text"})
        try:
            page = request_text("https://books.google.com/books?" + accessible)
            print("ACCESSIBLE PREFIX", repr(page[:1800]))
            for term in ("foreword", "preface", "available", "page", "book search", "book info", "copyright"):
                position = page.lower().find(term)
                print("ACCESSIBLE TERM", term, position, repr(page[max(0, position - 200):position + 750] if position >= 0 else ""))
        except Exception as exc:
            print("Accessible source failure", type(exc).__name__, str(exc)[:250])
        direct = urllib.parse.urlencode({"id": volume, "pg": "PP1", "output": "html_text"})
        try:
            page = request_text("https://books.google.com/books?" + direct)
            print("DIRECT ACCESSIBLE PREFIX", repr(page[:2000]))
            print("DIRECT ACCESSIBLE FOREWORD OCCURRENCES", page.lower().count("foreword"))
        except Exception as exc:
            print("Direct accessible failure", type(exc).__name__, str(exc)[:250])
        download_url = f"https://books.google.com/books/download/The_Sea_and_the_Jungle?id={volume}&output=pdf"
        try:
            request = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=25) as item:
                prefix = item.read(256)
                print("OFFICIAL DOWNLOAD", "status", item.status, "type", item.headers.get("Content-Type"),
                      "url", item.url, "first256", repr(prefix))
        except Exception as exc:
            print("Official download failure", type(exc).__name__, str(exc)[:300])

if __name__ == "__main__":
    main()
