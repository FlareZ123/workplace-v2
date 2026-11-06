# Agent 5: question on v3 control-job shutdowns

**6 November 2026, 16:33 UTC.** In run `42249717424`, cases 0, 2, 6 and 18 have ended with runner shutdown / exit 143, not Python exceptions; case 17 remains active. The case-2 log shows the model loaded successfully and then ran until shutdown, with no inference exception.

Were these jobs intentionally cancelled? If not, I can split each control's A/B stream into separate jobs to keep each run shorter. I have not launched a replacement control workflow.
