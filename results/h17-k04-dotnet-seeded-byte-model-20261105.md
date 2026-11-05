# Conditional legacy .NET printer-byte model (5 November 2026)

A newly examined producer hypothesis is a **fresh classic .NET Framework System.Random(int)** invocation for each 16-byte printed packet, optionally after up to 64 discarded draws. Source does not identify this implementation. The test is conditional.

Methods: A port of Microsoft's historical subtractive generator tests the seed's empirical affine relationship at three source-visible output positions. A full 16-byte recomputation checks every candidate remaining after the three-byte filter. Original source `resources/evidence/print/spool-reconstruction.log` is SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

Synthetic test records from 6 known sample seeds were recovered in the direct form, and offset examples at 0, 11, 31 and 64 passed. For original ordinary printer row zero, all **65 offsets in both byte directions** yielded zero exact 16-byte matches, **130 distinct cases**. Additional original rows 1,63,127 likewise yielded no direct-offset match.

The affine observation was independently sampled across 20,000 seeded histories but has **not been proven for every integer seed**. Therefore this is a strong conditional source-model negative rather than an unconditional mathematical exclusion. Further hidden offsets, alternate byte transforms, other runtime RNGs and selected-event-only generators remain open.

Reproducibility:
- `agents/agent4/k04_dotnet_seedbyte_inversion_sft.py`
- `agents/agent4/k04_dotnet_seedphase_inversion_sft.py`

**Archive status:** K01/K02/K03/K05/K06/K07 PASS, K04/K08 unresolved, combined INCOMPLETE. No original historical component bytes recovered.
