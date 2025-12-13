# cern_bridge_reporter.py
# Auto-run CERN χ analog hunt + generate capsule summary

import uproot
import numpy as np
import matplotlib.pyplot as plt
import datetime

# Same small public dataset
url = "root://eospublic.cern.ch//eos/opendata/cms/mc/RunIISummer20UL16MiniAOD/QCD_Pt-15to7000_TuneCP5_Flat_13TeV-pythia8/MINIAODSIM/106X_mcRun2_asymptotic_v17-v1/270000/005F8E94-0B5E-0E4D-9F0B-2B2C9F5E1E8E.root"
events = uproot.open(url + ":Events")
jet_pt = events["Jet_pt"].array(library="np")
leading_pt = np.array([pts[pts.argmax()] if len(pts) > 0 else 0 for pts in jet_pt])
chi_analog = leading_pt / leading_pt.max()

# Plot
plt.figure(figsize=(10, 6))
plt.hist(chi_analog, bins=100, range=(0, 1), density=True, alpha=0.7, color='purple')
plt.axvline(0.15, color='gold', linestyle='--', linewidth=2, label="Solar Wind χ Ceiling (0.15)")
plt.axvline(chi_analog.max(), color='red', linestyle='-', linewidth=2, label=f"Observed Max: {chi_analog.max():.4f}")
plt.title("CERN χ Analog: Normalized Leading Jet pT (Bridge Test #1)")
plt.xlabel("Normalized Amplitude")
plt.ylabel("Density")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("cern_bridge_test_plot.png")
plt.close()

# Auto-generate capsule text
max_chi = chi_analog.max()
status = "Potential Bridge" if abs(max_chi - 0.15) < 0.05 else "No Clear Bridge Yet"

capsule_md = f"""
# Teaching Capsule – CERN χ Bridge Test #001 (Auto-Generated)

**Run Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M UTC')}  
**Observed Max χ-analog:** {max_chi:.6f}  
**Status:** {status}

## Plot
![CERN Bridge Test Plot](cern_bridge_test_plot.png)

## Quick Verdict
- If observed max ≈ 0.15 (±0.05): Possible universal ceiling echo.
- Otherwise: Domains differ — next test needed.

**Next Run:** Change dataset or metric to probe deeper.

**End of Auto-Capsule**
"""

with open("capsules/auto_cern_bridge_001.md", "w") as f:
    f.write(capsule_md)

print("CERN Bridge Test complete!")
print(f"Max normalized amplitude: {max_chi:.6f}")
print("Plot saved + capsule written to capsules/auto_cern_bridge_001.md")
