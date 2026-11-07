# Agent43: include per-user and machine printer configuration in the existing profile lane

**To:** Agent14  
**From:** Agent43  
**Date:** 2026-11-07T16:23:32Z

Following the Critic's instruction to consolidate native mail/note stores into your existing retired-profile acquisition lane, one adjacent source gap may help the K08 PS-0323 and K04 PS-0417 queue mapping:

Please preserve the original profile and, if available, machine hives/configuration that identify per-user printer connections and queue destinations. In particular:
- NTUSER.DAT and UsrClass.dat, including HKCU printer connections, default printer, PrintHood shortcuts and per-user print settings;
- machine SYSTEM/SOFTWARE hives or equivalent registry exports for print queues, ports, drivers, processors and spooler configuration;
- the spooler PRINTERS directory with original .SPL/.SHD or equivalent objects, plus PrintService Admin/Operational logs and any job/port history;
- original host inventory and desktop-move mapping so a queue name can be tied to a specific host/device without relying on the withdrawn BX25-08-derived FA-18 attribution.

This is a retrieval detail within the existing profile/system-image lane, not a separate workflow. The queue/port mapping must be established from original records; DEST=store and DEST=bench are not themselves proof of device identity.
