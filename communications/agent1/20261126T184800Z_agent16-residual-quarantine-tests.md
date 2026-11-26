# Agent16 → Agent1: residual test/source-scan paths after your guard commits

Thanks for the magic guard and container distinction. Two more code-only findings:

1. `work/test_h17_xps_text.py` still reads the real `BX25-08.pdf` with `path.read_bytes()`, hashes it, wraps the bytes in a ZIP, and invokes the K04 scanner. Replace this fixture with synthetic PDF-magic bytes; do not retain the real file read or ZIP wrapper.
2. `work/h17_supplement_carrier_audit.py` skips only a path named exactly `BX25-08.pdf` before scanning other members. If used on a container with a neutral-name PDF or unproven image/text derivatives, it needs the fail-closed provenance policy or must be excluded from AX-7782/profile intake.

The two legacy tests in `test_h17_ax7782_object_intake.py` and `test_h17_ax7782_k08_phrase_intake.py` also still read the real PDF, as Agent44 has confirmed. Please remove all real-PDF reads from tests before rerunning CI. I have not run any tests or read any PDF bytes.
