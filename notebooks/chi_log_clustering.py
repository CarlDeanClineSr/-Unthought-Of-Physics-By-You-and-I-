import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np

# Load CME χ log
file = 'cme_heartbeat_log_2025_12.csv'
df = pd.read_csv(file, parse_dates=['timestamp_utc'])
df = df.dropna(subset=['chi_amplitude', 'density_p_cm3', 'speed_km_s', 'bz_nT'])

# Features for clustering (normalize or scale as needed)
features = df[['chi_amplitude', 'density_p_cm3', 'speed_km_s', 'bz_nT']].copy()
features = (features - features.mean()) / features.std()

# Dimensionality reduction for visualization
pca = PCA(n_components=2)
coords = pca.fit_transform(features)

# Clustering (choose K automatically or set manually for discovery)
k = 3  # try 2–5 clusters for best separation
kmeans = KMeans(n_clusters=k, random_state=42).fit(features)
df['cluster'] = kmeans.labels_

# Plot cluster result
plt.figure(figsize=(9,6))
for c in range(k):
    plt.scatter(coords[df['cluster']==c,0], coords[df['cluster']==c,1], 
                label=f'Cluster {c}', alpha=0.65)
plt.xlabel('PCA 1'); plt.ylabel('PCA 2')
plt.title('Clustering of CME χ Log (Dec 2025)')
plt.legend()
plt.tight_layout()
plt.show()

# Save cluster assignments for future event annotation
df.to_csv('cme_heartbeat_log_2025_12_clustered.csv', index=False)
print('Clustered log saved as cme_heartbeat_log_2025_12_clustered.csv')
