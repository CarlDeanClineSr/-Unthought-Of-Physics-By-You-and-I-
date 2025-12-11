# Teaching Capsule #001 – Starting Verified Truth
**Date:** 2025-12-11
**Status:** [Verified]
**Author:** Carl Dean Cline Sr

## Verified Statement
The LUFT program observes real-time solar wind parameters (Bz, proton density, velocity, temperature) and GOES X-ray flux using NOAA primary sources.

The intake system v0.7.0 pulls, validates, and archives these parameters with:
- 5-minute cadence (configurable)
- SHA-256 integrity hashing on every CSV
- Capsule manifests with schema version and UTC basis
- Threshold-triggered event capsules (HIGH_IMPACT, FLARE, TRIPLE_COINCIDENCE)

This pipeline ran without data loss or fabrication on live NOAA feeds in December 2025.

**Evidence:**
- Repository: integration/intake-vault (submodule SHA will be recorded in git)
- Scripts: scripts/data_intake_v0.7.0.py
- Sample output: capsules/ and raw_csv/ directories

## Next Unthought-Of Question (to be tested in workshop)
When proton density ≥ 25 cm⁻³ and Bz ≤ –10 nT coincide with X-ray flux ≥ 2×10⁻⁶ W/m², does the observed curl residual (Δ) align in direction and magnitude with the predicted lattice correction C_luft = μ₀ α × n̂ ?

Test harness armed in v0.7.0 CLUFT_DEVIATION capsule.

**Teaching chain begins here. No forward claim until the sky answers.**
