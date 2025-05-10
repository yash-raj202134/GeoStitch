import rasterio
from rasterio.transform import from_gcps
from rasterio.control import GroundControlPoint
from rasterio.enums import Resampling
import numpy as np
import cv2

# Load your stitched image
image_path = 'stitched_result.png'
img = cv2.imread(image_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

height, width = img.shape[:2]

# --- Step 1: Manually assign geocoordinates to corners ---
# These coordinates are just examples, you need to manually pick
# lat/lon values from Google Earth Pro for the corners of your stitched image


# gcps = [
#     GroundControlPoint(row=0, col=0, x=144.976547, y=-37.817264),              # Top-left
#     GroundControlPoint(row=0, col=width, x=144.992960, y=-37.818182),          # Top-right
#     GroundControlPoint(row=height, col=0, x=144.981998, y=-37.830138),         # Bottom-left
#     GroundControlPoint(row=height, col=width, x=144.987814, y=-37.829788),     # Bottom-right
# ]

# gcps = [
#     GroundControlPoint(row=0, col=0, x=144.976547, y=-37.817444),              # Top-left
#     GroundControlPoint(row=0, col=width, x=144.992960, y=-37.818362),          # Top-right
#     GroundControlPoint(row=height, col=0, x=144.981998, y=-37.830318),         # Bottom-left
#     GroundControlPoint(row=height, col=width, x=144.987814, y=-37.829968),     # Bottom-right
# ]


# gcps = [
#     GroundControlPoint(row=0, col=0, x=144.976247, y=-37.818144),              # Top-left (more southwest)
#     GroundControlPoint(row=0, col=width, x=144.992660, y=-37.819062),          # Top-right (south shift only)
#     GroundControlPoint(row=height, col=0, x=144.981698, y=-37.831018),         # Bottom-left (more southwest)
#     GroundControlPoint(row=height, col=width, x=144.987514, y=-37.830668),     # Bottom-right (south shift only)
# ]

gcps = [
    GroundControlPoint(row=0, col=0, x=144.976047, y=-37.818144),              # Top-left
    GroundControlPoint(row=0, col=width, x=144.993160, y=-37.819762),          # Top-right (lower to rotate counter-clockwise)
    GroundControlPoint(row=height, col=0, x=144.980998, y=-37.829618),         # Bottom-left (higher to rotate counter-clockwise)
    GroundControlPoint(row=height, col=width, x=144.987814, y=-37.831668),     # Bottom-right
]


# --- Step 2: Build GeoTIFF with transform from GCPs ---
transform = from_gcps(gcps)

output_path = "georeferencing/stitched_georeferenced.tif"
with rasterio.open(
    output_path,
    'w',
    driver='GTiff',
    height=img.shape[0],
    width=img.shape[1],
    count=3,
    dtype=img.dtype,
    crs='EPSG:4326',  # WGS84
    transform=transform
) as dst:
    for i in range(3):  # RGB channels
        dst.write(img[:, :, i], i + 1)

print(f"✅ GeoTIFF saved as: {output_path}")


# --- Step 3: Resample to a lower resolution (optional) ---
with rasterio.open(output_path) as src:
    data = src.read(
        out_shape=(src.count, int(src.height * 0.5), int(src.width * 0.5)),
        resampling=Resampling.bilinear
    )
    transform = src.transform * src.transform.scale(
        (src.width / data.shape[-1]),
        (src.height / data.shape[-2])
    )
    metadata = src.meta.copy()
    metadata.update({
        'transform': transform,
        'height': data.shape[1],
        'width': data.shape[2]
    })
    output_resampled_path = "georeferencing/stitched_georeferenced_resampled.tif"
    with rasterio.open(output_resampled_path, 'w', **metadata) as dst:
        dst.write(data)
    print(f"✅ Resampled GeoTIFF saved as: {output_resampled_path}")
