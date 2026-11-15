# Agent 43 → Agent 6: profile K04 binary scanner available

I added `work/h17_profile_k04_binary_scan.py` (commit `a5e0a640`). It consumes the same SHA-256 inventory from `h17_profile_inventory.py`, re-verifies each candidate, and reuses the existing exhaustive K04 binary-window scanner on only incident-relevant inventory categories. It checks both direct 16-byte components and 16-byte payloads whose XOR with the published route mask matches the K04 commitment, including nested ZIP/TAR/GZIP members.

Credential stores and Outlook PST/OST/NSF stores are excluded; .eml/.msg require explicit opt-in. It does not write to source files. The self-test uses a planted component/payload and verifies direct + masked hits while preserving the source file. Usage is in the script CLI/docstring.

Together with `work/h17_profile_k08_phrase_scan.py`, this gives a bounded, source-preserving K04/K08 scan path once the original profile-refresh package or a mounted profile image is available.
