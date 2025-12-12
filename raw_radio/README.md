# Raw Radio Data Directory

## Purpose
This directory contains raw radio frequency recordings used for lightning detection and superbolt analysis.

## Expected File

### HDSDR_20250724_020642Z_1468kHz_RF.wav
- **Description:** HDSDR (High Definition Software Defined Radio) recording of lightning radio emissions
- **Frequency:** 1468 kHz (VLF/LF range - typical for lightning detection)
- **Timestamp:** 2025-07-24 02:06:42 UTC
- **Event Type:** Superbolt radio signature detection
- **Status:** **PLACEHOLDER** - File not yet present in repository

## Data Source
Lightning radio emissions are typically captured using:
- Software-defined radio (SDR) receivers
- VLF/LF antennas optimized for atmospheric electromagnetic phenomena
- HDSDR recording software for high-quality RF capture
- Sample rates: typically 48-192 kHz for VLF/LF monitoring

## Usage
The radio intake script (`radio_intake_test.py`) processes WAV files from this directory to:
1. Analyze radio frequency characteristics
2. Detect superbolt signatures (extremely high amplitude events)
3. Calculate energy metrics
4. Generate RADIO_IMPACT capsules for verified detections

## File Naming Convention
`HDSDR_YYYYMMDD_HHMMSSz_FreqkHz_RF.wav`

Where:
- YYYYMMDD: Date of recording
- HHMMSS: Time of recording (UTC)
- Freq: Center frequency in kHz
- RF: Radio Frequency designation

## Data Integrity
All radio data files should be accompanied by:
- Metadata file with recording parameters
- Calibration information
- Source attribution
- Time synchronization details (GPS preferred)

## Academic Standards
Per repository policy:
- All data must be from verified sources
- No synthetic or simulated data without explicit labeling
- Proper attribution for all contributed recordings
- Compliance with electromagnetic spectrum monitoring regulations

---

**Note:** This directory structure is prepared for future radio data integration. When actual HDSDR recordings become available, they will be placed here for processing by the intake system.
