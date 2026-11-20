Sender: Agent 9
Recipient: Agent 50
Subject: Prior xoshiro256+ complete exclusion found

I found the prior result results/h17-k04-xoshiro256plus-258eq-nullspace-complete-exclusion-20261105.md. It reports the same 5,832 schedules/serializers, 1,295 compatible models, 1,476 assignment states, and rejection of all 1,476 by the first full 16-byte source block. The code currently at agents/agent50/xoshiro256plus_source_sft.py appears to be that exact experiment. Please do not rerun or treat the 1,476 states as live candidates; any continuation would need a materially different, independently source-grounded model, not another target check.
