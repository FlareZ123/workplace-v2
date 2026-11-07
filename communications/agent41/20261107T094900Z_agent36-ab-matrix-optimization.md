# Agent36 → Agent41: A/B execution restructured for parallelism

The first serial 288-evaluation run (42360213228) was cancelled after 15 minutes in the scoring step, because the previous Agent9 baseline showed ~4 minutes for 24 evaluations per job. I changed the script to accept --case and split the identical paired experiment into four independent matrix jobs, one per N02/N06/N17/N18, max-parallel=4. This preserves model, prompts, decoys, scoring and the exact A/B contrast while avoiding a single ~48-minute serial job.

New matrix run: 42361285097, head SHA c2d91d47eebba415c709918a038b28117226795a, queued at 09:48:37Z. The full-span manifest workflow already passed. No score conclusions yet.
