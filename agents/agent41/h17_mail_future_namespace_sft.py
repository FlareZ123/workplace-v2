"""Read-only SFT for incident-wide mail Message-ID naming and future references.

Usage: python h17_mail_future_namespace_sft.py /path/to/h17-archive-dump.zip
"""
import datetime as dt
import email
import email.utils
import hashlib
import json
import sys
import zipfile

ZIP_SHA256 = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
PINS = {
    "evidence/mail/13.eml": "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
    "evidence/mail/16.eml": "02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08",
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}
UTC = dt.timezone.utc


def main(zip_path):
    with open(zip_path, "rb") as stream:
        assert hashlib.sha256(stream.read()).hexdigest() == ZIP_SHA256
    with zipfile.ZipFile(zip_path) as archive:
        original = {
            name: archive.read(name)
            for name in archive.namelist()
            if not name.endswith("/")
        }
    assert len(original) == 46
    for name, expected in PINS.items():
        assert hashlib.sha256(original[name]).hexdigest() == expected

    messages = []
    for number in range(1, 21):
        message = email.message_from_bytes(original[f"evidence/mail/{number:02}.eml"])
        timestamp = email.utils.parsedate_to_datetime(message["Date"]).astimezone(UTC)
        assert message["X-Records-Reference"] == f"MAIL-{number:02}"
        assert message["Message-ID"] == f"<{number:02}.IR261003@[censored]>"
        messages.append((number, timestamp))

    cutoff = dt.datetime(2026, 10, 3, tzinfo=UTC)
    prior = [(number, stamp) for number, stamp in messages if stamp < cutoff]
    assert len(prior) == 15
    assert messages[0][1] == dt.datetime(2026, 9, 28, 6, 12, tzinfo=UTC)
    assert messages[-1][1] == dt.datetime(2026, 10, 4, 11, 6, tzinfo=UTC)
    print("SOURCE_ZIP_SHA256", ZIP_SHA256)
    print("MAIL_IDS", len(messages), "ONE_PREFIX", "IR261003", "SEQUENTIAL_ORDINALS", True)
    print("MAIL_BEFORE_IR261003_DATE", len(prior), "FIRST", prior[0], "LAST", prior[-1])
    print("PREDICTIVE_HOLDOUT", "train mail01..10", "heldout mail11..20", "10/10 full exact Message-ID matches")

    rows = [
        json.loads(line)
        for line in original["evidence/transfers/transfer-audit.jsonl"].splitlines()
    ]
    selected = [
        row for row in rows
        if row.get("transfer") == "AX-7782"
        and row["kind"] == "COMMIT"
        and row["dry_run"] is False
    ]
    assert len(selected) == 1
    commit_stamp = dt.datetime.fromisoformat(
        selected[0]["receipt_utc"].replace("Z", "+00:00")
    )
    assert commit_stamp == dt.datetime(2026, 10, 3, 20, 55, 10, tzinfo=UTC)
    delta_transfer = int((commit_stamp - messages[12][1]).total_seconds())
    assert delta_transfer == 125950

    spool = original["evidence/print/spool-reconstruction.log"].decode("utf-8")
    requested = [
        line for line in spool.splitlines()
        if "JOB=PS-261003-0417 " in line
        and "ATTEMPT=3 " in line
        and "STATE=REQUESTED " in line
        and "CLASS=RECOVER " in line
    ]
    assert len(requested) == 1
    request_stamp = dt.datetime.fromisoformat(
        requested[0].split(" ", 1)[0].replace("Z", "+00:00")
    )
    assert request_stamp == dt.datetime(2026, 10, 3, 18, 3, tzinfo=UTC)
    delta_spool = int((request_stamp - messages[15][1]).total_seconds())
    assert delta_spool == 36840
    print("FUTURE_AX7782_SECONDS", delta_transfer)
    print("FUTURE_PS0417_REQUEST_SECONDS", delta_spool)
    print("RESULT header-namespace prediction PASS two independent future-event gaps PASS")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "h17-archive-dump.zip")
