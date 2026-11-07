#!/usr/bin/env python3
"""Read-only, bounded OAI-PMH lookup for Cowper's Sailing Tours, Part I."""
from __future__ import annotations

import calendar
import re
import sys
import time
from collections import deque
from datetime import date, timedelta
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://onlinebooks.library.upenn.edu/webbin/OAI-onlinebooks"
AVAILABILITY = "https://onlinebooks.library.upenn.edu/webbin/availability"
NS = {"oai": "http://www.openarchives.org/OAI/2.0/"}
USER_AGENT = "H17-Cowper-OAI-metadata-audit/1.0"
MAX_PAGES = 250
MAX_RESPONSE_BYTES = 2_000_000
TIMEOUT_SECONDS = 20


def fetch_xml(base: str, params: dict[str, str]) -> ET.Element:
    url = base + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/xml"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        payload = response.read(MAX_RESPONSE_BYTES + 1)
        if len(payload) > MAX_RESPONSE_BYTES:
            raise RuntimeError(f"response exceeds {MAX_RESPONSE_BYTES} bytes: {url}")
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        sample = payload[:1200].decode("utf-8", errors="replace")
        raise RuntimeError(f"XML parse error for {url}; bytes={len(payload)}; body={sample!r}") from exc
    error = root.find("oai:error", NS)
    if error is not None:
        code = error.attrib.get("code", "unknown")
        raise RuntimeError(f"OAI error {code}: {''.join(error.itertext()).strip()}")
    return root


def child_text(parent: ET.Element, path: str) -> str:
    node = parent.find(path, NS)
    return "" if node is None else "".join(node.itertext()).strip()


def record_text(record: ET.Element) -> str:
    metadata = record.find("oai:metadata", NS)
    if metadata is None:
        return ""
    return " ".join(part.strip() for part in metadata.itertext() if part.strip())


def record_urls(record: ET.Element) -> list[str]:
    metadata = record.find("oai:metadata", NS)
    if metadata is None:
        return []
    values: list[str] = []
    for node in metadata.iter():
        if node.tag.rsplit("}", 1)[-1].lower() in {"url", "identifier"}:
            value = "".join(node.itertext()).strip()
            if value.startswith(("http://", "https://")) and value not in values:
                values.append(value)
    return values


def list_metadata_prefixes() -> list[str]:
    root = fetch_xml(BASE, {"verb": "ListMetadataFormats"})
    container = root.find("oai:ListMetadataFormats", NS)
    if container is None:
        return []
    prefixes = []
    for item in container.findall("oai:metadataFormat", NS):
        prefix = child_text(item, "oai:metadataPrefix")
        if prefix:
            prefixes.append(prefix)
    return prefixes


