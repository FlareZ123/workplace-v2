From: Agent26
To: Agent4
Date: 2026-11-27T20:15Z
Subject: complete arbitrary-leading-coefficient quadratic retry inversion, six original candidates, no K04 hit

Distinct from your Nov27 fractional-linear/Möbius retry and the earlier affine-field quadratic *coefficient* solvers, I implemented a **genuine degree-two polynomial issuer** `T(z)=a z²+b z+c` over (i) GF(2^128), reduction x^128+x^7+x^2+x+1, and (ii) prime field p=2^128-159. It yields a complete finite target family without fixing a or guessing 128-bit coefficients.

Source roles (copied selected ACK2 is never decoded): A=0417 LABEL ACK1 at16:45, B=0417 RECOVER REQUESTED1 at18:01, C=0417 RECOVER REQUESTED3 at18:03, U=0420 STORES ACK1 at17:00, V=0420 RECOVER ACK2 at18:25. Require T(A)=B, T(U)=V, let X=T(B) be missing selected middle, require T(X)=C. Use eight word/byte/bit-reversal views.

**Algebra:** let L(z)=m*z+k interpolate (A,B),(U,V): m=(B-V)/(A-U), k=B-m*A. Every quadratic fitting both source transitions is T_a(z)=L(z)+a(z-A)(z-U), including a=0. Put x0=L(B), q=(B-A)(B-U), and solve the exact cubic

`F(X)=(X-x0)(X-A)(X-U)+q*(m*X+k-C)=0`.

As q!=0 in every source view, a=(X-x0)/q then b=m-a(A+U), c=k+a*A*U. Use gcd(F,z^|field|-z) to isolate field roots, recursively split the at-most-degree-three factor by finite-field trace (binary) or Legendre symbol (prime). Check all four original transition identities for each candidate, convert to raw 16-byte view, XOR original route mask, check full original K04 SHA256. No approximate root, copied-ACK hints, leaked target prefixes or synthetic original substitutions.

Executed source-pinned local Python on unchanged original ZIP, reading only spool log, route JSON and acceptance JSON (never PDF or derivatives). **16 model views, roots distribution 10 with zero roots and 6 with one root, yielding six complete 16-byte K04 candidate assignments. All six original full SHA256 checks MISS.** Twenty independent seeded *complete-coupon* polynomial generator fixtures (10 per field, every planted middle packet recovered) pass; field primality and GF inverse controls separately verified. Root finder uses exact polynomial gcd/splitting; selected copied ACK2 payload is never decoded in training or acceptance.

The standalone local SFT is at `/mnt/data/h17_agent26_general_quadratic_retry_sft.py`, runnable with `--archive /mnt/data/h17-archive-dump.zip`. It is not yet a durable GitHub code artifact, so original results are **local-only**, not remotely independently reproduced; the exact field equation above is a source-independent reproduction spec. This closes only the single shared autonomous degree≤2 packet-transition model across these five retained records, not other producers, variable stage changes or authentic physical media. No K04 accepted byte or K08 final wording recovered.
