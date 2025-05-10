import folium
import rasterio
from rasterio.plot import reshape_as_image
from rasterio.warp import transform_bounds
import numpy as np
import base64
from io import BytesIO
import matplotlib.pyplot as plt

# Load GeoTIFF
path = "georeferencing/stitched_georeferenced.tif"
with rasterio.open(path) as src:
    img = src.read([1, 2, 3])
    bounds = src.bounds
    crs = src.crs
    img = reshape_as_image(img)
    bounds_wgs84 = transform_bounds(crs, "EPSG:4326", *bounds)

# Prepare the RGB image
img = np.clip(img, 0, 255).astype(np.uint8)
buffer = BytesIO()
plt.imsave(buffer, img, format='png')
encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
img_url = f"data:image/png;base64,{encoded}"

# Center of the bounds
center_lat = (bounds_wgs84[1] + bounds_wgs84[3]) / 2
center_lon = (bounds_wgs84[0] + bounds_wgs84[2]) / 2

# Create folium map (no default tiles)
m = folium.Map(location=[center_lat, center_lon], zoom_start=17, tiles=None)

# Add a clean "no labels" tile layer (CartoDB Positron No Labels)
folium.TileLayer(
    tiles='https://cartodb-basemaps-a.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png',
    attr='CartoDB',
    name='CartoDB Positron (No Labels)',
    overlay=False,
    control=True
).add_to(m)

# Add overlay image
folium.raster_layers.ImageOverlay(
    image=img_url,
    bounds=[[bounds_wgs84[1], bounds_wgs84[0]], [bounds_wgs84[3], bounds_wgs84[2]]],
    opacity=0.7,
    interactive=True,
    cross_origin=False
).add_to(m)

folium.LayerControl().add_to(m)

# Save the map
m.save("visualization/overlay_clean_basemap.html")
print("✅ Map saved as: overlay_clean_basemap.html")