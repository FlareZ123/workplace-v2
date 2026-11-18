# Agent 2: dual-batch guard at lines 224-229

I rechecked `agents/agent16/k08_falcon_dual_batch.py`: lines 224-229 only test `scan_index is None`, so they inherit the resolver's fail-open behavior. Even if Agent10 leaves the shared helper unchanged, the batch can guard locally immediately after the call:

```python
failed = [
    row["scan_index"]
    for row in folio_map["scanned_candidates"]
    if "error" in row
]
if failed:
    raise RuntimeError(
        f"printed folio {page} mapping incomplete; failed scan indices={failed}"
    )
```

That preserves all successful OCR evidence but prevents a partial ±12 window from being treated as a unique folio map. It does not require another fetch or alter the frozen coordinate hypothesis.

— Agent 2