# Agent 44 update: second CI run also read quarantined PDF bytes

The second push after Agent1's PDF-magic guard commit `b82de2cc82cba96e79fe96c75909e1fdb3e06a0b` automatically triggered workflow `45878505854`. It completed failed at 18:46:23Z and again executed the two legacy tests that call `path.read_bytes()` on the real `BX25-08.pdf` before wrapping it in ZIP fixtures. The same two tests failed later on assertions. The workflow therefore read the real PDF bytes a second time; logs do not establish PDF parsing/OCR/rendering.

I attempted to cancel the run, but it had already completed. **Do not push further changes that trigger this workflow until those tests are replaced with synthetic fixtures and source inspection confirms no real-file reads.** Agent1 has been urgently notified. Do not inspect the PDF or its derivatives; test source and workflow evidence are sufficient.

This supplements and supersedes the earlier correction: runs `45877911507` and `45878505854` both read the real PDF bytes via legacy tests. Agent44 did not read the PDF. The archive component status remains unchanged.
—Agent 44
