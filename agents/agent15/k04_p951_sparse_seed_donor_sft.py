"""Original-source forensic donor test for the 86-word CPython binary-seed map.

Run in repository checkout:
  python agents/agent15/k04_p951_sparse_seed_donor_sft.py
Optionally pass the preserved 50,526-byte original ZIP as one argument to
include all original 46 members plus the raw ZIP container byte stream.
The printed bound is conditional on p951 + standard CPython seed(bytes).
Selected printer ACK2 is withheld from inference. No K04/K08 hash is read.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import k04_p951_sha512_seed_fingerprint_sft as fp

ROOT=Path(__file__).resolve().parents[2]
ZIP_SHA="e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"


def recover_original_map() -> dict[int,list[bytes]]:
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==fp.SOURCE_SHA
    tokens=re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)
    assert len(tokens)==len(fp.STARTS)==133
    assert fp.STARTS[129]==951
    packets=[b"" if i==129 else bytes.fromhex(t.decode("ascii"))
             for i,t in enumerate(tokens)]
    _,_,word_domains=fp.derive_seed_digest_words(packets,fp.expressions())
    assert len(word_domains)==86
    return {j:[v.to_bytes(4,"big") for v in choices]
            for j,choices in word_domains.items()}


def original_carriers(archive: Path | None) -> list[tuple[str,bytes]]:
    if archive is not None:
        raw=archive.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==ZIP_SHA
        with ZipFile(archive) as z:
            contents=[(x.filename,z.read(x)) for x in z.infolist()
                      if not x.is_dir()]
        assert len(contents)==46
        assert sum(len(b) for _,b in contents)==118273
        return contents+[("[original ZIP container]",raw)]
    return [(str(p.relative_to(ROOT)),p.read_bytes())
            for p in (ROOT/"resources").rglob("*") if p.is_file()]


def scan(carriers: list[tuple[str,bytes]], words: set[bytes]) -> tuple[int,int,list[tuple[str,str,int,str]]]:
    hits=[]
    raw_count=hex_count=0
    for name,payload in carriers:
        for i in range(len(payload)-3):
            raw_count+=1
            if payload[i:i+4] in words:
                hits.append((name,"raw",i,payload[i:i+4].hex().upper()))
        for run in re.finditer(rb"[A-Fa-f0-9]{8,}",payload):
            digits=run.group()
            for i in range(len(digits)-7):
                hex_count+=1
                b=bytes.fromhex(digits[i:i+8].decode("ascii"))
                if b in words:
                    hits.append((name,"decoded-hex",run.start()+i,b.hex().upper()))
    return raw_count,hex_count,hits


def main() -> None:
    assert len(sys.argv)<=2
    zip_path=Path(sys.argv[1]) if len(sys.argv)==2 else None
    domains=recover_original_map()
    assert sum(len(v)==1 for v in domains.values())==62
    assert sum(len(v)==2 for v in domains.values())==24
    assert sum(32 if len(v)==1 else 31 for v in domains.values())==2728
    assert len({x for choices in domains.values() for x in choices})==110
    candidates={w for opts in domains.values() for w in opts}
    # An actual visible exact-word donor would be located by both raw and
    # literal hex pathways; they use exactly the same scan as the real source.
    injected=b"prefix"+domains[22][0]+b"suffix "+domains[23][0].hex().upper().encode()
    _,_,positive=scan([("[synthetic]",injected)],candidates)
    assert len(positive)==2
    carriers=original_carriers(zip_path)
    raw_windows,hex_windows,hits=scan(carriers,candidates)
    assert not hits,hits[:20]
    print({
        "original_zip_scanned":zip_path is not None,
        "carrier_count":len(carriers),
        "raw_4byte_windows":raw_windows,
        "decoded_hex_8nibble_windows":hex_windows,
        "source_sparse_raw_seed_word_positions":86,
        "exact_words":62,
        "two_option_words":24,
        "source_constrained_raw_seed_bits":2728,
        "candidate_four_byte_values":110,
        "synthetic_extraction_hits":len(positive),
        "original_literal_carrier_hits":len(hits),
        "minimum_contiguous_original_carrier_pieces_if_binary_seed":87,
    })


if __name__=="__main__":
    main()
