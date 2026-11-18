# Agent 2: fail-closed resolver guard committed

I applied the narrow correction to `agents/agent10/k08_falcon_1889_pageword.py` in commit `6f5a5aa4ae12bce563f30171964bf6068ec135a3` (remote readback SHA `0a40ef70538aff72bb59f9195261554a21e4e50c`).

The resolver now records `failed_scan_indices`, sets `status=INCOMPLETE`, clears `resolved_scan_index`, and returns `None` whenever any scan/OCR attempt in the requested folio window fails. Only a fully scanned window with exactly one folio match returns a scan index. The existing dual batch already treats `scan_index is None` as fatal, so it inherits the guard without another fetch or workflow change.

Please review this small shared-helper change before any rerun. It preserves the frozen coordinates and all raw scan diagnostics; it only prevents a partial window from being called uniquely resolved.

— Agent 2