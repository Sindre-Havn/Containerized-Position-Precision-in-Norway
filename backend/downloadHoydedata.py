import os
from shapely import LineString, box
import rasterio
from rasterio.merge import merge
import rasterio

from time import perf_counter_ns

# First, download the elevation data from hoydedata.no for the area you want to work with
# Place the downloaded folder inside your project at relative path "data/dom10/data/"

def create_new_raster(startpoint: float, endpoint: float) -> None:
    """
    Merges all available rasterfiles intersecting the direct line
    from "startpoint" to "endpoint".
    Bad solution, if "startpoint" and "endpoint" is describing a road
    segment which unfortunately turns around a raster, the taster to describe
    the "elbow" of the turn, might not get merged.
    """

    # startPoint = [450459.33,7370679.7]
    # endPoint = [514148.8, 7414287.3]

    line = LineString([startpoint, endpoint])
    buffer = line.buffer(distance=10000)

    # Find all .tif files in the folder
    folder_path = "data/dtm10/landsdekkende/"
    tif_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".tif")]

    covering_rasters = []

    for file in tif_files:
        raster = rasterio.open(file)
        bounds = raster.bounds
        raster_bbox = box(bounds.left, bounds.bottom, bounds.right, bounds.top)

        if raster_bbox.intersects(buffer):
            covering_rasters.append(raster)
        else:
            raster.close()

    if not covering_rasters:
        raise ValueError("No rasterfile covers the area you specified!")

    # Merge rasters
    mosaic, out_transform = merge(covering_rasters)

    # Copy data from first raster
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

    # Close rasters
    for raster in covering_rasters:
        raster.close()
    
    """
    For debugging:
    
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
    """


#createNewRaster([446098.28,7371410.12],	[475901.49, 7365141.92])