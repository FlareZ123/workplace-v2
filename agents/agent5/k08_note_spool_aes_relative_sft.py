"""K08 SFT: whole-note HMAC to original printer payload via AES and common pad.
Candidate final component is recovered from PS-0323, with real N06/N13/N17/N18
whole-caption source controls. Original files and verifier read-only.
Requires cryptography. Run from the workplace-v2 checkout.
"""
import hashlib
import hmac
import json
import re
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[2]
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
K08_SHA = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def view(a, order):
    if order == 0: return a
    if order == 1: return a[::-1]
    if order == 2: return b"".join(a[i:i+4][::-1] for i in (0,4,8,12))
    return b"".join(a[i:i+4] for i in (12,8,4,0))

def load():
    notes = (ROOT/"resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    spool = (ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(notes).hexdigest() == NOTES_SHA
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    route = json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT/"resources/acceptance.json").read_text())
    candidate = json.loads((ROOT/"candidate.json").read_text())
    assert acceptance["slot_sha256"]["K08"] == K08_SHA
    assert candidate["K04"] is None and candidate["K08"] is None
    keys = {k:bytes.fromhex(v) for k,v in candidate.items() if v is not None}
    assert set(keys) == {"K01","K02","K03","K05","K06","K07"}
    assert all(hashlib.sha256(v).hexdigest() == acceptance["slot_sha256"][k]
               for k,v in keys.items())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    keys["nonce"] = nonce
    keys["mask"] = bytes.fromhex(route["K04"]["masked_component"])
    rows = {}
    for line in spool.splitlines()[1:]:
        if b"+00:00" not in line or b"ATTEMPT=1 STATE=ACK" not in line: continue
        m = re.search(rb"JOB=PS-261003-(\d+).*?PAYLOAD=([0-9A-F]{32})", line)
        assert m
        rows[int(m[1])] = bytes.fromhex(m[2].decode())
    assert len(rows) == 128 and all(n in rows for n in (302,306,313,317,318,323))
    hmacs = {}
    for note in (2,6,13,17,18):
        m = re.search(rb"^N"+f"{note:02d}".encode()+rb" / Emily[^\n]*\n([^\n]+)",
                      notes, re.M)
        assert m
        line = m[1].decode("ascii")
        if note in (2,6,17,18): line = line.split(": ",1)[1]
        normalized = " ".join(re.findall(r"[a-z0-9]+", line.lower()))
        hmacs[note] = hmac.new(nonce,normalized.encode(),hashlib.sha256).digest()[:16]
    assert hmacs[2].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    return keys, hmacs, rows

def run():
    keys, hmacs, rows = load()
    comps = set()
    models = heldout_pairs = original_hits = full_heldouts = positives = 0
    planted_pad = hashlib.sha256(b"H17 independent K08 planted transport").digest()[:16]
    for key in keys.values():
        aes = Cipher(algorithms.AES(key),modes.ECB())
        for enc in (False,True):
            def cipher(block, inverse=False):
                op = aes.decryptor() if enc == inverse else aes.encryptor()
                return op.update(block)+op.finalize()
            for hv in range(4):
                h = {n:view(v,hv) for n,v in hmacs.items()}
                for pv in range(4):
                    p = {n:view(rows[300+n],pv) for n in (*hmacs,23)}
                    for site in ("output","input"):
                        pad = (xor(p[2],cipher(h[2])) if site=="output"
                               else xor(cipher(p[2],True),h[2]))
                        matches = 0
                        for n in (6,13,17,18):
                            predicted = (xor(cipher(h[n]),pad) if site=="output"
                                         else cipher(xor(h[n],pad)))
                            matches += predicted == p[n]
                            heldout_pairs += 1
                        full_heldouts += matches == 4
                        decoded = (cipher(xor(p[23],pad),True) if site=="output"
                                   else xor(cipher(p[23],True),pad))
                        component = view(decoded,hv)
                        comps.add(component)
                        original_hits += hashlib.sha256(component).hexdigest() == K08_SHA
                        # Independently generate and recover five complete synthetic pairs.
                        synthetic = {n:(xor(cipher(v),planted_pad) if site=="output"
                                        else cipher(xor(v,planted_pad))) for n,v in h.items()}
                        recovered = (xor(synthetic[2],cipher(h[2])) if site=="output"
                                     else xor(cipher(synthetic[2],True),h[2]))
                        assert recovered == planted_pad
                        for n in (6,13,17,18):
                            got = (xor(cipher(h[n]),recovered) if site=="output"
                                   else cipher(xor(h[n],recovered)))
                            assert got == synthetic[n]
                        # An entirely withheld final 16-byte HMAC-like block roundtrips.
                        unknown = bytes([0x94])*16
                        encoded = (xor(cipher(view(unknown,hv)),planted_pad) if site=="output"
                                   else cipher(xor(view(unknown,hv),planted_pad)))
                        result = (cipher(xor(encoded,recovered),True) if site=="output"
                                  else xor(cipher(encoded,True),recovered))
                        assert view(result,hv) == unknown
                        models += 1
                        positives += 1
    summary = dict(source_models=models,real_whole_note_holdout_checks=heldout_pairs,
                   all_four_real_notes_predicted=full_heldouts,
                   distinct_complete_K08_candidates=len(comps),
                   original_K08_SHA256_hits=original_hits,
                   whole_synthetic_sixobject_controls=positives)
    assert summary == dict(source_models=512,real_whole_note_holdout_checks=2048,
                   all_four_real_notes_predicted=0,distinct_complete_K08_candidates=512,
                   original_K08_SHA256_hits=0,whole_synthetic_sixobject_controls=512)
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    run()
