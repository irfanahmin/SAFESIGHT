import pandas as pd
import numpy as np
import folium
from sklearn.cluster import DBSCAN
from shapely.geometry import MultiPoint

# Load the dataset from CSV
df = pd.read_csv(r"C:\Users\Dell\OneDrive\Desktop\safesight models\crime_datas.csv")

# Ensure the latitude and longitude columns exist
if 'latitude' not in df.columns or 'longitude' not in df.columns:
    raise ValueError("CSV file must contain 'latitude' and 'longitude' columns.")

# Convert to Numpy array for clustering
coordinates = df[['latitude', 'longitude']].values

# DBSCAN Clustering (EPS = ~500m, Min Samples = 2)
kms_per_radian = 6371.0088
epsilon = 0.5 / kms_per_radian  # Convert meters to radians
db = DBSCAN(eps=epsilon, min_samples=2, metric='haversine').fit(np.radians(coordinates))

df['cluster'] = db.labels_

# Center the map explicitly on Bangalore city
bangalore_center = [12.9716, 77.5946]
m = folium.Map(location=bangalore_center, zoom_start=12)

# Add markers for each alert
for idx, row in df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color="red" if row["cluster"] == -1 else "blue",  # Red = Noise, Blue = Clustered
        fill=True,
        fill_color="red" if row["cluster"] == -1 else "blue",
        fill_opacity=0.7,
    ).add_to(m)

# Mark cluster centers
for cluster in set(db.labels_):
    if cluster == -1:
        continue  # Skip noise points
    cluster_points = df[df.cluster == cluster][["latitude", "longitude"]].values
    cluster_center = MultiPoint(cluster_points).centroid
    folium.Marker(
        location=[cluster_center.y, cluster_center.x],
        icon=folium.Icon(color="green", icon="info-sign"),
        popup=f"Hotspot {cluster}",
    ).add_to(m)

# Save and Show Map
m.save(r"C:\Users\Dell\OneDrive\Desktop\safesight models\hotspot_map.html")
print("Hotspot map saved! Open 'hotspot_map.html' to view.")
