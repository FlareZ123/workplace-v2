"""Original-source AES-CTR K04 carrier test, SHA-pinned read-only, paired K08 experiment."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from k08_aes_ciphertext_carrier_sft import ACCEPT, ROUTE, SIX, carriers, source


def main(root: Path) -> None:
    original_acceptance = json.loads(source(root / "acceptance.json", ACCEPT))
    route = json.loads(source(root / "evidence/recovery-routing.json", ROUTE))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = original_acceptance["slot_sha256"]["K04"]
    keys = [bytes.fromhex(v) for v in SIX.values()]
    for name, value in zip(SIX, keys):
        assert hashlib.sha256(value).hexdigest() == original_acceptance["slot_sha256"][name]
    keys.extend([nonce, mask])
    windows = carriers(root)
    data = np.frombuffer(b"".join(windows), dtype=np.uint8).reshape((-1, 16))
    mask_vec = np.frombuffer(mask, dtype=np.uint8)
    hits = []
    count = 0
    for key_idx, key in enumerate(keys):
        for iv_idx, iv in enumerate((bytes(16), nonce, mask)):
            obj = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
            pads = obj.update(bytes(64)) + obj.finalize()
            for offset in range(4):
                pad = np.frombuffer(pads[offset*16:(offset+1)*16], dtype=np.uint8)
                possible_k04 = data ^ pad ^ mask_vec
                for window_idx, block in enumerate(possible_k04):
                    if hashlib.sha256(block).hexdigest() == target:
                        hits.append((key_idx, iv_idx, offset, window_idx))
                count += len(windows)
    assert count == 5_922_720 and hits == [], (count, hits)
    print("ORIGINAL_CTR_K04 windows=61695 keys=8 iv=3 stages=4 component_checks=5922720 hits=0")

    positive = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    physical = bytes(a ^ b for a, b in zip(positive, mask))
    obj = Cipher(algorithms.AES(keys[0]), modes.CTR(nonce)).encryptor()
    ciphertext = bytes(x ^ y for x, y in zip(physical, obj.update(bytes(16))))
    obj = Cipher(algorithms.AES(keys[0]), modes.CTR(nonce)).decryptor()
    recovered_coupon = obj.update(ciphertext)
    recovered = bytes(x ^ y for x, y in zip(recovered_coupon, mask))
    assert recovered == positive and hashlib.sha256(recovered).digest() == hashlib.sha256(positive).digest()
    print("SYNTHETIC_FULL_COUPON_AES_CTR_PLANT PASS")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
