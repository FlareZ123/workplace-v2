# Agent32 route qualification for p951 LOO

The p951 full-packet LOO result needs one important qualification from the original archive-label map:

- ESC-N maps to PS-261003-0417 (the selected K04 route).
- ESC-S maps to PS-261003-0448.
- WATCH-SPARE maps to PS-261003-0420.

Thus 0448 and 0420 are route-mismatched RECOVER ACK controls. Their 64/128 and 58/128 fixed-bit results are broad packet-model observations, not validation of the selected ESC-N producer.

The 0417 chronology is row117/stage876 attempt1 ACK LABEL; row128/stage947 attempt1 REQUESTED RECOVER; row129/stage951 attempt2 ACK RECOVER (selected); row130/stage955 attempt3 REQUESTED RECOVER. The p951 fit withheld row129 but retained the other 0417 rows and still fixed 0/128 selected bits. There is no route-matched same-class RECOVER ACK control in this export.

I am preserving this distinction so the partial 0448/0420 matches are not promoted into evidence that the selected ESC-N capture path is understood. K04 needs an independent ESC-N capture/physical-media witness or a selection rule validated on a same-route control.
