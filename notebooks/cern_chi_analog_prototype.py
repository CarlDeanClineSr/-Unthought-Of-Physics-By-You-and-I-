# cern_chi_analog_prototype.py
# Prototype: Hunt for χ-like saturation in CERN Open Data QCD jets
# Target: Normalized leading jet pT response — does it cap like solar wind χ = 0.15?

import uproot  # pip install uproot awkward (if needed locally)
import numpy as np
import matplotlib.pyplot as plt

# Real small public CMS QCD jet sample from CERN Open Data Portal
# Direct link to a manageable file (~200 MB ROOT)
url = "root://eospublic.cern.ch//eos/opendata/cms/mc/RunIISummer20UL16MiniAOD/QCD_Pt-15to7000_TuneCP5_Flat_13TeV-pythia8/MINIAODSIM/106X_mcRun2_asymptotic_v17-v1/270000/005F8E94-0B5E-0E4D-9F0B-2B2C9F5E1E8E.root"

# Open remotely and access the tree
events = uproot.open(url + ":Events")

# Pull leading jet pT (transverse momentum) — proxy for "driver response"
# In real runs, expand to subleading jets, multiplicity, etc.
jet_pt = events["Jet_pt"].array(library="np")  # All jets per event
leading_pt = np.array([pts[pts.argmax()] if len(pts) > 0 else 0 for pts in jet_pt])

# Normalize to hunt for universal ceiling (like χ / χ_max)
chi_analog = leading_pt / leading_pt.max()

# Plot histogram for saturation check
plt.figure(figsize=(10, 6))
plt.hist(chi_analog, bins=100, range=(0, 1), density=True, alpha=0.7, color='purple')
plt.axvline(0.15, color='gold', linestyle='--', linewidth=2, label="Solar Wind χ Ceiling Reference (0.15)")
plt.title("Prototype χ Analog: Normalized Leading Jet pT in CERN QCD Events")
plt.xlabel("Normalized Amplitude (leading jet pT / max)")
plt.ylabel("Density")
plt.legend()
plt.grid(alpha=0.3)
plt.show()

print(f"Events processed: {len(leading_pt)}")
print(f"Max normalized amplitude observed: {chi_analog.max():.6f}")
print("If a hard cutoff appears near 0.15 (or scaled), that's the bridge signal.")
