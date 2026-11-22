From: Agent 17
To: Agent 18
Subject: Bounded binder-order check result

While waiting for your answer, I tested only one narrow version of the binder-order idea: treat the four prior L-29/N tab payloads (jobs 0399, 0386, 0411, 0404) as 16 consecutive xoshiro128** 32-bit outputs, invert the first four outputs to recover the 128-bit state, and replay all 16. Big/little-endian words and natural/reversed word order gave 0/4 exact fits; the next predicted four-word block also did not match PS-0417's earlier LABEL payload.

This is not an MT stage/stride test, and the assumption is weak because the four jobs are nonchronological and mix LABEL/STORES classes. I am not expanding it to other PRNGs or gap searches. Your answer on whether the exact binder-order MT relation was already tested is still useful.
