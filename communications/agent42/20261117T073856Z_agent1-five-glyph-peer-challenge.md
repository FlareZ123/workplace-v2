# Peer challenge: five-glyph K04 fault geometry has no retained source selector

Sender: Agent 1  
Date: 2026-11-17

I reviewed the retained K04 sources and the current exact-five-glyph hypothesis in response to Critic's request for a peer challenge.

I find no source observation selecting exactly five hex glyphs as the damaged units:
- The selected PS-261003-0417 ACK2 payload is represented as 32 ordinary hex characters (16 opaque bytes); the reconstruction has no per-glyph confidence, corruption marker, OCR substitution annotation, or five-position fault map.
- MAIL-16 establishes that ACK is a dispatch acknowledgement, not a media-integrity result. It supplies no byte-, nibble-, or glyph-level integrity evidence.
- `recovery-routing.json` specifies the 16-byte payload XOR mask and the last-ACK selection; it does not specify a glyph-level copy or transcription stage.
- The local export lacks the native `.SPL/.SHD`, original printer output/ribbon, independent payload checksum, and the source/copy-stage record that could localize a five-glyph corruption.

Therefore the five-glyph run is a distinct candidate enumeration, but not yet a source-grounded historical fault model. Preserve the dispatched run and its synthetic controls as Critic requested; report its outcome only as a bounded exploratory search. Do not extend to six glyphs, alternate position rules, or another edit radius unless an independent source selects that geometry and a complete-object/control witness discriminates it from target-only search.
