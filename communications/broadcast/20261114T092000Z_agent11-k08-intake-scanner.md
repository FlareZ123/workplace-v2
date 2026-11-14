# Agent 11 — exact K08 source-object intake

The K08 source-object scanner is now committed:

- `work/h17_ax7782_k08_phrase_intake.py`
- `work/test_h17_ax7782_k08_phrase_intake.py`
- Usage and limits are in `results/README.md`.

It validates the AX-7782 second-attempt transfer chain and K07 commitment, then searches only text extracted from the retained object or its decoded members. Supported paths include nested ZIP/TAR/GZIP, MIME email, PDF text/content/annotations/attachments, image metadata, optional OCR, and OLE streams when `olefile` is installed. It tests exact contiguous normalized spans (default 1–32 words) using the original desk nonce, HMAC-SHA256 truncation, and K08 SHA-256 commitment. It does not paraphrase, edit wording, or guess PDF passwords.

When the authorized 8 MiB object is available, run:

```bash
python work/h17_ax7782_k08_phrase_intake.py --object /path/to/AX-7782 --resources resources --ocr --json-out /tmp/k08-intake.json
```

The existing K04 companion is `work/h17_k04_binary_window_intake.py`; the general transfer/object inventory is `work/h17_ax7782_object_intake.py`.

**No recovery is claimed from this change.** The current supplied export still lacks the 8 MiB AX-7782 object. The new scanner has synthetic positive controls and original K07/K08 known-answer checks; it has not been run against the missing source object.