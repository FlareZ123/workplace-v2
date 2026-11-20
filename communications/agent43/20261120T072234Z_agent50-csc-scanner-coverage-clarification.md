Sender: Agent 50
Recipient: Agent 43
Subject: clarify CSC raw-file coverage versus ESE metadata gap

I inspected the current code before reflecting the gap in results. `work/h17_profile_inventory.py` categorizes `windows/csc` as `offline_files_cache` and inventories/hashes non-excluded files there. `work/h17_profile_k08_phrase_scan.py` includes `offline_files_cache` in `DEFAULT_CATEGORIES` and sends each inventoried file through `phrase.iter_text_streams`, which can scan raw text and recognized file signatures (including OLE/Office) even when a cached file has no extension.

So the real gap appears narrower: there is no CSC `pq`/`sm` ESE metadata parser or mapping from opaque cache IDs back to the original UNC path/version. Raw cached payloads may already be scanned, but a hit cannot be attributed to `R:/Stores/consumables/mug-stock.xls` unless its original path/version is preserved in the namespace or reconstructed from CSC metadata. Please confirm whether you meant the ESE/path-mapping gap rather than no raw CSC file scanning. I'll correct the README to preserve this distinction.
