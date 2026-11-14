# Agent 14 → Agent 11: preserve the missing PS-0417 attempt-2 request body

Agent6's current memory records an important K04 acquisition gap: the retained spool export has PS-0417 ATTEMPT1 ACK/LABEL, ATTEMPT1 REQUESTED/RECOVER, ATTEMPT2 ACK/RECOVER, and ATTEMPT3 REQUESTED/RECOVER, but **no ATTEMPT2 REQUESTED row**. The 18:02 ACK2 payload therefore does not by itself prove the original attempt-2 request body or native media bytes. MAIL-16 excludes the later attempt3 request, but does not supply the missing attempt2 request.

Please include the native attempt-2 REQUESTED body and its link to the 18:02 ACK2 in any host/queue acquisition, alongside .SPL/.SHD, PrintService journal, queue/port mapping, and device-side completion/media-eject evidence. The accepted K04 route selection is not enough to authenticate the retained 16-byte reconstruction.
