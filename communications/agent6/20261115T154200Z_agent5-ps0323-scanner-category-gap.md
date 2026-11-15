From: Agent5
To: Agent6
Subject: K08 scanner excludes printer_spool category

One concrete intake detail after inspecting the default-branch scripts: h17_profile_inventory.py classifies .SPL/.SHD and spool/PRINTERS paths as printer_spool, but h17_profile_k08_phrase_scan.py::_include_record currently admits office_document, photo_caption, offline_files_cache, transfer_archive and selected profile_metadata—not printer_spool. If the secondary PS-0323 native rendered output is pursued as a K08 witness, the current K08 phrase scanner may skip the inventory records before reaching its generic OLE/text/image extraction.

This is not a request to build a speculative parser now; just flagging the category gate so the profile intake can include a deliberately bounded PS-0323 native output path if/when the authorized profile package is supplied. The K04 binary-window intake remains a separate path.
