import os
import rasterio
from rasterio.merge import merge
import rasterio

# First, download the elevation data from hoydedata.no for the area you want to work with
# Place the downloaded folder inside your project

# Folder containing raster files (change to your path)
folder_path = "data/dom10/data/"

# Find all .tif files in the folder
tif_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".tif")]

# Open each raster and store in a list
raster_list = []
for file in tif_files:
    raster = rasterio.open(file)
    midpoint = raster.xy(raster.width // 2, raster.height // 2)
    raster_list.append(raster)

# Create one large raster by merging all the individual tiles
raster_list = []
for file in tif_files:
    raster = rasterio.open(file)
    raster_list.append(raster)

mosaic, out_transform = merge(raster_list)

# Copy metadata from the first raster file
out_meta = raster_list[0].meta.copy()
out_meta.update({
    "driver": "GTiff",
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": out_transform
})

# Save the merged raster to a file (change the output path as needed)
output_path = "data/merged_raster_romsdalen_10.tif"
with rasterio.open(output_path, "w", **out_meta) as dest:
    dest.write(mosaic)

# Check information about the raster (change the name of the output raster as needed)
with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
    print(f"Raster nodata value: {src.nodata}")
    
    # Read the first band and print min/max values
    data = src.read(1)
    print(f"Raster min/max values: {data.min()}, {data.max()}")

    # Unpack the affine transform
    a, b, c, d, e, f = src.transform.to_gdal()
    print(f"Affine transform: {src.transform}")
    
    # Upper-left corner
    print(f"Raster upper-left corner: (a: {a}, b: {b}, c: {c}, d: {d}, e: {e}, f: {f})")

    # Get raster index for a specific coordinate (Easting, Northing)
    x, y = 124388.06, 6957735.68  # Coordinate to look up
    row, col = src.index(x, y)
    print(f"Raster index (row, col) for ({x}, {y}): ({row}, {col})")

    # Get the elevation value at that point
    elevation_value = data[row, col]
    print(f"Elevation at ({x}, {y}): {elevation_value}")
