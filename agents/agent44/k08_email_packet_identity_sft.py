"""K08 exact-source retrieval SFT: native-export email spans and direct spool carriers.

Read-only, Python standard library only. Run from a workplace-v2 checkout:
    python agents/agent44/k08_email_packet_identity_sft.py
"""
import hashlib
import hmac
import json
import re
from email import policy
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resources"
MAIL = RES / "evidence" / "mail"

EXPECTED = {
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "route": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "spool": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "mail_manifest": "a96c73a0913e518af06afea06324dd4479e89fa41c753f9b93c81df1db89b3e1",
}


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def contiguous_spans(text: str):
    words = normalize(text).split()
    for start in range(len(words)):
        for end in range(start + 1, len(words) + 1):
            yield " ".join(words[start:end])


def mail_manifest(paths):
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


acceptance_raw = (RES / "acceptance.json").read_bytes()
route_raw = (RES / "evidence" / "recovery-routing.json").read_bytes()
spool_raw = (RES / "evidence" / "print" / "spool-reconstruction.log").read_bytes()
assert hashlib.sha256(acceptance_raw).hexdigest() == EXPECTED["acceptance"]
assert hashlib.sha256(route_raw).hexdigest() == EXPECTED["route"]
assert hashlib.sha256(spool_raw).hexdigest() == EXPECTED["spool"]
acceptance = json.loads(acceptance_raw)
route = json.loads(route_raw)
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
k08_target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
assert k08_target.hex() == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"

# Test every contiguous normalized phrase span in every surviving EML subject/body.
mail_paths = sorted(MAIL.glob("*.eml"))
assert len(mail_paths) == 20
assert mail_manifest(mail_paths) == EXPECTED["mail_manifest"]
seen = {}
span_occurrences = 0
mail_hits = []
for path in mail_paths:
    message = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    assert not message.is_multipart()
    assert message.get_content_type() == "text/plain"
    assert not message.get_filename()
    segments = [("subject", str(message.get("Subject", ""))), ("body", message.get_content())]
    for segment_name, segment_text in segments:
        for phrase in contiguous_spans(segment_text):
            span_occurrences += 1
            if phrase in seen:
                continue
            seen[phrase] = (path.name, segment_name)
            component = hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]
            if sha256(component) == k08_target:
                mail_hits.append((path.name, segment_name, phrase, component.hex()))

# Exercise the same email-span/HMAC/commitment path with a planted synthetic phrase.
planted_phrase = "A distinct original witness preserves the final keeper envelope wording"
planted_component = hmac.digest(nonce, normalize(planted_phrase).encode("utf-8"), "sha256")[:16]
planted_target = sha256(planted_component)
planted_mail_hit = any(
    sha256(hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]) == planted_target
    for phrase in contiguous_spans("Header text. " + planted_phrase + " trailing control.")
)
assert planted_mail_hit

# Test whether an intact 16-byte spool packet is itself the K08 component.
# Exclude the disputed K04 ACK2 by selector fields before reading its PAYLOAD.
header_re = re.compile(rb"JOB=([^ ]+) ATTEMPT=(\d+) STATE=([^ ]+) CLASS=([^ ]+)")
payload_re = re.compile(rb"PAYLOAD=([0-9A-F]{32})")
selected = (b"PS-261003-0417", b"2", b"ACK", b"RECOVER")
selected_indices = []
selected_record_indices = []
packets = []
record_index = 0
for index, line in enumerate(spool_raw.splitlines()):
    header = header_re.search(line)
    if not header:
        continue
    selector = (header.group(1), header.group(2), header.group(3), header.group(4))
    if selector == selected:
        selected_indices.append(index)
        selected_record_indices.append(record_index)
        record_index += 1
        continue
    payload_match = payload_re.search(line)
    assert payload_match
    packets.append((index, header.group(1).decode(), int(header.group(2)), header.group(3).decode(),
                    header.group(4).decode(), bytes.fromhex(payload_match.group(1).decode())))
    record_index += 1
assert selected_indices == [130]
assert selected_record_indices == [129]
assert len(packets) == 132
assert sum(row[4] == "LABEL" for row in packets) == 52
assert len({row[5] for row in packets}) == 132
packet_hits = [
    (index, job, attempt, state, klass, payload.hex())
    for index, job, attempt, state, klass, payload in packets
    if sha256(payload) == k08_target
]

# Exercise the same direct-packet candidate loop with a planted synthetic component.
planted_packet = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
planted_packet_target = sha256(planted_packet)
planted_packet_hits = [p.hex() for p in [row[5] for row in packets] + [planted_packet]
                       if sha256(p) == planted_packet_target]
assert planted_packet_hits == [planted_packet.hex()]

print(json.dumps({
    "mail": {
        "messages": len(mail_paths),
        "mime_parts_per_message": "single text/plain; no attachments",
        "subject_body_segments": 40,
        "span_occurrences": span_occurrences,
        "unique_normalized_spans": len(seen),
        "complete_K08_HMAC_component_matches": mail_hits,
        "planted_positive": planted_mail_hit,
    },
    "spool": {
        "selected_K04_record_index_excluded_by_header_before_payload_read": selected_record_indices,
        "selected_K04_source_line_index": selected_indices,
        "intact_packets": len(packets),
        "intact_LABEL_packets": sum(row[4] == "LABEL" for row in packets),
        "unique_intact_payloads": len({row[5] for row in packets}),
        "direct_K08_component_matches": packet_hits,
        "planted_positive": planted_packet_hits,
    },
    "K08_target_sha256": k08_target.hex(),
    "source_sha256": EXPECTED,
}, indent=2))
