"""H17 K08: audit quotation and original-terminal-text transport in exported email.

This is a source-only transport test, not a guess at a missing author caption.
Run: python agents/agent48/k08_mail_quote_version_transport_sft.py
"""
from email import policy
from email.parser import BytesParser
from hashlib import sha256
from pathlib import Path
import json
import re
import sys

PINS = {
    "evidence/records-custodian.txt": "786211e7be248e6ba31f017a071e038436782b8550b863f85d77a6c32e1d640a",
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "evidence/mail/11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "evidence/mail/20.eml": "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71",
    "evidence/mail/INDEX.md": "3fe9b6f14cf23d0f8f0b6ea5ed02230242aaa6b9949c0d6845b57eb8aa85659b",
}


def main(root):
    for relative, expected in PINS.items():
        assert sha256((root / relative).read_bytes()).hexdigest() == expected, relative

    mail = root / "evidence/mail"
    files = sorted(mail.glob("*.eml"))
    assert [path.stem for path in files] == [f"{i:02d}" for i in range(1, 21)]
    totals = {"multipart": 0, "attachment_headers": 0,
              "in_reply_to": 0, "references": 0,
              "quoted_prefix_body_lines": 0, "quoted_forward_headers": 0}
    reply_subjects = []
    surviving_caption_related = []
    normalized_re = re.compile(r"\b(?:caption|keeper|desk phrase|final phrase|envelope|margin)\b",
                               flags=re.I)
    for path in files:
        email = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
        assert email.get("X-Records-Reference") == f"MAIL-{path.stem}"
        assert email.get_content_type() == "text/plain", path
        assert not email.is_multipart(), path
        content = email.get_content()
        if str(email.get("Subject", "")).startswith("Re: "):
            reply_subjects.append(path.stem)
        if normalized_re.search(content):
            surviving_caption_related.append(path.stem)
        totals["multipart"] += email.is_multipart()
        totals["attachment_headers"] += int(any(
            item in email for item in ("Content-Disposition", "Content-ID")
        ))
        totals["in_reply_to"] += "In-Reply-To" in email
        totals["references"] += "References" in email
        totals["quoted_prefix_body_lines"] += sum(
            line.lstrip().startswith(">") for line in content.splitlines()
        )
        totals["quoted_forward_headers"] += sum(
            bool(re.search(r"^(?:Forwarded message|Begin forwarded message|On .+ wrote:)",
                           line, flags=re.I))
            for line in content.splitlines()
        )

    assert reply_subjects == ["06", "17"], reply_subjects
    assert all(v == 0 for v in totals.values()), totals
    assert "11" in surviving_caption_related and "20" in surviving_caption_related
    for index in ("11", "20"):
        e = BytesParser(policy=policy.default).parsebytes((mail / f"{index}.eml").read_bytes())
        assert e.get("In-Reply-To") is None
        assert e.get("References") is None

    note = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_text()
    assert "N13 / Emily" in note and "N23 / Emily" in note
    assert "The wording in my margin was never an official slogan." in note
    assert 'The envelope only remembers the words I finally put on it.' in note
    print(json.dumps({
        "original_email_count": len(files),
        "original_email_structure": totals,
        "reply_subjects": reply_subjects,
        "caption_topic_emails": surviving_caption_related,
        "caption_descriptive_mail11_and_mail20": "no reply/forward chain or quoted final inscription",
        "N23_final_margin_reference": "final inscription is described, not transcribed",
        "scope": "surviving plain-text exported headers and body markup only",
        "conclusion": "NO_EXPLICIT_SURVIVING_LITERAL_TERMINAL_QUOTATION_POINTER",
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else
         Path(__file__).resolve().parents[2] / "resources")
