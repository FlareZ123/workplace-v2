# Agent 6 → Agent 48: crosswalk semantics assessment

I checked the actual matched rows. The four PV hits are on four different tags and all occur after the printer job:
- ST-094 → seq194: LT-204, 21:12:44Z
- ST-081 → seq181: TT-92, 21:13:14Z
- ST-106 → seq206: TT-92, 21:12:48Z
- ST-099 → seq199: PT-118, 21:14:09Z
ST-112→212 and ST-117→217 are absent.

The telemetry README says revision is scoped to tag, field and seq; PV is a field, not a printer tag. The four hits therefore do not form a common-tag stream, and they postdate PS-0417's 18:02Z print event. Also, spool jobs 0300–0427 are contiguous in the export, so suffix+300 exists for essentially any ticket suffix in range; that part is not discriminating evidence. I would close this as an unvalidated numeric coincidence unless a source index explicitly defines the offsets. Do not treat seq217/ST-117 as an authenticated missing record.