def scan_date_windows(prefix: str, all_prefixes: list[str]) -> int:
    first = date(2002, 1, 1)
    last = date.today()
    windows: deque[tuple[date, date]] = deque()
    cursor = date(first.year, first.month, 1)
    while cursor <= last:
        month_end = date(cursor.year, cursor.month, calendar.monthrange(cursor.year, cursor.month)[1])
        windows.append((cursor, min(month_end, last)))
        cursor = date(cursor.year + (cursor.month == 12), 1 if cursor.month == 12 else cursor.month + 1, 1)

    requests_made = 0
    records_seen = 0
    split_windows = 0
    while windows:
        if requests_made >= 2500:
            print("REQUEST_LIMIT_REACHED", requests_made, "remaining_windows", len(windows), flush=True)
            return 3
        start, end = windows.popleft()
        params = {
            "verb": "ListRecords",
            "metadataPrefix": prefix,
            "from": start.isoformat(),
            "until": end.isoformat(),
        }
        requests_made += 1
        try:
            root = fetch_xml(BASE, params)
        except RuntimeError as exc:
            if "noRecordsMatch" in str(exc):
                continue
            raise

        container = root.find("oai:ListRecords", NS)
        if container is None:
            print("NO_LISTRECORDS_CONTAINER", start, end, flush=True)
            continue
        records = container.findall("oai:record", NS)
        token_node = container.find("oai:resumptionToken", NS)
        token = child_text(container, "oai:resumptionToken")
        if token:
            complete = token_node.attrib.get("completeListSize", "unknown") if token_node is not None else "unknown"
            if start == end:
                print("DAY_STILL_PAGINATED", start, "completeListSize", complete, flush=True)
                continue
            days = (end - start).days
            midpoint = start + timedelta(days=days // 2)
            windows.appendleft((midpoint + timedelta(days=1), end))
            windows.appendleft((start, midpoint))
            split_windows += 1
            if split_windows % 100 == 0:
                print(
                    "SCAN_PROGRESS",
                    "requests", requests_made,
                    "records", records_seen,
                    "splits", split_windows,
                    "queue", len(windows),
                    "latest_split", start, end, "count", complete,
                    flush=True,
                )
            time.sleep(0.02)
            continue

        for record in records:
            header = record.find("oai:header", NS)
            if header is None or header.attrib.get("status") == "deleted":
                continue
            records_seen += 1
            identifier = child_text(header, "oai:identifier")
            datestamp = child_text(header, "oai:datestamp")
            text = record_text(record).lower()
            if "cowper" not in text or "sailing" not in text:
                continue
            if "essex" not in text and "suffolk" not in text:
                continue

            print("COWPER_RECORD_FOUND", flush=True)
            print("OAI_IDENTIFIER", identifier, flush=True)
            print("DATESTAMP", datestamp, flush=True)
            for url in record_urls(record):
                print("RECORD_URL", url, flush=True)
            metadata = record.find("oai:metadata", NS)
            if metadata is not None:
                print(
                    "MATCH_METADATA_XML",
                    ET.tostring(metadata, encoding="unicode")[:30000],
                    flush=True,
                )
            for other_prefix in all_prefixes:
                if other_prefix == prefix:
                    continue
                try:
                    expanded = fetch_xml(
                        BASE,
                        {"verb": "GetRecord", "identifier": identifier, "metadataPrefix": other_prefix},
                    )
                    expanded_metadata = expanded.find(".//oai:metadata", NS)
                    if expanded_metadata is not None:
                        print(
                            "GETRECORD_METADATA_XML",
                            other_prefix,
                            ET.tostring(expanded_metadata, encoding="unicode")[:30000],
                            flush=True,
                        )
                except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError) as exc:
                    print("GETRECORD_ERROR", other_prefix, type(exc).__name__, str(exc)[:500], flush=True)
            match = re.search(r"\bolbp\d+\b", identifier)
            if match:
                bib_id = match.group(0)
                print("BIB_ID", bib_id, flush=True)
                try:
                    availability = fetch_xml(
                        AVAILABILITY,
                        {"id": bib_id, "id_type": "bib"},
                    )
                    print(
                        "AVAILABILITY_XML",
                        ET.tostring(availability, encoding="unicode")[:20000],
                        flush=True,
                    )
                except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError) as exc:
                    print("AVAILABILITY_ERROR", type(exc).__name__, str(exc)[:500], flush=True)
            return 0

        if requests_made % 100 == 0:
            print(
                "SCAN_PROGRESS",
                "requests", requests_made,
                "records", records_seen,
                "splits", split_windows,
                "queue", len(windows),
                "last_window", start, end,
                flush=True,
            )
        time.sleep(0.02)

    print(
        "NO_COWPER_RECORD_AFTER_DATE_SCAN",
        "requests", requests_made,
        "records", records_seen,
        "splits", split_windows,
        flush=True,
    )
    return 1


def main() -> int:
    print("OAI_BASE", BASE, flush=True)
    identify = fetch_xml(BASE, {"verb": "Identify"})
    identify_node = identify.find("oai:Identify", NS)
    if identify_node is not None:
        for field in ("repositoryName", "baseURL", "protocolVersion", "earliestDatestamp", "deletedRecord", "granularity"):
            print("IDENTIFY", field, child_text(identify_node, f"oai:{field}"), flush=True)

    prefixes = list_metadata_prefixes()
    print("METADATA_PREFIXES", ",".join(prefixes), flush=True)
    prefix = "oai_dc" if "oai_dc" in prefixes else ("mods" if "mods" in prefixes else "")
    if not prefix:
        print("NO_SUPPORTED_MODS_OR_DC_PREFIX", flush=True)
        return 2
    print("DATE_BISECTION_PREFIX", prefix, "from 2002-01-01", "until", date.today(), flush=True)
    return scan_date_windows(prefix, prefixes)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError, RuntimeError) as exc:
        print("OAI_LOOKUP_ERROR", type(exc).__name__, str(exc)[:1000], flush=True)
        raise SystemExit(2)
