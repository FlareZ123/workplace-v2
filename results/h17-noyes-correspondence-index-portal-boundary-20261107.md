# Noyes public-site correspondence-index boundary (7 November 2026)

## Source lead

The decrypted BX25-08 property annex labels `https://noyes-energy-group.pages.dev/` as the "Electronic correspondence index". A bounded, read-only probe was run because the URL is explicitly present in the source PDF.

- Workflow: [42361978425](https://github.com/FlareZ123/workplace-v2/actions/runs/42361978425)
- Captured metadata: [noyes-index-readonly-probe.json](assets/cowper/noyes-index-readonly-probe.json)

## Observations

- The public root is a corporate marketing site, not an exposed correspondence index.
- `robots.txt` returns HTTP 200 and explicitly disallows `/admin` and `/api/`.
- The linked `/admin/` page is titled "Partner & employee access | Noyes Energy Group" and presents a username/password form. The form posts to `/api/login`.
- The probe recorded only the public page structure, form field names and status. No credentials were supplied, no form was submitted, and no disallowed API path was requested.

The public `/insights/` index and its three linked articles were also fetched read-only. They contain generic corporate marketing copy about energy systems, renewables and partnerships; they expose no H-17, incident, WN-14 or correspondence-index records. Similar wording about making space for perspectives is generic site copy and is not treated as the missing personal K08 caption.

## Stop rule

Do not access `/api/`, submit the PDF release setting to the portal, guess credentials, or attempt to bypass the login. The four-digit setting recovered for BX25-08 is specific to that PDF and is not an authorized website credential.

## Remaining source request

The actual electronic correspondence-index export must be obtained from the records custodian or another authorized source. The public site does not provide the missing H-17 correspondence or scan-release material.
