#!/usr/bin/env python3
"""Read-only, bounded OAI-PMH lookup for Cowper's Sailing Tours, Part I."""
from __future__ import annotations

import re
import sys
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
    root = ET.fromstring(payload)
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


def list_sets() -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    params = {"verb": "ListSets"}
    for _ in range(50):
        root = fetch_xml(BASE, params)
        container = root.find("oai:ListSets", NS)
        if container is None:
            break
        for item in container.findall("oai:set", NS):
            spec = child_text(item, "oai:setSpec")
            name = child_text(item, "oai:setName")
            if spec:
                found.append((spec, name))
        token = child_text(container, "oai:resumptionToken")
        if not token:
            break
        params = {"verb": "ListSets", "resumptionToken": token}
    return found


def scan_records(prefix: str, set_spec: str | None) -> tuple[str | None, int, int]:
    params = {"verb": "ListRecords", "metadataPrefix": prefix}
    if set_spec:
        params["set"] = set_spec
    seen = 0
    for page in range(1, MAX_PAGES + 1):
        root = fetch_xml(BASE, params)
        container = root.find("oai:ListRecords", NS)
        if container is None:
            print("NO_LISTRECORDS_CONTAINER", prefix, set_spec or "ALL", flush=True)
            return None, seen, page
        for record in container.findall("oai:record", NS):
            header = record.find("oai:header", NS)
            if header is None or header.attrib.get("status") == "deleted":
                continue
            seen += 1
            identifier = child_text(header, "oai:identifier")
            datestamp = child_text(header, "oai:datestamp")
            text = record_text(record)
            lowered = text.lower()
            if "cowper" in lowered and "sailing" in lowered and (
                "essex" in lowered or "suffolk" in lowered
            ):
                print("COWPER_RECORD_FOUND", flush=True)
                print("OAI_IDENTIFIER", identifier, flush=True)
                print("DATESTAMP", datestamp, flush=True)
                print("SET_SPEC", set_spec or "ALL", flush=True)
                for url in record_urls(record):
                    print("RECORD_URL", url, flush=True)
                metadata = record.find("oai:metadata", NS)
                if metadata is not None:
                    xml = ET.tostring(metadata, encoding="unicode")
                    print("MATCH_METADATA_XML", xml[:30000], flush=True)
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
                return identifier, seen, page
        token = child_text(container, "oai:resumptionToken")
        if not token:
            return None, seen, page
        params = {"verb": "ListRecords", "resumptionToken": token}
    return None, seen, MAX_PAGES


def main() -> int:
    print("OAI_BASE", BASE, flush=True)
    identify = fetch_xml(BASE, {"verb": "Identify"})
    identify_node = identify.find("oai:Identify", NS)
    if identify_node is not None:
        for field in ("repositoryName", "baseURL", "protocolVersion", "earliestDatestamp", "deletedRecord", "granularity"):
            print("IDENTIFY", field, child_text(identify_node, f"oai:{field}"), flush=True)

    prefixes = list_metadata_prefixes()
    print("METADATA_PREFIXES", ",".join(prefixes), flush=True)
    sets = list_sets()
    print("SET_COUNT", len(sets), flush=True)
    relevant_sets = [
        (spec, name)
        for spec, name in sets
        if any(word in (spec + " " + name).lower() for word in ("guidebook", "sailing", "nautical", "yacht"))
    ]
    for spec, name in relevant_sets:
        print("RELEVANT_SET", spec, "|", name, flush=True)

    prefix = "mods" if "mods" in prefixes else ("oai_dc" if "oai_dc" in prefixes else "")
    if not prefix:
        print("NO_SUPPORTED_MODS_OR_DC_PREFIX", flush=True)
        return 2

    if relevant_sets:
        for spec, _ in relevant_sets:
            identifier, seen, pages = scan_records(prefix, spec)
            print("SET_SCAN", spec, "records", seen, "pages", pages, "found", bool(identifier), flush=True)
            if identifier:
                return 0
    identifier, seen, pages = scan_records(prefix, None)
    print("FULL_SCAN", "records", seen, "pages", pages, "found", bool(identifier), flush=True)
    if identifier:
        return 0
    print("NO_COWPER_RECORD_WITHIN_BOUNDED_SCAN", flush=True)
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError, RuntimeError) as exc:
        print("OAI_LOOKUP_ERROR", type(exc).__name__, str(exc)[:1000], flush=True)
        raise SystemExit(2)
