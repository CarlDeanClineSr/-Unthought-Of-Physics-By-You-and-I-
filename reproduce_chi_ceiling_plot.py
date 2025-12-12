import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV and ensure correct time sequence
df = pd.read_csv("cme_heartbeat_log_2025_12.csv", parse_dates=["timestamp_utc"])
df = df.sort_values("timestamp_utc")

fig, ax = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

colors = df["storm_phase"].map({"pre": "green", "peak": "red", "post-storm": "blue"})
ax[0].scatter(df["timestamp_utc"], df["chi_amplitude"], c=colors, s=20)
ax[0].axhline(0.15, color="gold", linestyle="--", linewidth=2, label="χ = 0.15 ceiling")
ax[0].set_ylabel("χ Amplitude")
ax[0].legend()
ax[0].set_title("LUFT χ = 0.15 Ceiling Confirmation — Dec 2025")

ax[1].plot(df["timestamp_utc"], df["density_p_cm3"], color="blue", label="Density")
ax[1].plot(df["timestamp_utc"], df["speed_km_s"]/10, color="cyan", label="Speed / 10")
ax[1].set_ylabel("Density (cm⁻³) / Speed (km/s ÷ 10)")
ax[1].legend()

ax[2].plot(df["timestamp_utc"], df["bz_nT"], color="red", label="Bz")
ax[2].plot(df["timestamp_utc"], df["bt_nT"], color="purple", label="Bt")
ax[2].set_ylabel("B (nT)")
ax[2].legend()

ax[3].psd(df["chi_amplitude"], Fs=1/(60/60), label="χ PSD")  # rough daily sampling
ax[3].set_xlabel("Time (UTC)")
ax[3].legend()

plt.tight_layout()
plt.show()