import os

from shapely import LineString, box
import rasterio
from rasterio.merge import merge
import rasterio

# First, download the elevation data from hoydedata.no for the area you want to work with
# Place the downloaded folder inside your project

# Folder containing raster files (change to your path)
# folder_path = "data/dom10/data/"

# # Find all .tif files in the folder
# tif_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".tif")]

# # Open each raster and store in a list
# raster_list = []


# # Create one large raster by merging all the individual tiles
# raster_list = []
# for file in tif_files:
#     raster = rasterio.open(file)
#     raster_list.append(raster)

# mosaic, out_transform = merge(raster_list)

# # Copy metadata from the first raster file
# out_meta = raster_list[0].meta.copy()
# out_meta.update({
#     "driver": "GTiff",
#     "height": mosaic.shape[1],
#     "width": mosaic.shape[2],
#     "transform": out_transform
# })

# # Save the merged raster to a file (change the output path as needed)
# output_path = "data/merged_raster_romsdalen_10.tif"
# with rasterio.open(output_path, "w", **out_meta) as dest:
#     dest.write(mosaic)

# # Check information about the raster (change the name of the output raster as needed)
# with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
#     print(f"Raster nodata value: {src.nodata}")
    
#     # Read the first band and print min/max values
#     data = src.read(1)
#     print(f"Raster min/max values: {data.min()}, {data.max()}")

#     # Unpack the affine transform
#     a, b, c, d, e, f = src.transform.to_gdal()
#     print(f"Affine transform: {src.transform}")
    
#     # Upper-left corner
#     print(f"Raster upper-left corner: (a: {a}, b: {b}, c: {c}, d: {d}, e: {e}, f: {f})")

#     # Get raster index for a specific coordinate (Easting, Northing)
#     x, y = 124388.06, 6957735.68  # Coordinate to look up
#     row, col = src.index(x, y)
#     print(f"Raster index (row, col) for ({x}, {y}): ({row}, {col})")

#     # Get the elevation value at that point
#     elevation_value = data[row, col]
#     print(f"Elevation at ({x}, {y}): {elevation_value}")


#for større rastere
def createNewRaster(startPoint,endPoint):
    folder_path = "data/dtm10/landsdekkende/"

    # Find all .tif files in the folder
    tif_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".tif")]

    # startPoint = [450459.33,7370679.7]
    # endPoint = [514148.8, 7414287.3]

    line = LineString([startPoint, endPoint])
    buffer = line.buffer(10000)

    covering_rasters = []

    for file in tif_files:
        raster = rasterio.open(file)
        bounds = raster.bounds
        raster_bbox = box(bounds.left, bounds.bottom, bounds.right, bounds.top)

        if raster_bbox.intersects(buffer):
            covering_rasters.append(raster)
        else:
            raster.close()  # Viktig å lukke rastere du ikke trenger!

    if not covering_rasters:
        raise ValueError("Ingen rasterfiler dekker det området du spesifiserte!")

    # Slå sammen rastere
    mosaic, out_transform = merge(covering_rasters)

    # Kopier metadata fra første raster
    out_meta = covering_rasters[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform
    })

    output_path = "data/merged_raster.tif"
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic)

    # Husk å lukke rasterene når du er ferdig
    for raster in covering_rasters:
        raster.close()
        left = out_transform.c
    top = out_transform.f
    pixel_width = out_transform.a
    pixel_height = out_transform.e
    width_in_pixels = mosaic.shape[2]
    height_in_pixels = mosaic.shape[1]

    right = left + (pixel_width * width_in_pixels)
    bottom = top + (pixel_height * height_in_pixels)

    print(f"Lower left corner (bottom-left): ({left}, {bottom})")
    print(f"Upper right corner (top-right): ({right}, {top})")


#createNewRaster([446098.28,7371410.12],	[475901.49, 7365141.92])