"""H-17 cross-archive label-seeded CPython Random source-block recovery pilot.

This probes *selected historical prehash/opaque blocks* from five independent
archive families before considering K04. The selected disputed printer bytes,
K04 commitment, and K08 wording are never used as candidate selectors.

Run with the unchanged original H-17 ZIP path as the sole argument.
"""
import hashlib
import json
import random
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ZIP_SHA = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
WINDOW_WORDS = 1_000_000
BLOCKS = {
    "K01_ink_register": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K02_selected_telemetry_preimage": bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
    "K05_selected_latches": bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
    "K06_issued_strips": bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
    "K07_selected_checkpoints_preimage": bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9"),
}
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")


def seeds():
    labels = [
        "H17", "H-17", "REC8", "REC8/1", "CEG-ARCHIVE-RECOVERY/v1",
        "IR-261003-H17", "H17-IR-261003", "2026-10-03", "2026-10-04",
        "20261003", "261003", "H17-POL-17", "H17-IR-261003|REC8/1",
        "PS-261003-0417", "ESC-N", "FA-17", "BX25/08", "Noyes Energy Group",
        "IR261003", "2026-09-24", "WN-14", "PTW-417", "RC-17", "AX-7782",
        "LT-204", "PS-261003-0420", "H-17 archive recovery",
        "H17-IR-261003|K04", "K01", "K02", "K03", "K04", "K05", "K06",
        "K07", "K08", "REC8|K01", "REC8|K02", "REC8|K05", "REC8|K06",
        "REC8|K07",
    ]
    for label in ("WN-14", "LT-204", "PTW-417", "PS-261003-0417",
                  "TRP2", "RC-17", "AX-7782", "Emily"):
        labels.extend((f"H17|{label}", f"{label}|H17", f"IR-261003-H17|{label}"))
    integers = [
        17, 2026, 261003, 20261003, 20261004, 20260924, 2610030417,
        417, 7782, 1700, 1802, 2103, 8131, 202610031802,
    ]
    times = [
        "2026-10-03T18:02:00+00:00", "2026-10-03T18:25:00+00:00",
        "2026-10-03T21:13:40+00:00", "2026-10-03T21:14:00+00:00",
    ]
    integers.extend(int(datetime.fromisoformat(t).timestamp()) for t in times)
    return list(dict.fromkeys(labels + integers + [MASK, NONCE] + list(BLOCKS.values())))


def full_views(block):
    words = [block[i:i + 4] for i in range(0, 16, 4)]
    return (
        b"".join(words),
        b"".join(w[::-1] for w in words),
        b"".join(words[::-1]),
        b"".join(w[::-1] for w in words[::-1]),
    )


def halfword_stream(native_bytes, half, reverse):
    """Extract one endian view of the top/bottom 16 bits of each native MT32 word."""
    size = len(native_bytes) // 4
    result = bytearray(size * 2)
    result[::2] = native_bytes[half + int(reverse)::4]
    result[1::2] = native_bytes[half + int(not reverse)::4]
    return bytes(result)


def main(zip_path):
    assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == ZIP_SHA
    with zipfile.ZipFile(zip_path) as z:
        original = json.loads(z.read("acceptance.json"))
        route = json.loads(z.read("evidence/recovery-routing.json"))
    assert bytes.fromhex(route["K04"]["masked_component"]) == MASK
    assert bytes.fromhex(route["K08"]["desk_nonce"]) == NONCE
    for slot in ("K01", "K02", "K05", "K06", "K07"):
        raw = BLOCKS[next(k for k in BLOCKS if k.startswith(slot))]
        component = hashlib.sha256(raw).digest()[:16] if slot in ("K02", "K07") else raw
        assert hashlib.sha256(component).hexdigest() == original["slot_sha256"][slot].lower()

    precomputed = {key: value for name, block in BLOCKS.items()
                   for key, value in ((name + "#" + str(i), v) for i, v in enumerate(full_views(block)))}
    source_seeds = seeds()
    assert len(source_seeds) == 90
    full_hits = []
    half_hits = []
    planted_full = planted_half = False

    for index, seed in enumerate(source_seeds):
        emitted = random.Random(seed).randbytes(WINDOW_WORDS * 4)
        if index == 0:
            synthetic = emitted[123456 * 4:123456 * 4 + 16]
            planted_full = emitted.find(synthetic) == 123456 * 4
        for label, pattern in precomputed.items():
            position = emitted.find(pattern)
            if position >= 0:
                full_hits.append((repr(seed), label, position))
        for half in (0, 2):
            for reversed_bytes in (False, True):
                words = halfword_stream(emitted, half, reversed_bytes)
                if index == 0 and half == 2 and reversed_bytes:
                    synthetic = words[4321 * 2:4321 * 2 + 16]
                    planted_half = words.find(synthetic) == 4321 * 2
                for label in ("K02_selected_telemetry_preimage", "K07_selected_checkpoints_preimage"):
                    position = words.find(BLOCKS[label])
                    if position >= 0:
                        half_hits.append((repr(seed), label, half, reversed_bytes, position))
    assert planted_full and planted_half and full_hits == [] and half_hits == []
    print(json.dumps({
        "original_zip_sha256": ZIP_SHA,
        "independent_selected_source_blocks": len(BLOCKS),
        "canonical_public_seed_values": len(source_seeds),
        "native_MT32_output_words_per_seed": WINDOW_WORDS,
        "native_full_block_layout_lookups": len(source_seeds) * len(precomputed),
        "structured_eight_halfword_lookups": len(source_seeds) * 4 * 2,
        "native_full_block_hits": full_hits,
        "structured_halfword_hits": half_hits,
        "planted_full_and_halfword_controls": [planted_full, planted_half],
        "note": "A named bounded authoring hypothesis, not a universal generator exclusion",
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
