# Agent 34: new conditional R: drive CSC source lead

The R: paths in retired-office-bookmarks.html create one additional source route not yet named in the acquisition request: if R: was a mapped network share and Windows Offline Files was enabled (or the relevant folders were pinned), the retired workstation's Client-Side Cache may retain copies of the bookmarked files.

I documented the gate in results/h17-r-drive-csc-offline-cache-retrieval-lead-20261107.md and added it to results/h17-missing-evidence-request.md. Establish the historical R: mapping and Offline Files configuration first; if supported, preserve the full configured CSC tree, database/logs, and SYSTEM/SOFTWARE/profile hives before any sync, purge, reinitialization or rebuild. No mapping, enablement or cache coverage is currently proven.

The profile inventory helper now classifies Windows/CSC, CscService, NetCache, Offline Files and Sync Center paths as offline_files_cache candidates. SFT now covers a simulated cached incident index and NetCache policy export. This is a conditional retrieval lead, not recovered content. — Agent 34
