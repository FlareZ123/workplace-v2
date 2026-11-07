"""Passive public archived-scan discovery for the H-17 folio-linked hostname.

Read-only urlscan.io search API: no site scan submission, login, protected
paths, corporate API requests, or dynamic credential use. The local source
only authorizes the historical publicly named correspondence hostname.
Run: python agents/agent29/h17_urlscan_historical_public_source_sft.py
"""
import json
import urllib.error
import urllib.parse
import urllib.request

HOST = 'noyes-energy-group.pages.dev'
QUERIES = (f'page.domain:{HOST}', f'task.url:"https://{HOST}/"')
for query in QUERIES:
    params = urllib.parse.urlencode({'q': query, 'size': '50'})
    url = f'https://urlscan.io/api/v1/search/?{params}'
    request = urllib.request.Request(
        url, headers={'User-Agent': 'H17-Historical-Source-Custody-Check/1.0'}
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            content = response.read(1_000_001)
            if len(content) > 1_000_000:
                print(json.dumps({'query': query, 'status': 'TOO_LARGE'}))
                continue
            data = json.loads(content)
            records = []
            for r in data.get('results', ()):
                page = r.get('page', {})
                task = r.get('task', {})
                scanned = str(task.get('url', ''))
                domain = str(page.get('domain', ''))
                if domain == HOST or urllib.parse.urlparse(scanned).hostname == HOST:
                    records.append({
                        'date': task.get('time'),
                        'url': scanned,
                        'title': page.get('title'),
                        'scan_uuid': task.get('uuid'),
                    })
            print(json.dumps({
                'query': query, 'status': 'OK',
                'total': data.get('total'),
                'historical_public_scans': records,
            }, sort_keys=True))
    except urllib.error.HTTPError as e:
        print(json.dumps({'query': query, 'status': 'HTTP_ERROR', 'http_code': e.code}))
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({'query': query, 'status': 'UNAVAILABLE',
                          'detail': str(e)[:100]}))
