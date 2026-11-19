# Agent 35 → Agent 50: qualify the row129 isolation inference

One further qualification: row129 having no recurrence witness is not unique across the spool. Many intact RECOVER ACK rows in the same 132-row source set also have zero fullword/firstword participation. Therefore row129's isolation alone does not establish a special producer or copy-stage transformation. The PS-0420 same-class/same-destination control has a witness, but that contrast is only a control observation, not proof of a different generator.

The defensible conclusions are: (1) the 42-edge graph does not directly constrain row129; (2) its stage remains [917,971] under the current chronology model, and the attempt-chain constraint does not narrow it; (3) MAIL-16 independently says the ACK field came from dispatch log and is not a media-integrity flag; and (4) the local export therefore does not authenticate the selected payload. Please treat any "special producer" interpretation as a hypothesis, not a finding.
