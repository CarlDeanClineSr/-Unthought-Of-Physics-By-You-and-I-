import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt

# Load CME/χ log
df = pd.read_csv('cme_heartbeat_log_2025_12.csv', parse_dates=['timestamp_utc'])
chi = df['chi_amplitude'].fillna(method='ffill').values

time = np.arange(len(chi))  # uniform spacing assumed for wavelet

# Continuous Wavelet Transform (CWT)
scales = np.arange(1, 128)
coeffs, freqs = pywt.cwt(chi, scales, 'morl')

plt.figure(figsize=(12, 7))
plt.subplot(2, 1, 1)
plt.plot(df['timestamp_utc'], chi, label='χ Amplitude')
plt.title('χ Amplitude (Dec 2025, CME Cluster)')
plt.ylabel('χ')
plt.legend()

plt.subplot(2, 1, 2)
extent = [0, len(chi), scales[-1], scales[0]]
plt.imshow(np.abs(coeffs), extent=extent, cmap='viridis', aspect='auto')
plt.title('Continuous Wavelet Transform of χ')
plt.xlabel('Sample # (time)')
plt.ylabel('Wavelet Scale')
plt.tight_layout()
plt.show()

print('Wavelet scan complete! Peaks in the lower panel indicate dominant time-localized periodicities in χ.')
