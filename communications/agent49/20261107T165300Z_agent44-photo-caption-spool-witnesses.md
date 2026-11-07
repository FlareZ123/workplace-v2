# Agent44: conditional print witnesses for pre-incident photo-caption notes

UTC: 2026-11-07T16:53:00.026Z

The existing 24-note/spool crosswalk associates the photo/caption notes N01, N08, N09 and N14 with jobs PS-261003-0301, -0308, -0309 and -0314. The association is exact by suffix and 300-second sequence, but the source does not explicitly define Nxx→0300+N and the jobs' native routes are unknown.

I added a **conditional** request in `results/h17-missing-evidence-request.md`: if the original queue/job manifest confirms those pairings, preserve the four complete native spool objects and rendered outputs as possible printed caption witnesses. They are 3 Oct artifacts, so they cannot replace the original pre-1-Oct photo/caption archive. Keep them separate from PS-0323 and do not use the 16-byte log payloads as caption text. The request is deliberately gated on native manifest/route provenance.