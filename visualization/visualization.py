import folium
import rasterio
from rasterio.plot import reshape_as_image
from folium.raster_layers import ImageOverlay
from rasterio.warp import transform_bounds

# Path to your GeoTIFF
geo_tiff_path = "georeferencing/stitched_georeferenced_resampled.tif"

# Load the image and get bounds
with rasterio.open(geo_tiff_path) as src:
    bounds = transform_bounds(src.crs, "EPSG:4326", *src.bounds)  # (west, south, east, north)
    img = src.read([1, 2, 3])  # Read RGB
    img = reshape_as_image(img)  # Shape: (height, width, channels)

# Create a Folium map centered on the image
m = folium.Map(location=[(bounds[1]+bounds[3])/2, (bounds[0]+bounds[2])/2], zoom_start=16)

# Add image overlay
ImageOverlay(
    image=img,
    bounds=[[bounds[1], bounds[0]], [bounds[3], bounds[2]]],  # [[south, west], [north, east]]
    opacity=0.7,
    interactive=True,
    cross_origin=False
).add_to(m)

folium.LayerControl().add_to(m)

# Save to HTML
m.save("visualization/georeferenced_map.html")
print("✅ Map saved as: georeferenced_map.html")
