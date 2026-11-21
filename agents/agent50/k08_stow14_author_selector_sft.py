#!/usr/bin/env python3
"""Cross-check K08 STOW14 against all source-authored crew subsets.

From repo root: python agents/agent50/k08_stow14_author_selector_sft.py
For original archive: python agents/agent50/k08_stow14_author_selector_sft.py path/to/original.zip
Source-only: no recovery candidate or acceptance commitment is modified.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

CREW_SHA256 = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
ROOT = Path(__file__).resolve().parents[2] / 'resources' / 'evidence'


def read_evidence(path: str, archive: str | None) -> bytes:
    if archive:
        with ZipFile(archive) as zipped:
            return zipped.read('evidence/' + path)
    return (ROOT / path).read_bytes()


def decode(notes: list[tuple[int, str]], selected: set[str]) -> tuple[str, int, str, int]:
    bits = [int(author in selected) for _, author in notes]
    first = [sum(bits[offset + i] << i for i in range(5)) for offset in (0, 5, 10, 15)]
    word = ''.join(chr(65 + n) if n < 26 else '?' for n in first)
    suffix = sum(bits[20 + i] << i for i in range(4))
    return word, suffix, ''.join(map(str, bits)), sum(bits)


def main(archive: str | None = None) -> None:
    raw = read_evidence('crew/noticeboard-and-desk-notes.txt', archive)
    assert hashlib.sha256(raw).hexdigest() == CREW_SHA256
    notes = [(int(i), author) for i, author in re.findall(
        r'^N(\d{2}) / ([A-Za-z]+) \[censored\]$', raw.decode(), re.M)]
    assert [number for number, _ in notes] == list(range(1, 25))
    authors = list(dict.fromkeys(author for _, author in notes))
    assert authors == ['Jason', 'Emily', 'Zoey', 'David', 'Gabriel', 'Simon']

    source_mails = (10, 11, 13)
    senders = []
    for mailno in source_mails:
        email = read_evidence(f'mail/{mailno:02d}.eml', archive).decode()
        sender = re.search(r'^From: (\w+) \[censored\]', email, re.M)
        assert sender and f'X-Records-Reference: MAIL-{mailno:02d}' in email
        senders.append(sender.group(1))
    assert senders == ['Simon', 'Emily', 'Gabriel']
    selected = set(senders)

    crew, crew_suffix, _, emily_count = decode(notes, {'Emily'})
    assert (crew, crew_suffix, emily_count) == ('CREW', 4, 8)
    word, suffix, bits, weight = decode(notes, selected)
    assert (word, suffix, bits, weight) == (
        'STOW', 14, '010011100101110011010111', 14)

    matches = []
    triple_matches = []
    word_matches = []
    counts = {}
    for size in range(1, len(authors) + 1):
        for combination in itertools.combinations(authors, size):
            name_set = set(combination)
            candidate_word, candidate_suffix, _, candidate_count = decode(notes, name_set)
            counts[size] = counts.get(size, 0) + 1
            if candidate_word == 'STOW' and candidate_suffix == 14:
                word_matches.append(list(combination))
            if candidate_suffix == candidate_count:
                matches.append((list(combination), candidate_word, candidate_suffix))
                if size == 3:
                    triple_matches.append(list(combination))
    assert counts == {1: 6, 2: 15, 3: 20, 4: 15, 5: 6, 6: 1}
    assert matches == [(['Emily', 'Gabriel', 'Simon'], 'STOW', 14)]
    assert triple_matches == [['Emily', 'Gabriel', 'Simon']]
    assert word_matches == [['Emily', 'Gabriel', 'Simon']]

    print(json.dumps({
        'source_crew_sha256': CREW_SHA256,
        'source_mail_numbers': list(source_mails),
        'source_mail_senders': senders,
        'prior_singleton_emily': f'{crew}{crew_suffix}',
        'selected_union_mask': bits,
        'selected_union_notes': weight,
        'selected_union_decode': f'{word}{suffix}',
        'nonempty_author_subsets': sum(counts.values()),
        'three_author_subsets': counts[3],
        'suffix_equals_selected_note_count_hits': len(matches),
        'unique_suffix_count_match': matches[0],
        'exact_STOW14_hits_all_subsets': len(word_matches),
        'K08_final_phrase': None,
        'K08_original_commitment_evaluated': False,
    }, sort_keys=True, indent=2))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
