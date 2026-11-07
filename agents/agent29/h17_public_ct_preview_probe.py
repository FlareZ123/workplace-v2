"""Passive public certificate-transparency lookup for folio-named pages.dev host.

This checks for a historically issued exact or preview hostname, not an
application page, password, protected endpoint, or authenticated service.
Only public crt.sh certificate metadata is queried. Standard-library Python.
"""
import json
import sys
import urllib.parse
import urllib.request

HOST = 'noyes-energy-group.pages.dev'
QUERIES = (HOST, '%.' + HOST)
records = {}
for query in QUERIES:
    url = 'https://crt.sh/?' + urllib.parse.urlencode({'q': query, 'output': 'json'})
    req = urllib.request.Request(url, headers={'User-Agent': 'H17-Archive-Passive-CT/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                print(json.dumps({'query':query, 'outcome':'TOO_LARGE'}))
                continue
            entries = json.loads(raw)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({'query':query, 'outcome':'UNAVAILABLE', 'detail':str(exc)[:140]}))
        continue
    for entry in entries if isinstance(entries, list) else ():
        for name in entry.get('name_value','').lower().splitlines():
            if name == HOST or name.endswith('.' + HOST):
                records[name] = min(entry.get('not_before', '9999'), records.get(name, '9999'))
    print(json.dumps({'query':query, 'outcome':'QUERY_OK', 'rows':len(entries) if isinstance(entries,list) else 0}))
print(json.dumps({'public_certificate_hostnames':sorted(records.items()), 'distinct_hosts':len(records)},sort_keys=True))
