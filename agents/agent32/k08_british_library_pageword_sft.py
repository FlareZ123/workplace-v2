#!/usr/bin/env python3
"""Inspect the public British Library Books OCR dataset's loader and data sources.

The Hugging Face dataset viewer cannot load this legacy script-based dataset.
This probe retrieves its public loader/config files directly from the Hub.
"""
from __future__ import annotations

import json
import urllib.request

BASE = "https://huggingface.co/datasets/TheBritishLibrary/blbooks/resolve/main"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "H17-Archive-Research/1.0 (public British Library OCR dataset)"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    print(f"Fetched {url}: {len(data)} bytes")
    return data


def main() -> None:
    tree = json.loads(fetch(
        "https://huggingface.co/api/datasets/TheBritishLibrary/blbooks/tree/main?recursive=true"
    ))
    print("Repository files:", [
        {"path": item.get("path"), "size": item.get("size"), "type": item.get("type")}
        for item in tree
    ])

    loader = fetch(f"{BASE}/blbooks.py").decode("utf-8")
    print("\n--- blbooks.py ---\n")
    print(loader)

    infos = json.loads(fetch(f"{BASE}/dataset_infos.json"))
    print("\n--- dataset_infos summary ---")
    for name, info in infos.items():
        print({
            "config": name,
            "description": info.get("description"),
            "features": info.get("features"),
            "download_checksums": info.get("download_checksums"),
            "download_size": info.get("download_size"),
            "dataset_size": info.get("dataset_size"),
        })


if __name__ == "__main__":
    main()
