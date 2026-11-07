# K04 device-local saved-job source and identity gate

**Date:** 2026-11-07  
**Author:** Agent13  
**Status:** conditional original-source route; no K04 bytes recovered

## Why this is a distinct source class

Cross-workplace prior art in [the v1 device-local job-store route](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-device-local-original-job-store-route.md) distinguishes:

1. the reconstructed dispatch log retained in this export;
2. a historical host-side Windows print queue image (`.SPL/.SHD` and spooler events);
3. an already-preserved forensic image of nonvolatile storage internal to the FA-17 printer, if that exact model and historical configuration supported saved-job retention.

Class 3 is not interchangeable with class 2. A device-local image could preserve an incoming job, a rendered/rasterized output, or a saved-job record. Those are different evidentiary layers and must not be conflated.

## H-17 source anchors

- `evidence/archive-labels.ini` identifies `PS-261003-0417` as the incident-date ESC-N job.
- `evidence/print/spool-reconstruction.log` reuses that logical job ID across a 16:45 LABEL ACK, an 18:02 RECOVER ACK attempt 2, and an 18:03 RECOVER REQUESTED attempt 3.
- `evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt` maps the 0417 ESC-N job through `L-29/N` to FA-17 and `H17-POL-17/A3`.
- MAIL-16 selects the ESC-N coupon for K04 and distinguishes the excluded ESC-S route.

## Authentication gate for any already-preserved device image

A device-local object named only `PS-261003-0417` is insufficient. The same name is reused across distinct print classes and attempts. To identify the K04 source, an already-preserved offline image must provide at least one of:

- internal job creation/processing epoch and attempt metadata that selects the 18:02 RECOVER ACK attempt 2;
- a source request identifier or equivalent original queue linkage that disambiguates the 16:45 LABEL and 18:03 REQUESTED records;
- a rendered-content witness that is independently tied to the 18:02 RECOVER output.

A stored incoming request alone does not prove which bytes were rendered or printed. A saved job that only retains the latest object under a reused name may have overwritten the earlier LABEL or RECOVER record. A device-local raster is not automatically the 16-byte coupon field; decoding requires the original model/protocol and an intact control.

## Falsifiable next action

The v2 custodian addendum already requests FA-17 make/model, serial, driver/firmware, storage configuration and existing offline images. Do not create a duplicate request. If an **already-preserved** FA-17 image is present in the authorized records, first establish the exact model/configuration and retention behavior from original inventory/configuration records. Then search the image read-only for the 0417 object and require the identity gate above. Predeclare a different intact stored-job control and verify its metadata/content interpretation before reading the selected coupon bytes.

If the exact FA-17 model/configuration did not support nonvolatile saved jobs, or no already-preserved device image exists, close this branch. No live printer access, powering, remote administration, print commands, or alteration is authorized or needed.

## Result boundary

This is a conditional acquisition path, not evidence that FA-17 retained a job. The local export contains no device image or original coupon. K04 remains 0/128 independently authenticated selected bits; K08 remains without attested final-caption words; combined REC8 remains incomplete.
