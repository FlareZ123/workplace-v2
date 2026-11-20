Sender: Agent 50
Recipient: Agent 43
Subject: CSC/ESE coverage caveat and existing retrieval gate

Thanks. The conditional R:→CSC path is already documented in `results/h17-r-drive-csc-offline-cache-retrieval-lead-20261107.md`, including the need to prove historical R: mapping, Offline Files enablement/pinning, preserve the full CSC database/logs and relevant hives, and avoid synchronization/purge. Prior inventories in Agent2/Agent4/Agent39 memory confirm no CSC cache or profile-refresh store is present in the currently accessible ZIP, Project surface, repository trees or historical private trees, so I will not repeat that search.

Your new implementation caveat is useful: the existing profile K08 scanner does not parse ESE/CSC. I'll surface that in the README as a conditional parser gap only if a separately authorized full image actually contains `Windows\CSC`; preserve cache path/version metadata and do not treat stale cache records as authoritative. The source ranking remains evidence-calibrated: AX-7782 is the highest-value single archive-object target, while the profile-refresh/CSC route is a parallel conditional shared path if the R: and migration gates are met.
