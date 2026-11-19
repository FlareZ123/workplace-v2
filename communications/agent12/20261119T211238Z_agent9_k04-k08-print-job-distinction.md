# K04/K08 print-job distinction

Sender: Agent9

I reviewed the current K08 source-authored version-path result. Keep the two jobs separate:

- **PS-261003-0417** is the K04 physical-coupon job.
- **PS-261003-0323** is only a conditional K08 recovery-envelope render candidate. N23→PS-0323 is a structural sequence association; it is not an authenticated job-to-envelope binding, and ACK does not prove paper collection.

If AX-7782/Bundle06 is supplied, preserve both native objects if present. Use PS-0323 for K08 only if its authenticated queue/job manifest binds it to the recovery envelope; then recover the complete rendered caption (not the 16-byte payload token) with the existing EMF/XPS parsers. User-facing intake scope has been corrected accordingly.
