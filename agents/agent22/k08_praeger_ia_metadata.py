#!/usr/bin/env python3
"""Bounded Internet Archive metadata probe for public Praeger text derivatives."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

QUERY='title:"The Way That I Went" AND creator:"Praeger"'
SEARCH="https://archive.org/advancedsearch.php?" + urllib.parse.urlencode([
    ("q", QUERY),
    ("fl[]", "identifier"),
    ("fl[]", "title"),
    ("fl[]", "creator"),
    ("fl[]", "date"),
    ("fl[]", "mediatype"),
    ("fl[]", "collection"),
    ("rows", 50),
    ("page", 1),
    ("output", "json"),
])

def get_json(url: str) -> dict:
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 Agent22-H17-research"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main() -> None:
    search=get_json(SEARCH)
    docs=search.get("response",{}).get("docs",[])
    print("IA_MATCH_COUNT", len(docs))
    out={"query":QUERY,"docs":[]}
    for doc in docs:
        ident=doc.get("identifier")
        row={"search":doc,"public_text_files":[],"restricted_markers":[]}
        if ident:
            meta=get_json("https://archive.org/metadata/"+urllib.parse.quote(ident))
            row["metadata_subset"]={
                "identifier":meta.get("metadata",{}).get("identifier"),
                "title":meta.get("metadata",{}).get("title"),
                "creator":meta.get("metadata",{}).get("creator"),
                "date":meta.get("metadata",{}).get("date"),
                "collection":meta.get("metadata",{}).get("collection"),
                "access-restricted-item":meta.get("metadata",{}).get("access-restricted-item"),
            }
            for f in meta.get("files",[]):
                name=str(f.get("name",""))
                low=name.lower()
                if any(low.endswith(s) for s in ("_djvu.txt",".txt",".xml",".pdf",".epub")):
                    candidate={
                        "name":name,
                        "size":f.get("size"),
                        "source":f.get("source"),
                        "format":f.get("format"),
                        "private":f.get("private"),
                        "restricted":f.get("restricted"),
                    }
                    if f.get("private") or f.get("restricted"):
                        row["restricted_markers"].append(candidate)
                    else:
                        row["public_text_files"].append(candidate)
        out["docs"].append(row)
        print("IA_ITEM", json.dumps(row, ensure_ascii=False))
    with open("praeger-ia-metadata.json","w",encoding="utf-8") as h:
        json.dump(out,h,indent=2,ensure_ascii=False)
        h.write("\n")

if __name__=="__main__":
    main()
